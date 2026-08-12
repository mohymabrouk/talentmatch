# Deployment

## Objective

Run a public portfolio demo at zero or near-zero cost.

The MVP is designed to work without paid ML inference.

---

## Suggested deployment

```text
Frontend    Vercel Hobby
Backend     free hobby web host
Database    Supabase Free
ML models   bundled with backend artifact or downloaded at startup
FAISS       loaded into backend memory
CI          GitHub Actions
```

Free-tier availability changes over time. Verify provider limits before deployment.

---

# Environment split

```text
local
preview
production
```

Do not share production secrets with preview environments unless required.

---

# Backend startup

Startup sequence:

```text
load config
   ↓
connect database
   ↓
load active ranker
   ↓
load FAISS index
   ↓
validate artifact compatibility
   ↓
mark ready
```

`/health` can return before models are loaded.

`/ready` should not.

---

# Model artifact deployment

Option A for MVP:

```text
commit small artifacts to release storage
```

Option B:

```text
download artifacts from object storage at startup
```

Avoid storing very large binary artifacts directly in Git history.

---

# Docker backend

Backend container responsibilities:

```text
install Python dependencies
copy application
copy/download ML artifacts
run migrations separately
start uvicorn
```

Example runtime:

```text
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

# Database migrations

Use Alembic.

Deployment order:

```text
1. apply backward-compatible migration
2. deploy backend
3. validate
4. remove deprecated fields later
```

Do not make destructive schema changes in the same step as application rollout.

---

# CI

Pull request:

```text
lint
type checks
unit tests
backend tests
ML feature tests
frontend build
```

Main branch:

```text
all PR checks
build deployable artifacts
deploy
smoke test
```

---

# Smoke tests

After deploy:

```text
GET /health → 200
GET /ready → 200
auth path works
recommendation request returns valid schema
interaction write succeeds
```

---

# Secrets

Never commit:

```text
database URL
JWT secret
Supabase service role key
private model storage credentials
```

Use provider environment variables.

---

# Zero-cost constraints

To remain cheap:

- CPU inference only
- modest embedding model
- FAISS in memory
- small catalog
- no paid LLM
- no managed vector DB
- no Kafka
- no GPU service
- no always-on worker requirement

---

# Cold starts

Free backend hosting may sleep.

Acceptable portfolio behavior:

```text
first request after inactivity is slow
subsequent requests are fast
```

Frontend should show:

```text
Loading recommendations…
```

Do not hide long cold starts with fake progress percentages.

---

# Dataset size target

Demo target:

```text
10k–100k jobs
```

Choose based on backend memory.

FAISS vectors:

```text
100k × 384 × float32
≈ 154 MB
```

Use smaller models or lower precision if necessary.

---

# Production-like local setup

Use Docker Compose:

```text
frontend
backend
postgres
```

FAISS stays inside backend process.

MLflow can remain local and optional.

---

# Release checklist

```text
[ ] migrations applied
[ ] active model exists
[ ] FAISS index exists
[ ] feature schema matches model
[ ] /ready passes
[ ] frontend API URL correct
[ ] auth redirect URL correct
[ ] rate limits enabled
[ ] secrets configured
[ ] smoke test passes
```
