# Security

## Scope

This is a portfolio/demo system, but the backend should follow production-safe defaults.

---

# Authentication

- use external auth provider
- verify JWT on backend
- derive user identity from token
- reject expired tokens
- do not trust client-provided user IDs

---

# Authorization

Every user-scoped query must include authenticated ownership.

Example:

Bad:

```sql
SELECT * FROM candidate_profiles WHERE user_id = :body_user_id;
```

Good:

```text
user_id comes from verified authentication context
```

---

# Rate limiting

Protect:

```text
recommendations
interactions
profile mutations
authentication-sensitive routes
```

Suggested:

```text
recommendations   30/min/user
interactions     120/min/user
profile updates   20/min/user
```

---

# Input validation

Validate:

```text
string length
enum values
list length
numeric ranges
UUID format
pagination maximums
```

Do not accept arbitrary event types.

---

# SQL

Use ORM or parameterized queries.

Never concatenate user input into SQL.

---

# CORS

Production:

```text
allow only deployed frontend origin
```

Do not use:

```text
*
```

with credentials.

---

# Secrets

Store in environment variables.

Never commit secrets.

Rotate immediately if exposed.

---

# Logging

Do not log:

```text
authorization headers
JWTs
passwords
full raw CV content
sensitive profile data
database credentials
```

---

# Data minimization

Do not collect data that the recommender does not need.

Avoid:

```text
gender
ethnicity
religion
photo
date of birth
marital status
health data
```

The ranking system should use professional relevance signals.

---

# Recommendation fairness

For the portfolio system:

- do not use protected characteristics as model features
- document limitations
- evaluate distribution across major non-sensitive segments
- avoid claiming the model is legally fair or bias-free

This demo is not an employment decision system.

It ranks jobs for candidates.
It does not rank candidates for employers.

---

# External URLs

If jobs include external application URLs:

- validate scheme
- allow only `https`
- display destination domain
- use safe redirect behavior

---

# Dependency security

CI should include:

```text
Python dependency audit
npm audit or equivalent
```

Keep dependencies pinned.

---

# Error handling

Production responses should never include:

```text
stack traces
database queries
filesystem paths
secret values
```

---

# Abuse cases

Consider:

```text
event spam
recommendation endpoint scraping
oversized request payload
invalid job IDs
repeated dismissal spam
automation against interaction endpoint
```

Mitigation:

```text
rate limits
body limits
authentication
validation
idempotency where useful
```
