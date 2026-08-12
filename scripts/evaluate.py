#!/usr/bin/env python3
"""Run the complete offline retrieval and ranking evaluation suite."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from time import perf_counter
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from app.core.config import Settings  # noqa: E402
from app.db.session import build_session_factory  # noqa: E402
from app.models import Job  # noqa: E402
from ml.evaluation.suite import JobMetadata, evaluate_ranker, ranking_metrics  # noqa: E402
from ml.features.dataset import FeatureDatasetBuilder  # noqa: E402
from ml.ranking.dataset import chronological_split, load_rows  # noqa: E402
from ml.ranking.model import RankerModel  # noqa: E402
from ml.ranking.trainer import _baseline_report  # noqa: E402
from ml.retrieval.embeddings import build_embedder  # noqa: E402
from ml.retrieval.index import VectorIndex  # noqa: E402
from ml.retrieval.text import candidate_text  # noqa: E402


KS = (5, 10, 20)


def percentile(values: list[float], percentage: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * percentage)))
    return ordered[index]


def evaluate_retrieval(
    records: list[dict[str, Any]],
    jobs: list[Job],
    index: VectorIndex,
    embedding_model: str,
) -> dict[str, object]:
    jobs_by_external = {job.external_id: job for job in jobs if job.external_id}
    metadata = {
        job.id: JobMetadata(title=job.title, company_name=job.company_name)
        for job in jobs
    }
    embedder = build_embedder(embedding_model)
    metric_values: dict[str, list[float]] = defaultdict(list)
    latency_values: list[float] = []
    recommendations_by_k: dict[int, set[str]] = {k: set() for k in KS}
    companies_by_k: dict[int, list[int]] = {k: [] for k in KS}
    titles_by_k: dict[int, list[int]] = {k: [] for k in KS}
    segment_values: dict[str, list[dict[str, float]]] = defaultdict(list)

    for record in records:
        relevant = [jobs_by_external[item].id for item in record["relevant_external_ids"] if item in jobs_by_external]
        if not relevant:
            continue
        started = perf_counter()
        vector = embedder.encode(
            [
                candidate_text(
                    record["target_roles"],
                    record["skills"],
                    record["years_experience"],
                    record["location"],
                    record["remote_preference"],
                )
            ]
        )[0]
        results = index.search(vector, min(200, len(jobs)))
        latency_values.append((perf_counter() - started) * 1000)
        recommended = [item.item_id for item in results]
        case_metrics = ranking_metrics(
            [
                type("EvaluationRow", (), {"request_id": "case", "job_id": job_id, "label": int(job_id in relevant), "features": type("Features", (), {"names": (), "values": ()})()})()
                for job_id in recommended
            ],
            [float(len(recommended) - index) for index in range(len(recommended))],
            KS,
        )
        for name, value in case_metrics.items():
            metric_values[name].append(value)
        segment = f"remote_preference:{record.get('remote_preference') or 'unknown'}"
        segment_values[segment].append(case_metrics)
        for k in KS:
            top_jobs = recommended[:k]
            recommendations_by_k[k].update(top_jobs)
            companies_by_k[k].append(len({metadata[job_id].company_name for job_id in top_jobs if job_id in metadata}))
            titles_by_k[k].append(len({metadata[job_id].title.casefold() for job_id in top_jobs if job_id in metadata}))

    case_count = len(latency_values)
    total_jobs = len(jobs)
    result: dict[str, object] = {
        "cases": case_count,
        "ranking": {name: round(sum(values) / len(values), 6) for name, values in metric_values.items()},
        "coverage": {
            f"catalog_coverage@{k}": round(len(recommendations_by_k[k]) / total_jobs, 6) if total_jobs else 0.0
            for k in KS
        },
        "diversity": {
            f"mean_unique_companies@{k}": round(sum(companies_by_k[k]) / len(companies_by_k[k]), 6) if companies_by_k[k] else 0.0,
            f"mean_unique_titles@{k}": round(sum(titles_by_k[k]) / len(titles_by_k[k]), 6) if titles_by_k[k] else 0.0,
        },
        "latency": {
            "p50_ms": round(percentile(latency_values, 0.50), 6),
            "p95_ms": round(percentile(latency_values, 0.95), 6),
            "p99_ms": round(percentile(latency_values, 0.99), 6),
        },
        "segments": {
            name: {
                metric: round(sum(item[metric] for item in values) / len(values), 6)
                for metric in values[0]
            }
            for name, values in segment_values.items()
            if values
        },
    }
    return result


def evaluate_ranking(rows, ranker_dir: Path, metadata: dict[str, JobMetadata]) -> dict[str, object]:
    split = chronological_split(rows)
    evaluation_rows = list(split.evaluation)
    model = RankerModel(ranker_dir)
    report = evaluate_ranker(evaluation_rows, model.predict, model.version, metadata)
    baselines = _baseline_report(tuple(evaluation_rows))
    report["baselines"] = baselines
    report["selected_baseline"] = "retrieval"
    report["beats_selected_baseline"] = report["ranking"]["ndcg@20"] > baselines["retrieval"]["ndcg@20"]
    report["split"] = {
        "train_rows": len(split.train),
        "validation_rows": len(split.validation),
        "test_rows": len(split.test),
        "evaluation": "test" if split.test else "validation" if split.validation else "train",
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run complete offline retrieval and ranking evaluation.")
    parser.add_argument("--retrieval-input", type=Path, default=Path("data/evaluation.jsonl"))
    parser.add_argument("--ranking-input", type=Path, default=Path("ml/artifacts/features/v001/training.jsonl"))
    parser.add_argument("--ranker", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=Path("ml/artifacts/evaluation/v001/report.json"))
    args = parser.parse_args()

    settings = Settings()
    retrieval_artifact_dir = Path(settings.retrieval_artifact_dir)
    _, factory = build_session_factory(settings)
    db = factory()
    try:
        jobs = db.scalars(select(Job).where(Job.is_active.is_(True))).all()
        if not jobs:
            raise RuntimeError("no active jobs found; seed jobs before evaluation")
        if not (retrieval_artifact_dir / "metadata.json").exists():
            from ml.retrieval.index import build_job_index

            build_job_index(db, settings, retrieval_artifact_dir)
        index = VectorIndex.load(retrieval_artifact_dir)
        records = [json.loads(line) for line in args.retrieval_input.read_text(encoding="utf-8").splitlines() if line.strip()]
        report: dict[str, object] = {
            "evaluation_version": "evaluation-v001",
            "retrieval": evaluate_retrieval(records, jobs, index, settings.embedding_model),
        }

        if args.ranking_input.exists():
            rows = load_rows(args.ranking_input)
        else:
            rows = FeatureDatasetBuilder(db).build()
        ranker_dir = args.ranker or Path(settings.ranker_artifact_dir)
        metadata = {job.id: JobMetadata(title=job.title, company_name=job.company_name) for job in jobs}
        if rows and ranker_dir.exists():
            report["ranking"] = evaluate_ranking(rows, ranker_dir, metadata)
        else:
            report["ranking"] = {"status": "unavailable", "reason": "training rows or ranker artifact missing"}

        report["database"] = {"active_jobs": len(jobs), "ranking_rows": len(rows)}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()
