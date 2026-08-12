# TalentMatch

Production-style job recommendation and ranking platform.

## Objective

Build a two-stage recommendation system that matches candidates to jobs using:

1. Candidate generation with embeddings + vector retrieval
2. Personalized ranking with engineered features + LightGBM
3. Behavioral feedback from clicks, saves, dismissals, and applications
4. Offline evaluation with ranking metrics
5. FastAPI serving
6. Minimal Next.js frontend
7. Zero-cost deployment path for portfolio/demo use

The project is designed to demonstrate practical ML engineering rather than notebook-only modeling.

## Implemented through Phase 2

The current implementation includes:

- PostgreSQL-compatible SQL migrations with SQLite support for fast local tests
- 12-job deterministic demo dataset and idempotent seed script
- Candidate profile, skills, jobs, recommendation requests/items, model versions, and append-only interactions
- FastAPI health, readiness, profile, jobs, recommendations, and interaction endpoints
- Local hashing embeddings with an optional locally cached sentence-transformer backend
- FAISS index artifacts when `faiss-cpu` is available, with an exact NumPy fallback
- Top-20 content recommendations, match reasons, request IDs, served positions, and automatic impressions
- Minimal Next.js frontend with profile setup and save/dismiss/apply/click feedback controls
- Retrieval evaluation for Recall@20, NDCG@20, and MRR

The demo identity is intentionally local-only. Authentication and authorization via an external provider remain future work.

## Local development

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[test]'

# SQLite is the default and needs no service.
.venv/bin/python scripts/migrate.py
.venv/bin/python scripts/seed_jobs.py
.venv/bin/python scripts/build_index.py

PYTHONPATH=backend .venv/bin/uvicorn app.main:app --reload --port 8000
```

For PostgreSQL, start `docker compose -f infra/docker-compose.yml up -d postgres`, set `DATABASE_URL` to `postgresql+psycopg://talentmatch:talentmatch@localhost:5432/talentmatch`, then run the same migration and seed commands.

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend uses `http://localhost:8000` by default. Set `NEXT_PUBLIC_API_URL` when the API is hosted elsewhere.

Validation commands:

```bash
.venv/bin/pytest -q
cd frontend && npm run build
.venv/bin/python scripts/evaluate_retrieval.py
```

---

## Core user flow

```text
Candidate creates profile
        ↓
Adds skills, role preferences, location, seniority
        ↓
System creates candidate representation
        ↓
Vector retrieval finds relevant jobs
        ↓
Ranker scores candidates
        ↓
Top recommendations are returned
        ↓
User clicks / saves / dismisses / applies
        ↓
Interactions are stored
        ↓
Features and future recommendations improve
```

---

## System architecture

```text
                    ┌─────────────────────┐
                    │      Next.js UI     │
                    └─────────┬───────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │      FastAPI API    │
                    └─────────┬───────────┘
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
      Candidate Service   Job Service   Recommendation Service
             │                │                │
             └────────────┬───┴───────┬────────┘
                          │           │
                          ▼           ▼
                    PostgreSQL      FAISS
                          │           │
                          │           ▼
                          │    Candidate Retrieval
                          │           │
                          │        Top 200
                          │           ▼
                          └────── Feature Pipeline
                                      │
                                      ▼
                               LightGBM Ranker
                                      │
                                      ▼
                                  Top 20 Jobs
```

---

## ML architecture

### Stage 1: candidate generation

```text
Candidate profile
     ↓
Candidate encoder
     ↓
Candidate embedding
     ↓
FAISS nearest-neighbor search
     ↓
Top 200 jobs
```

### Stage 2: ranking

```text
Candidate + Job + Interaction Features
                  ↓
             LightGBM
                  ↓
           relevance score
                  ↓
              Top 20
```

Later upgrade:

```text
Candidate Tower           Job Tower
      │                       │
      ▼                       ▼
candidate embedding      job embedding
      └──────── dot product ──┘
```

---

## Recommended stack

```text
Frontend       Next.js + TypeScript
Styling        Tailwind CSS
Backend        FastAPI
Database       PostgreSQL / Supabase
ORM            SQLAlchemy
Migrations     Alembic
ML             PyTorch + LightGBM
Embeddings     sentence-transformers
Vector search  FAISS
Data           pandas + scikit-learn
Validation     Pydantic
Testing        pytest
Tracking       MLflow locally
Container      Docker
CI             GitHub Actions
```

---

## Repository structure

```text
talentmatch/
│
├── README.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── FRONTEND_UX.md
│   ├── BACKEND_API.md
│   ├── ML_SYSTEM.md
│   ├── DATA_MODEL.md
│   ├── EVALUATION.md
│   ├── DEPLOYMENT.md
│   ├── SECURITY.md
│   └── ROADMAP.md
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── hooks/
│   └── types/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── main.py
│   └── tests/
│
├── ml/
│   ├── data/
│   ├── features/
│   ├── retrieval/
│   ├── ranking/
│   ├── training/
│   ├── evaluation/
│   ├── artifacts/
│   └── tests/
│
├── scripts/
│   ├── seed_jobs.py
│   ├── build_index.py
│   ├── train_ranker.py
│   └── evaluate.py
│
├── infra/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
│
└── .github/
    └── workflows/
```

---

## MVP scope

The MVP is complete when a user can:

- create a candidate profile
- add skills
- set desired roles
- set location / remote preference
- browse recommendations
- save a job
- dismiss a job
- mark a job as applied
- refresh recommendations
- see recommendation reasons
- view recommendation score metadata in development mode

The system must:

- return recommendations through an API
- retrieve candidates through vector similarity
- rank candidates with a trained model
- store interactions
- support cold-start users
- expose model version
- measure offline ranking quality

---

## Non-goals for MVP

Do not add:

- Kafka
- Kubernetes
- Spark
- microservices
- paid vector databases
- paid embedding APIs
- LLMs
- complex messaging queues
- distributed training
- real company scraping
- automated job applications

These can be discussed in scaling documentation without being implemented.

---

## Primary success criteria

```text
Recommendation API p95 latency     < 250 ms
Recall@20                          measurable baseline + improvement
NDCG@20                            measurable baseline + improvement
Cold-start recommendations         supported
Interaction logging                complete
Model versioning                   exposed
Zero-cost demo architecture        supported
```

---

## Portfolio story

The final project should demonstrate:

```text
data processing
feature engineering
embeddings
vector retrieval
learning-to-rank
behavioral feedback
cold start
offline evaluation
model serving
API design
database design
frontend integration
monitoring
deployment
```

This is an ML engineering project first and a web application second.
