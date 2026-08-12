# Implementation Checklist

## Completed through Phase 4

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

- [ ] App shell
- [ ] Header
- [ ] Login
- [ ] Onboarding
- [ ] Role selector
- [ ] Skill selector
- [ ] Preference form
- [ ] Recommendation feed
- [ ] Job card
- [ ] Match score
- [ ] Match reasons
- [ ] Filters
- [ ] Job detail
- [ ] Save
- [ ] Dismiss
- [ ] Apply
- [ ] Saved page
- [ ] Applications page
- [ ] Profile page
- [ ] Empty states
- [ ] Skeleton states
- [ ] Error states
- [ ] Mobile layout
- [ ] Keyboard navigation
- [ ] Focus states

## Evaluation

- [ ] Recall@5
- [ ] Recall@10
- [ ] Recall@20
- [ ] NDCG@10
- [ ] NDCG@20
- [ ] MRR
- [ ] Coverage
- [ ] Diversity
- [ ] Cold-start segment
- [ ] Active-user segment
- [ ] Latency p50
- [ ] Latency p95
- [ ] Fallback rate

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
