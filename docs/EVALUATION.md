# Evaluation

## Goal

Measure whether the recommendation system improves ranking quality without relying on subjective demos.

---

# Offline metrics

Primary:

```text
Recall@K
NDCG@K
MRR
HitRate@K
```

Secondary:

```text
coverage
diversity
freshness
latency
fallback rate
```

---

## Recall@K

Question:

```text
Of the jobs the user actually engaged with, how many were present in top K?
```

Primary K values:

```text
5
10
20
```

---

## NDCG@K

Measures ranking quality when stronger labels matter.

Possible gains:

```text
apply    5
save     3
click    1
```

Higher-value events should appear nearer the top.

---

## MRR

Useful when evaluating the first relevant recommendation.

```text
MRR = mean reciprocal rank of first relevant item
```

---

# Evaluation dataset

Use chronological holdout.

For each candidate:

```text
history before cutoff
        ↓
generate recommendation
        ↓
compare with future positive interaction
```

Never train and test on the same future event.

---

# Baseline table

The deterministic local fixture produces the following measured Phase 5 report.
These values are demo-data measurements, not production claims.

```text
Model                    Recall@20   NDCG@20   MRR
---------------------------------------------------
Newest                    1.000       0.834      0.778
Popularity                1.000       1.000      1.000
Skill overlap             1.000       0.754      0.667
Embedding retrieval       1.000       0.844      1.000
LightGBM ranker            1.000       1.000      1.000
Two-tower + ranker        not run     not run    not run
```

Run `.venv/bin/python scripts/evaluate.py` to regenerate the persisted report.
Do not treat the deterministic fixture as a production benchmark.

---

# Retrieval evaluation

Evaluate candidate generation separately from ranking.

Question:

```text
Can retrieval put the relevant job inside top 200?
```

Metrics:

```text
Recall@50
Recall@100
Recall@200
```

If retrieval recall is poor, ranking cannot recover the missing job.

---

# Ranking evaluation

Evaluate only on a consistent candidate set.

Metrics:

```text
NDCG@10
NDCG@20
MRR
Precision@K
```

Phase 4 currently evaluates grouped recommendation requests with a chronological
70/15/15 split. The trainer reports NDCG@20 and MRR for the LambdaRank model and
these deterministic baselines:

```text
retrieval score
skill overlap ratio
job popularity
newest job (negative age)
```

Promotion requires the ranker to beat the selected retrieval baseline on NDCG@20.
Metrics, training configuration, feature schema, and model metadata are persisted
alongside the LightGBM artifact.

---

# Segment evaluation

Break down by:

```text
new users
active users
low-activity users
remote-preferring users
seniority level
job age
job category
```

Important question:

```text
Does the model work only for highly active users?
```

---

# Cold-start evaluation

Create profile-only candidates.

Evaluate:

```text
content retrieval quality
skill match
role match
location compatibility
```

Cold-start performance should be reported separately.

---

# Coverage

Measure:

```text
unique recommended jobs
/
eligible active jobs
```

Low coverage means a small number of jobs dominate recommendations.

---

# Diversity

Simple metrics:

```text
unique companies in top K
unique normalized titles in top K
average pairwise embedding distance
```

---

# Freshness

Measure age distribution of recommended jobs:

```text
median days since posted
p90 days since posted
```

Do not force freshness at the cost of relevance.

---

# Latency

Track recommendation endpoint:

```text
p50
p95
p99
```

Break down:

```text
profile load
feature generation
FAISS retrieval
DB job load
ranker inference
post-processing
```

Target MVP:

```text
p95 < 250 ms
```

If free hosting introduces cold starts, report warm latency separately.

---

# Reliability

Track:

```text
recommendation errors
fallback rate
empty-result rate
index-load failures
ranker-load failures
```

The complete report persists `fallback_rate` and `empty_result_requests` from
recommendation request records, alongside retrieval/ranking latency p50, p95,
and p99.

---

# Regression tests

Every candidate model should be compared against active model.

Block promotion when:

```text
NDCG regression > threshold
Recall regression > threshold
latency unacceptable
artifact incompatible
feature schema mismatch
```

---

# Evaluation command

Target developer experience:

```bash
python scripts/evaluate.py \
  --model ml/artifacts/ranker/v001 \
  --split test
```

Output:

```text
Recall@20: ...
NDCG@20: ...
MRR: ...
Coverage: ...
p95 inference: ...
```

Also write:

```text
metrics.json
```

---

# Model card

Every promoted model should have:

```text
version
training window
feature set
dataset size
metrics
known limitations
artifact location
```

---

# Honest portfolio reporting

Report:

```text
actual metrics
actual dataset
actual latency
actual model version
```

Do not report theoretical gains.
Do not fabricate A/B tests.
Do not call offline evaluation "production uplift."
