# Implementation Checklist

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
