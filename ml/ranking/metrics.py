from __future__ import annotations

from collections import defaultdict
from math import log2

from ml.ranking.dataset import RankingRow


def _group_rows(rows: list[RankingRow] | tuple[RankingRow, ...], scores) -> list[tuple[list[int], list[float]]]:
    grouped: dict[str, list[tuple[int, float]]] = defaultdict(list)
    for row, score in zip(rows, scores, strict=True):
        grouped[row.request_id].append((row.label, float(score)))
    return [
        ([label for label, _ in values], [score for _, score in values])
        for _, values in sorted(grouped.items())
    ]


def ndcg(labels: list[int], scores: list[float], k: int = 20) -> float:
    order = sorted(range(len(labels)), key=lambda index: scores[index], reverse=True)[:k]
    dcg = sum((2**labels[index] - 1) / log2(position + 2) for position, index in enumerate(order))
    ideal = sorted(labels, reverse=True)[:k]
    ideal_dcg = sum((2**label - 1) / log2(position + 2) for position, label in enumerate(ideal))
    return dcg / ideal_dcg if ideal_dcg else 0.0


def mrr(labels: list[int], scores: list[float]) -> float:
    for position, index in enumerate(sorted(range(len(labels)), key=lambda item: scores[item], reverse=True), start=1):
        if labels[index] > 0:
            return 1.0 / position
    return 0.0


def evaluate(rows: list[RankingRow] | tuple[RankingRow, ...], scores, k: int = 20) -> dict[str, float]:
    grouped = _group_rows(rows, scores)
    if not grouped:
        return {"ndcg@20": 0.0, "mrr": 0.0}
    return {
        "ndcg@20": sum(ndcg(labels, values, k) for labels, values in grouped) / len(grouped),
        "mrr": sum(mrr(labels, values) for labels, values in grouped) / len(grouped),
    }


def baseline_scores(rows: list[RankingRow] | tuple[RankingRow, ...], feature_name: str) -> list[float]:
    try:
        index = rows[0].features.names.index(feature_name)
    except (IndexError, ValueError) as exc:
        raise ValueError(f"unknown baseline feature: {feature_name}") from exc
    return [row.features.values[index] for row in rows]
