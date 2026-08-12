# Architecture

## Design principles

1. One deployable backend.
2. One frontend.
3. PostgreSQL is the source of truth.
4. FAISS is an in-memory retrieval index.
5. ML inference stays synchronous for the MVP.
6. Training is offline.
7. No infrastructure is added unless it solves a measured problem.

---

## High-level system

```text
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────┐
│   Next.js   │
└──────┬──────┘
       │ JSON
       ▼
┌─────────────┐
│   FastAPI   │
└──────┬──────┘
       │
       ├───────────────┬────────────────┬────────────────┐
       ▼               ▼                ▼                ▼
 Candidate        Job Catalog      Interactions   Recommendations
 Service           Service           Service          Service
       │               │                │                │
       └───────────────┴──────────┬─────┴────────────────┘
                                  ▼
                             PostgreSQL
                                  │
                 ┌────────────────┴───────────────┐
                 ▼                                ▼
             Feature reads                     Events
                 │
                 ▼
            Recommendation
                 │
          ┌──────┴──────┐
          ▼             ▼
       FAISS         Ranker
          │             │
          └──────┬──────┘
                 ▼
            Top results
```

---

## Recommendation request

```text
GET /v1/recommendations
        ↓
Authenticate user
        ↓
Load candidate profile
        ↓
Build user features
        ↓
Build / fetch candidate vector
        ↓
FAISS query
        ↓
Retrieve top 200 job IDs
        ↓
Load job features
        ↓
Build candidate-job features
        ↓
LightGBM predict (or content-score fallback)
        ↓
Apply business filters
        ↓
Diversity pass
        ↓
Return top 20
```

---

## Components

### Frontend

Responsibilities:

- authentication UI
- onboarding
- candidate profile editing
- recommendation feed
- job details
- user interaction capture
- loading and error states
- minimal client-side state

Do not put ranking logic in the frontend.

### FastAPI backend

Responsibilities:

- request validation
- authentication enforcement
- authorization
- rate limiting
- recommendation orchestration
- event logging
- model metadata
- persistence
- error handling

### PostgreSQL

Source of truth for:

- users
- candidate profiles
- skills
- jobs
- job skills
- interactions
- recommendation impressions
- model metadata

### FAISS

Purpose:

- fast approximate or exact nearest-neighbor retrieval
- candidate generation only

FAISS is rebuildable. PostgreSQL remains authoritative.

### Ranking model

MVP:

```text
LightGBM binary classifier or LambdaRank
```

Input:

```text
candidate features
job features
cross features
retrieval score
behavior features
```

Output:

```text
ranking score
```

### Offline trainer

Runs separately from API.

```text
database export
    ↓
dataset builder
    ↓
time split
    ↓
feature generation
    ↓
train
    ↓
evaluate
    ↓
persist artifact
    ↓
register model metadata
```

Phase 4 uses `ml/ranking` for grouped chronological splits, LambdaRank training,
baseline comparison, and artifact loading. The API records the loaded model version
on each recommendation request and falls back to the content score when the ranker
artifact is unavailable or incompatible.

---

## Model artifact layout

```text
ml/artifacts/
└── ranker/
    └── v001/
        ├── model.txt
        ├── feature_schema.json
        ├── metrics.json
        ├── training_config.json
        └── metadata.json
```

Embedding artifacts:

```text
ml/artifacts/
└── retrieval/
    └── v001/
        ├── faiss.index
        ├── item_ids.npy
        ├── embeddings.npy
        └── metadata.json
```

---

## Data freshness

MVP strategy:

- jobs: refresh manually or via scheduled seed/import script
- user interactions: write immediately
- user aggregate features: calculate on request or cache
- item embeddings: rebuild when catalog materially changes
- ranking model: retrain manually initially

Avoid pretending the MVP is real-time streaming infrastructure.

---

## Caching

Optional.

Use only after measuring need.

Potential cache keys:

```text
candidate_profile:{user_id}
recommendations:{user_id}:{model_version}
job:{job_id}
```

Recommended TTL for demo:

```text
recommendations: 5 minutes
job details: 1 hour
```

Invalidate recommendation cache after:

```text
save
dismiss
apply
profile update
preference update
```

---

## Failure behavior

### FAISS unavailable

Fallback:

```text
popular jobs filtered by preferences
```

### ranker unavailable

Fallback:

```text
retrieval similarity ordering
```

### database temporarily unavailable

Return:

```text
503 Service Unavailable
```

Do not fabricate recommendations.

---

## Scaling path

Only document this; do not build it in MVP.

```text
Current
FastAPI + PostgreSQL + FAISS

Scale step 1
Redis feature/recommendation cache

Scale step 2
Separate retrieval service

Scale step 3
Managed ANN/vector service

Scale step 4
Event queue

Scale step 5
Streaming feature pipeline

Scale step 6
Dedicated online feature store
```

---

## Main architectural constraint

Training and serving must use equivalent feature definitions.

Avoid:

```text
training feature != production feature
```

All shared features should live in reusable feature modules.
