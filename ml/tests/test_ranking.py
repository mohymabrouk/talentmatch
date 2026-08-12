from datetime import UTC, datetime, timedelta

from ml.features.schema import FEATURE_SCHEMA
from ml.ranking.dataset import RankingRow, chronological_split
from ml.ranking.model import RankerModel
from ml.ranking.trainer import train_ranker


def make_rows(group_count: int = 18) -> list[RankingRow]:
    rows: list[RankingRow] = []
    start = datetime(2026, 1, 1, tzinfo=UTC)
    for request_number in range(group_count):
        for candidate_number, label in enumerate((1, 0, 0)):
            values = {name: 0.0 for name in FEATURE_SCHEMA.names}
            values.update(
                {
                    "retrieval_score": 0.1 if candidate_number == 0 else 0.9 - candidate_number * 0.1,
                    "skill_overlap_ratio": 1.0 if candidate_number == 0 else 0.0,
                    "required_skill_match_ratio": 1.0 if candidate_number == 0 else 0.0,
                    "job_popularity_30d": 0.2 + candidate_number * 0.1,
                    "job_age_days": float(candidate_number + 1),
                }
            )
            rows.append(
                RankingRow(
                    request_id=f"request-{request_number:03d}",
                    user_id="user-001",
                    job_id=f"job-{request_number:03d}-{candidate_number}",
                    served_at=start + timedelta(days=request_number),
                    label=label,
                    features=FEATURE_SCHEMA.vector(values),
                )
            )
    return rows


def test_chronological_split_keeps_request_groups_intact() -> None:
    split = chronological_split(make_rows(10))
    train_requests = {row.request_id for row in split.train}
    validation_requests = {row.request_id for row in split.validation}
    test_requests = {row.request_id for row in split.test}

    assert train_requests.isdisjoint(validation_requests | test_requests)
    assert validation_requests.isdisjoint(test_requests)
    assert max(row.served_at for row in split.train) < min(row.served_at for row in split.validation)
    assert max(row.served_at for row in split.validation) < min(row.served_at for row in split.test)
    assert {row.request_id for row in split.train} == {f"request-{index:03d}" for index in range(7)}


def test_train_ranker_writes_versioned_artifacts_and_beats_retrieval(tmp_path) -> None:
    output_dir = tmp_path / "ranker" / "v001"
    metrics = train_ranker(make_rows(), output_dir, num_boost_round=40)

    assert metrics["feature_schema_version"] == FEATURE_SCHEMA.version
    assert metrics["beats_selected_baseline"] is True
    assert metrics["ranker"]["ndcg@20"] > metrics["baselines"]["retrieval"]["ndcg@20"]
    assert (output_dir / "model.txt").is_file()
    assert (output_dir / "feature_schema.json").is_file()
    assert (output_dir / "metrics.json").is_file()
    assert (output_dir / "training_config.json").is_file()
    assert (output_dir / "metadata.json").is_file()

    model = RankerModel(output_dir)
    assert model.version == "ranker-v001"
    assert isinstance(model.predict(make_rows(1)[0].features), float)
