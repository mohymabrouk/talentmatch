# Roadmap

## Rule

Do not build future phases before the previous phase is measurable and working.

---

# Phase 0 — Repository and data

Deliver:

- repository structure
- local PostgreSQL
- migrations
- seed job dataset
- candidate profile schema
- basic API
- basic frontend shell

Exit criteria:

```text
jobs load
profile saves
database migrations work
frontend talks to backend
```

---

# Phase 1 — Content-based MVP

Deliver:

- job text preprocessing
- local embedding model
- FAISS index builder
- candidate profile embedding
- nearest-neighbor retrieval
- top 20 recommendations
- basic recommendation reasons

Exit criteria:

```text
new user can create profile
new user receives relevant jobs
recommendation endpoint works
retrieval evaluation exists
```

---

# Phase 2 — Interaction system

Deliver:

- impression logging
- click logging
- save
- dismiss
- apply
- recommendation request IDs
- recommendation item positions

Exit criteria:

```text
every served recommendation can be traced
behavioral events are linked to served ranking
```

---

# Phase 3 — Feature pipeline

Deliver:

- user features
- job features
- cross features
- time-safe feature generation
- shared training/serving feature definitions

Exit criteria:

```text
feature schema is versioned
training and serving outputs match
unit tests cover critical features
```

---

# Phase 4 — LightGBM ranker ✅

Deliver:

- labeled training dataset
- chronological train/validation/test split
- baseline metrics
- LightGBM training
- inference integration
- model artifact
- model metadata

Exit criteria:

```text
ranker beats baseline on selected metric
model version is stored with recommendations
fallback exists
```

Implemented in the current branch: `scripts/seed_demo_feedback.py`,
`scripts/build_features.py`, `scripts/train_ranker.py`, chronological grouped
evaluation, versioned artifacts, serving integration, model-version persistence,
and content-ranking fallback.

---

# Phase 5 — Evaluation suite

Deliver:

```text
Recall@K
NDCG@K
MRR
coverage
diversity
latency
segment metrics
```

Exit criteria:

```text
one command runs complete offline evaluation
metrics are persisted
README reports real results
```

---

# Phase 6 — UX polish

Deliver:

- complete onboarding
- recommendation feed
- filters
- job details
- saved jobs
- application tracking
- profile editor
- loading states
- empty states
- errors
- responsive UI
- accessibility pass

Exit criteria:

```text
desktop and mobile usable
no broken states
no placeholder design
```

---

# Phase 7 — Deployment

Deliver:

- backend Dockerfile
- frontend deployment
- hosted database
- environment configuration
- migrations
- readiness endpoint
- rate limiting
- CI
- smoke tests

Exit criteria:

```text
public URL works
first-time user flow works
recommendations work
interactions persist
```

---

# Phase 8 — Two-tower retrieval

Only after the ranker project is complete.

Deliver:

- candidate tower
- job tower
- hard negative sampling
- training loop
- learned embedding export
- FAISS rebuild
- comparison against sentence-transformer retrieval

Exit criteria:

```text
two-tower retrieval beats or meaningfully complements content retrieval
```

---

# Phase 9 — Advanced personalization

Optional:

- recent-history embedding
- weighted behavior decay
- company affinity
- title affinity
- skill affinity
- diversity reranking
- exploration strategy

Do not add reinforcement learning unless the data supports it.

---

# Phase 10 — MLOps extension

Optional:

- MLflow model registry
- scheduled retraining
- challenger vs champion
- automated regression checks
- drift reporting
- model promotion workflow

---

# Explicitly deferred

Do not implement for portfolio MVP:

```text
Kafka
Kubernetes
Spark
Flink
paid vector database
GPU serving
feature-store platform
multi-region deployment
microservices
automated applications
employer-side candidate ranking
```
