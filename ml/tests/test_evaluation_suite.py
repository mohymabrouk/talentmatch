from datetime import UTC, datetime, timedelta

from ml.evaluation.suite import JobMetadata, evaluate_ranker
from ml.features.schema import FEATURE_SCHEMA
from ml.ranking.dataset import RankingRow


def make_rows() -> list[RankingRow]:
    rows: list[RankingRow] = []
    start = datetime(2026, 1, 1, tzinfo=UTC)
    for request_number in range(4):
        for candidate_number, label in enumerate((1, 0, 0)):
            values = {name: 0.0 for name in FEATURE_SCHEMA.names}
            values["skill_overlap_ratio"] = float(candidate_number == 0)
            values["user_interaction_count_30d"] = float(request_number > 1)
            values["remote_compatible"] = float(candidate_number != 1)
            rows.append(
                RankingRow(
                    request_id=f"request-{request_number}",
                    user_id="user-001",
                    job_id=f"job-{request_number}-{candidate_number}",
                    served_at=start + timedelta(days=request_number),
                    label=label,
                    features=FEATURE_SCHEMA.vector(values),
                )
            )
    return rows


def test_evaluation_suite_reports_quality_coverage_diversity_latency_and_segments() -> None:
    rows = make_rows()
    metadata = {
        row.job_id: JobMetadata(title=f"Role {row.job_id[-1]}", company_name=f"Company {row.job_id[-1]}")
        for row in rows
    }
    report = evaluate_ranker(
        rows,
        predictor=lambda vector: vector.values[FEATURE_SCHEMA.names.index("skill_overlap_ratio")],
        model_version="test-model",
        metadata=metadata,
    )

    ranking = report["ranking"]
    assert ranking["recall@5"] == 1.0
    assert ranking["ndcg@5"] == 1.0
    assert ranking["mrr"] == 1.0
    assert report["coverage"]["catalog_coverage@5"] == 1.0
    assert report["diversity"]["mean_unique_companies@5"] == 3.0
    assert report["latency"]["prediction_total_ms"] >= 0
    assert set(report["segments"]) == {"all", "cold_start", "engaged", "remote_compatible", "remote_incompatible"}
    assert report["segments"]["cold_start"]["groups"] == 2.0
