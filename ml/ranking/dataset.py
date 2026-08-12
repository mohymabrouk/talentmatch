from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from ml.features.schema import FEATURE_SCHEMA, FeatureVector


@dataclass(frozen=True)
class RankingRow:
    request_id: str
    user_id: str
    job_id: str
    served_at: datetime
    label: int
    features: FeatureVector

    @classmethod
    def from_record(cls, record: dict[str, object]) -> "RankingRow":
        schema_version = str(record["schema_version"])
        if schema_version != FEATURE_SCHEMA.version:
            raise ValueError(f"unsupported feature schema: {schema_version}")
        values = record["features"]
        if not isinstance(values, dict):
            raise ValueError("training record features must be an object")
        vector = FEATURE_SCHEMA.vector({name: float(values[name]) for name in FEATURE_SCHEMA.names})
        label = int(record["label"])
        if label < 0:
            raise ValueError("training labels must be non-negative")
        served_at = datetime.fromisoformat(str(record["served_at"]))
        if served_at.tzinfo is None:
            raise ValueError("served_at must include a timezone")
        return cls(
            request_id=str(record["request_id"]),
            user_id=str(record["user_id"]),
            job_id=str(record["job_id"]),
            served_at=served_at,
            label=label,
            features=vector,
        )


@dataclass(frozen=True)
class DatasetSplit:
    train: tuple[RankingRow, ...]
    validation: tuple[RankingRow, ...]
    test: tuple[RankingRow, ...]

    @property
    def evaluation(self) -> tuple[RankingRow, ...]:
        return self.test or self.validation or self.train


def load_rows(path: Path) -> list[RankingRow]:
    rows = [
        RankingRow.from_record(json.loads(line))
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError(f"no training rows found in {path}")
    return sorted(rows, key=lambda row: (row.served_at, row.request_id, row.job_id))


def chronological_split(
    rows: list[RankingRow], train_ratio: float = 0.70, validation_ratio: float = 0.15
) -> DatasetSplit:
    if not rows:
        raise ValueError("cannot split an empty dataset")
    grouped: dict[str, list[RankingRow]] = {}
    for row in sorted(rows, key=lambda item: (item.served_at, item.request_id, item.job_id)):
        grouped.setdefault(row.request_id, []).append(row)
    ordered_groups = sorted(grouped.values(), key=lambda group: (group[0].served_at, group[0].request_id))
    group_count = len(ordered_groups)
    train_groups = max(1, min(group_count, int(group_count * train_ratio)))
    validation_groups = int(group_count * validation_ratio)
    if group_count >= 3:
        validation_groups = max(1, validation_groups)
        if train_groups + validation_groups >= group_count:
            train_groups = max(1, group_count - validation_groups - 1)
    validation_end = min(group_count, train_groups + validation_groups)
    return DatasetSplit(
        train=tuple(row for group in ordered_groups[:train_groups] for row in group),
        validation=tuple(row for group in ordered_groups[train_groups:validation_end] for row in group),
        test=tuple(row for group in ordered_groups[validation_end:] for row in group),
    )


def matrix(rows: tuple[RankingRow, ...] | list[RankingRow]):
    import numpy as np

    return np.asarray([row.features.values for row in rows], dtype=np.float32)


def labels(rows: tuple[RankingRow, ...] | list[RankingRow]):
    import numpy as np

    return np.asarray([row.label for row in rows], dtype=np.float32)


def groups(rows: tuple[RankingRow, ...] | list[RankingRow]) -> list[int]:
    counts: list[int] = []
    current: str | None = None
    for row in rows:
        if row.request_id != current:
            counts.append(0)
            current = row.request_id
        counts[-1] += 1
    return counts
