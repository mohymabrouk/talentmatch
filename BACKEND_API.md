# Backend API

## Backend goals

- explicit contracts
- typed request/response models
- predictable errors
- rate limiting
- authentication
- no ML logic inside route handlers
- testable service layer
- structured logging

---

## Package layout

```text
backend/app/
├── api/
│   ├── deps.py
│   └── routes/
│       ├── auth.py
│       ├── profile.py
│       ├── jobs.py
│       ├── recommendations.py
│       ├── interactions.py
│       └── health.py
│
├── core/
│   ├── config.py
│   ├── security.py
│   ├── rate_limit.py
│   └── logging.py
│
├── db/
│   ├── session.py
│   └── base.py
│
├── models/
├── schemas/
├── repositories/
├── services/
└── main.py
```

---

## API versioning

Use:

```text
/api/v1
```

Example:

```text
GET /api/v1/recommendations
```

---

## Authentication

MVP:

```text
Supabase Auth
```

Backend receives JWT.

Flow:

```text
Frontend
   ↓
Supabase login
   ↓
JWT
   ↓
Authorization: Bearer <token>
   ↓
FastAPI verifies token
```

Never trust `user_id` sent from the client for protected user-scoped resources.

Derive user identity from the verified token.

---

## Endpoints

### Health

```http
GET /api/v1/health
```

Response:

```json
{
  "status": "ok"
}
```

### Readiness

```http
GET /api/v1/ready
```

Checks:

- database reachable
- retrieval index loaded
- ranker loaded

Response:

```json
{
  "status": "ready",
  "database": true,
  "retrieval": true,
  "ranker": true
}
```

---

## Profile

### Get profile

```http
GET /api/v1/profile
```

### Update profile

```http
PATCH /api/v1/profile
```

Request:

```json
{
  "target_roles": [
    "Machine Learning Engineer",
    "Applied AI Engineer"
  ],
  "skills": [
    "Python",
    "PyTorch",
    "FastAPI"
  ],
  "years_experience": 3,
  "location": "Paris",
  "remote_preference": "hybrid"
}
```

---

## Jobs

### List jobs

```http
GET /api/v1/jobs
```

Query:

```text
page
page_size
location
remote_mode
seniority
posted_after
```

### Job detail

```http
GET /api/v1/jobs/{job_id}
```

---

## Recommendations

```http
GET /api/v1/recommendations
```

Query:

```text
limit=20
cursor=<optional>
```

Response:

```json
{
  "model_version": "ranker-v001",
  "retrieval_version": "retrieval-v001",
  "items": [
    {
      "job_id": "job_123",
      "title": "Machine Learning Engineer",
      "company": "Acme",
      "location": "Paris",
      "remote_mode": "hybrid",
      "score": 0.9132,
      "match_reasons": [
        "Strong skill overlap",
        "Matches preferred role"
      ]
    }
  ]
}
```

Do not expose raw internal feature values by default.

---

## Interactions

Single generic endpoint:

```http
POST /api/v1/interactions
```

Request:

```json
{
  "job_id": "job_123",
  "event_type": "save",
  "recommendation_request_id": "rec_abc123"
}
```

Allowed event types:

```text
impression
click
save
dismiss
apply
```

Backend adds:

```text
user_id
timestamp
model_version
```

Do not allow client to set those authoritative fields.

---

## Recommendation request ID

Every recommendation response gets a request ID.

Purpose:

- trace impressions
- connect interactions to served rankings
- support offline evaluation
- debug model behavior

Example:

```json
{
  "recommendation_request_id": "rec_01J...",
  "items": []
}
```

---

## Rate limiting

Apply per authenticated user and per IP for unauthenticated endpoints.

Suggested demo limits:

```text
GET recommendations
30 requests / minute / user

POST interactions
120 requests / minute / user

GET jobs
60 requests / minute / IP

auth-sensitive endpoints
20 requests / minute / IP
```

Return:

```http
429 Too Many Requests
```

Headers:

```text
Retry-After
X-RateLimit-Limit
X-RateLimit-Remaining
```

---

## Request limits

Set:

```text
maximum JSON body size
maximum string lengths
maximum skills per profile
maximum roles per profile
maximum page size
```

Example:

```text
skills <= 50
roles <= 10
page_size <= 100
```

---

## Timeouts

Recommendation service:

```text
hard timeout: 2 seconds
```

Target:

```text
p95 < 250 ms
```

If ranker fails but retrieval succeeds:

```text
fallback to retrieval ordering
```

Return metadata internally through logs.

---

## Errors

Format:

```json
{
  "error": {
    "code": "PROFILE_INCOMPLETE",
    "message": "Complete your profile before requesting recommendations."
  }
}
```

Common codes:

```text
UNAUTHORIZED
FORBIDDEN
NOT_FOUND
VALIDATION_ERROR
PROFILE_INCOMPLETE
RATE_LIMITED
RECOMMENDATION_UNAVAILABLE
INTERNAL_ERROR
```

Do not leak stack traces.

---

## Service layer

Route:

```python
@router.get("/recommendations")
async def get_recommendations(...):
    return await service.recommend(...)
```

Service owns orchestration:

```text
load profile
build features
retrieve candidates
rank
filter
persist impression metadata
return response
```

Repository owns database access.

ML package owns model inference.

---

## Logging

Structured JSON fields:

```text
request_id
user_id
route
status_code
duration_ms
model_version
retrieval_version
candidate_count
returned_count
fallback_used
```

Never log:

```text
JWTs
passwords
full resume text
sensitive profile fields
```

---

## Testing

Required:

```text
unit tests
service tests
API contract tests
database tests
recommendation fallback tests
rate-limit tests
authorization tests
```

Critical cases:

- unauthenticated user cannot read private profile
- user cannot write another user's interaction
- malformed event rejected
- missing ranker uses fallback
- missing retrieval index fails readiness
- recommendation endpoint respects limit
