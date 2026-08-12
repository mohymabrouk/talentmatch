from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ml.features.schema import FEATURE_SCHEMA
from ml.ranking.dataset import DatasetSplit, RankingRow, groups, labels, matrix, chronological_split
from ml.ranking.metrics import baseline_scores, evaluate


def _group_count(rows: tuple[RankingRow, ...]) -> int:
    return len({row.request_id for row in rows})


def _baseline_report(rows: tuple[RankingRow, ...]) -> dict[str, dict[str, float]]:
    scores_by_name = {
        "retrieval": baseline_scores(rows, "retrieval_score"),
        "skill_overlap": baseline_scores(rows, "skill_overlap_ratio"),
        "popularity": baseline_scores(rows, "job_popularity_30d"),
        "newest": [-score for score in baseline_scores(rows, "job_age_days")],
    }
    return {name: evaluate(rows, scores, k=20) for name, scores in scores_by_name.items()}


def train_ranker(
    rows: list[RankingRow],
    output_dir: Path,
    version: str = "ranker-v001",
    seed: int = 42,
    num_boost_round: int = 80,
) -> dict[str, Any]:
    split = chronological_split(rows)
    if not split.train:
        raise ValueError("chronological split produced no training rows")
    if len({row.label for row in split.train}) < 2:
        raise ValueError("training split must contain both positive and negative labels")
    import lightgbm as lgb

    params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_at": [5, 10, 20],
        "learning_rate": 0.05,
        "num_leaves": 7,
        "min_data_in_leaf": 1,
        "feature_fraction": 1.0,
        "bagging_fraction": 1.0,
        "verbosity": -1,
        "seed": seed,
        "feature_fraction_seed": seed,
        "bagging_seed": seed,
        "data_random_seed": seed,
    }
    train_data = lgb.Dataset(
        matrix(split.train),
        label=labels(split.train),
        group=groups(split.train),
        feature_name=list(FEATURE_SCHEMA.names),
        free_raw_data=False,
    )
    valid_sets = []
    valid_names = []
    if split.validation and len({row.label for row in split.validation}) >= 1:
        valid_sets.append(
            lgb.Dataset(
                matrix(split.validation),
                label=labels(split.validation),
                group=groups(split.validation),
                feature_name=list(FEATURE_SCHEMA.names),
                reference=train_data,
                free_raw_data=False,
            )
        )
        valid_names.append("validation")
    callbacks = [lgb.log_evaluation(period=0)]
    if valid_sets:
        callbacks.append(lgb.early_stopping(stopping_rounds=12, verbose=False))
    booster = lgb.train(
        params,
        train_data,
        num_boost_round=num_boost_round,
        valid_sets=valid_sets,
        valid_names=valid_names,
        callbacks=callbacks,
    )
    evaluation_rows = split.evaluation
    predictions = booster.predict(matrix(evaluation_rows))
    ranker_metrics = evaluate(evaluation_rows, predictions, k=20)
    baselines = _baseline_report(evaluation_rows)
    selected_baseline = "retrieval"
    metrics = {
        "model_version": version,
        "feature_schema_version": FEATURE_SCHEMA.version,
        "evaluation_split": "test" if split.test else "validation" if split.validation else "train",
        "rows": {"total": len(rows), "train": len(split.train), "validation": len(split.validation), "test": len(split.test)},
        "groups": {"total": len({row.request_id for row in rows}), "train": _group_count(split.train), "validation": _group_count(split.validation), "test": _group_count(split.test)},
        "selected_baseline": selected_baseline,
        "ranker": ranker_metrics,
        "baselines": baselines,
        "beats_selected_baseline": ranker_metrics["ndcg@20"] > baselines[selected_baseline]["ndcg@20"],
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    booster.save_model(str(output_dir / "model.txt"))
    (output_dir / "feature_schema.json").write_text(FEATURE_SCHEMA.as_json(), encoding="utf-8")
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (output_dir / "training_config.json").write_text(
        json.dumps({"version": version, "seed": seed, "num_boost_round": num_boost_round, "params": params}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "metadata.json").write_text(
        json.dumps(
            {
                "version": version,
                "model_type": "lightgbm-lambdarank",
                "schema_version": FEATURE_SCHEMA.version,
                "created_at": datetime.now(UTC).isoformat(),
                "artifact_format": "lightgbm-booster-text",
                "feature_names": list(FEATURE_SCHEMA.names),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return metrics
