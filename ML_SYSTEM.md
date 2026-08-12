# ML System

## Goal

Rank jobs for a candidate.

The system has two stages:

```text
retrieval
   ↓
ranking
```

Retrieval maximizes recall.
Ranking maximizes ordering quality.

---

# Stage 0 — Baselines

Always build baselines first.

## Baseline A: newest jobs

```text
score = posted_at
```

## Baseline B: popularity

```text
score =
click_count
+ 3 * save_count
+ 5 * apply_count
```

## Baseline C: rule-based skill overlap

```text
score =
matched_candidate_skills
/
required_job_skills
```

All later models must beat these baselines on offline metrics.

---

# Stage 1 — Content retrieval

## Candidate text representation

Construct structured text:

```text
Target roles:
Machine Learning Engineer, Applied AI Engineer

Skills:
Python, PyTorch, FastAPI, Docker, PostgreSQL

Experience:
3 years

Location:
Paris

Work preference:
Hybrid or Remote
```

## Job representation

```text
Title:
Machine Learning Engineer

Skills:
Python, PyTorch, Docker, AWS

Description:
...
```

Use a local sentence-transformer model.

Output:

```text
candidate vector: d dimensions
job vector: d dimensions
```

Normalize vectors if cosine similarity is used.

---

## FAISS index

Build offline:

```text
active jobs
   ↓
job encoder
   ↓
embeddings matrix
   ↓
FAISS index
```

Artifacts:

```text
faiss.index
item_ids.npy
metadata.json
```

Request:

```text
candidate vector
    ↓
search(k=200)
    ↓
job IDs + similarity scores
```

---

# Stage 2 — Ranking

## First production ranker

Use LightGBM.

Why:

- fast
- strong tabular baseline
- interpretable feature importance
- cheap CPU inference
- no GPU required
- easy to deploy

---

## Feature groups

### Retrieval

```text
embedding_similarity
retrieval_position
```

### Skill match

```text
skill_overlap_count
skill_overlap_ratio
required_skill_match_ratio
missing_required_skill_count
```

### Role

```text
title_similarity
target_role_exact_match
target_role_semantic_similarity
```

### Experience

```text
candidate_years_experience
job_required_years
experience_gap
seniority_match
```

### Location

```text
same_city
same_country
remote_compatible
distance_bucket
```

### Compensation

Only if reliable:

```text
salary_above_minimum
salary_gap
```

### Job quality/freshness

```text
job_age_days
job_popularity_7d
job_click_rate
job_apply_rate
```

### Candidate behavior

```text
candidate_click_rate_30d
candidate_save_rate_30d
candidate_apply_rate_30d
recent_role_affinity
recent_company_affinity
recent_skill_affinity
```

### Cross features

```text
candidate_job_skill_overlap
candidate_job_title_similarity
candidate_job_location_match
candidate_job_seniority_match
```

---

# Labels

Preferred positive hierarchy:

```text
apply   strongest
save    strong
click   weak
impression with no action   negative
dismiss                    explicit negative
```

Simple binary target for first ranker:

```text
positive:
save OR apply

negative:
impression without later save/apply
```

Alternative:

```text
apply = 5
save = 3
click = 1
dismiss = -2
```

Do not overcomplicate labels before you have enough data.

---

# Training dataset

One row:

```text
user_id
job_id
served_at
label
feature_1
feature_2
...
```

Important:

Features must only use information available at `served_at`.

No future leakage.

---

# Time-based split

Do not random split interaction events.

Use:

```text
train      oldest 70%
validation next 15%
test       latest 15%
```

or date windows.

Example:

```text
Jan–Apr  train
May      validation
Jun      test
```

---

# Negative sampling

For retrieval model:

Positive:

```text
user interacted positively with job
```

Negatives:

```text
shown but ignored
random active jobs
hard negatives from semantic retrieval
```

Hard negatives are especially useful:

```text
job is semantically similar
but user did not engage
```

---

# Two-tower upgrade

After the LightGBM system works.

## Candidate tower inputs

```text
user ID optional
target roles
skills
experience
location
recent interactions
```

## Job tower inputs

```text
job ID optional
title
description
skills
seniority
location
```

Output:

```text
candidate embedding
job embedding
```

Train with contrastive objective.

Positive pair:

```text
candidate applied/saved job
```

Negative pair:

```text
candidate ignored/dismissed job
```

---

# Cold start

## New candidate

No behavior exists.

Use:

```text
profile content
skills
target roles
location
experience
```

Retrieval works immediately.

Ranker uses content and cross features.

## New job

No interaction features exist.

Use:

```text
job content embedding
skill features
freshness
```

Avoid assigning zero quality solely because a job is new.

---

# Diversity

Pure ranking may return near-duplicates.

Apply a small post-ranking diversity pass.

Example constraints:

```text
max 3 jobs from same company in top 20
avoid 10 near-identical titles
mix high-score adjacent roles when relevant
```

Do not let diversity override obvious relevance.

---

# Explainability

Generate reasons from deterministic features.

Example:

```text
Strong skill overlap
Matches your preferred role
Compatible with your remote preference
Recently posted
```

Do not use an LLM.

Do not claim causal explanations.

---

# Inference contract

Input:

```python
CandidateContext
List[JobCandidate]
```

Output:

```python
List[RankedJob]
```

Include:

```text
job_id
retrieval_score
ranking_score
reason_codes
```

Reason codes:

```text
SKILL_MATCH
ROLE_MATCH
LOCATION_MATCH
REMOTE_MATCH
EXPERIENCE_MATCH
FRESH_JOB
```

Frontend converts these into display strings.

---

# Model versioning

Every served recommendation stores:

```text
retrieval_version
ranker_version
```

Example:

```text
retrieval-v003
ranker-v007
```

Never deploy a model artifact without version metadata.

---

# Reproducibility

Training config must store:

```text
dataset cutoff
feature list
hyperparameters
random seed
code commit
metrics
artifact checksum
```

---

# Retraining

MVP:

manual command.

```bash
python scripts/train_ranker.py
```

Later:

scheduled workflow.

Trigger only when there is enough new labeled data.

---

# No paid inference

All ML components can run locally/CPU:

```text
sentence-transformers
FAISS
LightGBM
PyTorch optional
```

No external inference API is required.
