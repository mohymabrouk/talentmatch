from collections.abc import Iterable, Sequence
from math import log2


def recall_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int) -> float:
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    return len(set(recommended[:k]) & relevant_set) / len(relevant_set)


def ndcg_at_k(recommended: Sequence[str], relevant: Iterable[str], k: int) -> float:
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    gains = [1.0 if item in relevant_set else 0.0 for item in recommended[:k]]
    dcg = sum(gain / log2(position + 2) for position, gain in enumerate(gains))
    ideal_length = min(k, len(relevant_set))
    ideal = sum(1.0 / log2(position + 2) for position in range(ideal_length))
    return dcg / ideal if ideal else 0.0


def mrr(recommended: Sequence[str], relevant: Iterable[str]) -> float:
    relevant_set = set(relevant)
    for position, item in enumerate(recommended, start=1):
        if item in relevant_set:
            return 1.0 / position
    return 0.0

