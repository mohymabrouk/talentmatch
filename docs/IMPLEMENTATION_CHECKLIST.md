# Implementation Checklist

## Completed through Phase 6

- [x] Create monorepo
- [x] Add frontend
- [x] Add backend
- [x] Add ML package
- [x] Add docs
- [x] Add Docker
- [x] Create users table
- [x] Create candidate profiles
- [x] Create skills
- [x] Create candidate skills
- [x] Create candidate target roles
- [x] Create jobs
- [x] Create job skills
- [x] Create interactions
- [x] Create recommendation requests
- [x] Create recommendation items
- [x] Create model versions
- [x] Add indexes
- [x] Add migrations
- [x] Seed deterministic demo jobs
- [x] Normalize seeded skill values
- [x] Select local embedding fallback
- [x] Build index and ID mapping
- [x] Normalize vectors
- [x] Encode candidate profile
- [x] Search top 200 candidates
- [x] Add retrieval fallback
- [x] Evaluate Recall@20
- [x] Health endpoint
- [x] Readiness endpoint
- [x] Profile GET
- [x] Profile PATCH
- [x] Jobs list
- [x] Job detail
- [x] Recommendations endpoint
- [x] Interaction endpoint
- [x] Request validation
- [x] Recommendation request IDs
- [x] Recommendation item positions
- [x] Versioned feature schema
- [x] User feature definitions
- [x] Job feature definitions
- [x] Cross feature definitions
- [x] Time-safe point-in-time snapshots
- [x] Shared training/serving feature builder
- [x] Feature dataset exporter
- [x] Critical feature unit tests
- [x] Labeled feedback dataset definition
- [x] Deterministic demo feedback seeder
- [x] Chronological grouped train/validation/test split
- [x] Retrieval, skill, popularity, and freshness baselines
- [x] LightGBM LambdaRank trainer
- [x] Versioned ranker artifact and metadata
- [x] Ranker schema compatibility checks
- [x] Ranker inference integration
- [x] Content-ranking fallback
- [x] Model version persisted per recommendation request
- [x] Ranker training and serving tests
- [x] Complete offline evaluation command
- [x] Recall@5, Recall@10, Recall@20
- [x] NDCG@5, NDCG@10, NDCG@20, MRR
- [x] Coverage and diversity metrics
- [x] Latency p50, p95, p99
- [x] Cold-start, engaged-user, and remote segments
- [x] Fallback and empty-result reliability metrics
- [x] Persisted evaluation report
- [x] Responsive application shell
- [x] Profile onboarding/editor
- [x] Recommendation feed and filters
- [x] Job detail view
- [x] Saved jobs and application tracking views
- [x] Loading, empty, and error states
- [x] Keyboard focus and semantic accessibility pass

The detailed backlog below is retained for future phases; the completed status above is authoritative.

## Repository

- [ ] Create monorepo
- [ ] Add frontend
- [ ] Add backend
- [ ] Add ML package
- [ ] Add docs
- [ ] Add CI
- [ ] Add Docker

## Database

- [ ] Create users table
- [ ] Create candidate profiles
- [ ] Create roles
- [ ] Create skills
- [ ] Create candidate skills
- [ ] Create jobs
- [ ] Create job skills
- [ ] Create interactions
- [ ] Create recommendation requests
- [ ] Create recommendation items
- [ ] Create model versions
- [ ] Add indexes
- [ ] Add migrations

## Job ingestion

- [ ] Select public dataset
- [ ] Normalize title
- [ ] Normalize company
- [ ] Normalize location
- [ ] Normalize remote mode
- [ ] Normalize seniority
- [ ] Normalize skills
- [ ] Remove duplicates
- [ ] Mark inactive jobs
- [ ] Seed database

## Retrieval

- [ ] Select local embedding model
- [ ] Build job text
- [ ] Encode active jobs
- [ ] Normalize vectors
- [ ] Build FAISS index
- [ ] Save ID mapping
- [ ] Load index on backend startup
- [ ] Encode candidate profile
- [ ] Search top 200
- [ ] Add retrieval fallback
- [ ] Evaluate Recall@K

## Features

- [ ] Skill overlap
- [ ] Required-skill overlap
- [ ] Title similarity
- [ ] Role match
- [ ] Experience gap
- [ ] Seniority match
- [ ] Location match
- [ ] Remote match
- [ ] Job age
- [ ] Job popularity
- [ ] Candidate click rate
- [ ] Candidate save rate
- [ ] Candidate apply rate
- [ ] Retrieval score
- [ ] Feature schema tests

## Ranking

- [ ] Define label
- [ ] Build time-safe dataset
- [ ] Build chronological split
- [ ] Train popularity baseline
- [ ] Train skill-overlap baseline
- [ ] Train LightGBM
- [ ] Evaluate
- [ ] Persist artifact
- [ ] Persist metrics
- [ ] Register model version
- [ ] Load model in backend
- [ ] Add fallback
- [ ] Record model version per request

## API

- [ ] Health endpoint
- [ ] Readiness endpoint
- [ ] Profile GET
- [ ] Profile PATCH
- [ ] Jobs list
- [ ] Job detail
- [ ] Recommendations endpoint
- [ ] Interaction endpoint
- [ ] Validation
- [ ] Authorization
- [ ] Rate limiting
- [ ] Structured errors
- [ ] Request IDs
- [ ] Structured logs

## Frontend

- [x] App shell
- [x] Header
- [ ] Login
- [x] Onboarding
- [x] Role selector
- [x] Skill selector
- [x] Preference form
- [x] Recommendation feed
- [x] Job card
- [x] Match score
- [x] Match reasons
- [x] Filters
- [x] Job detail
- [x] Save
- [x] Dismiss
- [x] Apply
- [x] Saved page
- [x] Applications page
- [x] Profile page
- [x] Empty states
- [x] Skeleton states
- [x] Error states
- [x] Mobile layout
- [x] Keyboard navigation
- [x] Focus states

## Evaluation

- [x] Recall@5
- [x] Recall@10
- [x] Recall@20
- [x] NDCG@10
- [x] NDCG@20
- [x] MRR
- [x] Coverage
- [x] Diversity
- [x] Cold-start segment
- [x] Active-user segment
- [x] Latency p50
- [x] Latency p95
- [x] Fallback rate

## Security

- [ ] JWT verification
- [ ] User ownership checks
- [ ] CORS
- [ ] Body limits
- [ ] Input length limits
- [ ] Rate limiting
- [ ] Secrets in environment variables
- [ ] No sensitive logs
- [ ] HTTPS-only external URLs
- [ ] Dependency audit

## Deployment

- [ ] Production database
- [ ] Migrations
- [ ] Backend deploy
- [ ] Frontend deploy
- [ ] Environment variables
- [ ] Model artifacts available
- [ ] FAISS index available
- [ ] `/ready` passes
- [ ] Smoke test
- [ ] Cold-start UX acceptable
- [ ] Public demo URL

## Portfolio

- [ ] Architecture diagram
- [ ] Real screenshots
- [ ] Real evaluation table
- [ ] Baseline comparison
- [ ] Latency measurements
- [ ] Tradeoffs section
- [ ] Cold-start explanation
- [ ] Scaling section
- [ ] Demo instructions
- [ ] No fabricated metrics
