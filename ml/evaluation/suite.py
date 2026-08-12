from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import ceil, log2
from time import perf_counter
from typing import Callable, Mapping

from ml.features.schema import FeatureVector
from ml.ranking.dataset import RankingRow


@dataclass(frozen=True)
class JobMetadata:
    title: str
    company_name: str


def ranked_list_metrics(
    recommended: list[str], relevant: set[str], ks: tuple[int, ...] = (5, 10, 20)
) -> dict[str, float]:
    labels = [int(item in relevant) for item in recommended]
    scores = [float(len(recommended) - index) for index in range(len(recommended))]
    return {
        **{f"recall@{k}": _recall(labels, scores, k) for k in ks},
        **{f"ndcg@{k}": _ndcg(labels, scores, k) for k in ks},
        "mrr": _mrr(labels, scores),
    }


def _group_rows(rows: list[RankingRow] | tuple[RankingRow, ...], scores: list[float]) -> list[list[tuple[RankingRow, float]]]:
    grouped: dict[str, list[tuple[RankingRow, float]]] = defaultdict(list)
    for row, score in zip(rows, scores, strict=True):
        grouped[row.request_id].append((row, float(score)))
    return list(grouped.values())


def _ndcg(labels: list[int], scores: list[float], k: int) -> float:
    order = sorted(range(len(labels)), key=lambda index: scores[index], reverse=True)[:k]
    dcg = sum((2**labels[index] - 1) / log2(position + 2) for position, index in enumerate(order))
    ideal = sorted(labels, reverse=True)[:k]
    ideal_dcg = sum((2**label - 1) / log2(position + 2) for position, label in enumerate(ideal))
    return dcg / ideal_dcg if ideal_dcg else 0.0


def _recall(labels: list[int], scores: list[float], k: int) -> float:
    positive_count = sum(label > 0 for label in labels)
    if not positive_count:
        return 0.0
    order = sorted(range(len(labels)), key=lambda index: scores[index], reverse=True)[:k]
    return sum(labels[index] > 0 for index in order) / positive_count


def _mrr(labels: list[int], scores: list[float]) -> float:
    order = sorted(range(len(labels)), key=lambda index: scores[index], reverse=True)
    for position, index in enumerate(order, start=1):
        if labels[index] > 0:
            return 1.0 / position
    return 0.0


def ranking_metrics(
    rows: list[RankingRow] | tuple[RankingRow, ...],
    scores: list[float],
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, float]:
    groups = _group_rows(rows, scores)
    if not groups:
        return {metric: 0.0 for k in ks for metric in (f"recall@{k}", f"ndcg@{k}")} | {"mrr": 0.0}
    result: dict[str, float] = {}
    for k in ks:
        result[f"recall@{k}"] = sum(
            _recall([row.label for row, _ in group], [score for _, score in group], k) for group in groups
        ) / len(groups)
        result[f"ndcg@{k}"] = sum(
            _ndcg([row.label for row, _ in group], [score for _, score in group], k) for group in groups
        ) / len(groups)
    result["mrr"] = sum(
        _mrr([row.label for row, _ in group], [score for _, score in group]) for group in groups
    ) / len(groups)
    return result


def _top_groups(
    rows: list[RankingRow] | tuple[RankingRow, ...], scores: list[float], k: int
) -> list[list[RankingRow]]:
    return [
        [row for row, _ in sorted(group, key=lambda item: item[1], reverse=True)[:k]]
        for group in _group_rows(rows, scores)
    ]


def coverage_metrics(
    rows: list[RankingRow] | tuple[RankingRow, ...], scores: list[float], ks: tuple[int, ...] = (5, 10, 20)
) -> dict[str, float]:
    candidate_jobs = {row.job_id for row in rows}
    result = {"candidate_jobs": float(len(candidate_jobs))}
    for k in ks:
        recommended_jobs = {row.job_id for group in _top_groups(rows, scores, k) for row in group}
        result[f"unique_jobs@{k}"] = float(len(recommended_jobs))
        result[f"catalog_coverage@{k}"] = len(recommended_jobs) / len(candidate_jobs) if candidate_jobs else 0.0
    return result


def diversity_metrics(
    rows: list[RankingRow] | tuple[RankingRow, ...],
    scores: list[float],
    metadata: Mapping[str, JobMetadata],
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, float]:
    result: dict[str, float] = {}
    for k in ks:
        groups = _top_groups(rows, scores, k)
        if not groups:
            result[f"mean_unique_companies@{k}"] = 0.0
            result[f"mean_unique_titles@{k}"] = 0.0
            result[f"mean_company_diversity@{k}"] = 0.0
            continue
        company_counts = []
        title_counts = []
        diversity_values = []
        for group in groups:
            companies = {metadata.get(row.job_id, JobMetadata(row.job_id, row.job_id)).company_name for row in group}
            titles = {metadata.get(row.job_id, JobMetadata(row.job_id, row.job_id)).title.casefold() for row in group}
            company_counts.append(len(companies))
            title_counts.append(len(titles))
            diversity_values.append(len(companies) / len(group) if group else 0.0)
        result[f"mean_unique_companies@{k}"] = sum(company_counts) / len(company_counts)
        result[f"mean_unique_titles@{k}"] = sum(title_counts) / len(title_counts)
        result[f"mean_company_diversity@{k}"] = sum(diversity_values) / len(diversity_values)
    return result


def segment_metrics(
    rows: list[RankingRow] | tuple[RankingRow, ...], scores: list[float], ks: tuple[int, ...] = (5, 10, 20)
) -> dict[str, dict[str, float]]:
    feature_index = {name: index for index, name in enumerate(rows[0].features.names)} if rows else {}

    def feature(row: RankingRow, name: str) -> float:
        return row.features.values[feature_index[name]]

    segments: dict[str, list[int]] = {
        "all": list(range(len(rows))),
        "cold_start": [index for index, row in enumerate(rows) if feature(row, "user_interaction_count_30d") == 0],
        "engaged": [index for index, row in enumerate(rows) if feature(row, "user_interaction_count_30d") > 0],
        "remote_compatible": [index for index, row in enumerate(rows) if feature(row, "remote_compatible") >= 0.5],
        "remote_incompatible": [index for index, row in enumerate(rows) if feature(row, "remote_compatible") < 0.5],
    }
    result: dict[str, dict[str, float]] = {}
    for name, indices in segments.items():
        segment_rows = [rows[index] for index in indices]
        segment_scores = [scores[index] for index in indices]
        result[name] = {"rows": float(len(segment_rows)), "groups": float(len({row.request_id for row in segment_rows}))}
        if not segment_rows:
            result[name].update(ranking_metrics(segment_rows, segment_scores, ks))
            continue
        result[name].update(ranking_metrics(segment_rows, segment_scores, ks))
    return result


def evaluate_ranker(
    rows: list[RankingRow],
    predictor: Callable[[FeatureVector], float],
    model_version: str,
    metadata: Mapping[str, JobMetadata] | None = None,
    ks: tuple[int, ...] = (5, 10, 20),
) -> dict[str, object]:
    if not rows:
        raise ValueError("cannot evaluate an empty ranking dataset")
    started = perf_counter()
    scores = [float(predictor(row.features)) for row in rows]
    elapsed_ms = (perf_counter() - started) * 1000
    latency_values = sorted([elapsed_ms / len(rows)] * len(rows))
    p95_index = min(len(latency_values) - 1, max(0, ceil(len(latency_values) * 0.95) - 1))
    report: dict[str, object] = {
        "model_version": model_version,
        "dataset": {
            "rows": len(rows),
            "groups": len({row.request_id for row in rows}),
            "candidate_jobs": len({row.job_id for row in rows}),
        },
        "ranking": ranking_metrics(rows, scores, ks),
        "coverage": coverage_metrics(rows, scores, ks),
        "latency": {
            "prediction_total_ms": round(elapsed_ms, 6),
            "prediction_per_row_ms": round(elapsed_ms / len(rows), 6),
            "prediction_p50_ms": round(latency_values[min(len(latency_values) - 1, len(latency_values) // 2)], 6),
            "prediction_p95_ms": round(latency_values[p95_index], 6),
            "prediction_p99_ms": round(latency_values[-1], 6),
        },
        "segments": segment_metrics(rows, scores, ks),
    }
    report["diversity"] = diversity_metrics(rows, scores, metadata or {}, ks)
    return report
