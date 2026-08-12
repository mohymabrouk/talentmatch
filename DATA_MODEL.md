# Data Model

## Principles

- PostgreSQL is authoritative.
- Use normalized tables for core entities.
- Keep model artifacts outside relational rows.
- Record recommendation impressions for evaluation.
- Do not overwrite behavioral history.

---

## Core tables

```text
users
candidate_profiles
skills
candidate_skills
jobs
job_skills
interactions
recommendation_requests
recommendation_items
model_versions
```

---

# users

```text
id                  uuid primary key
auth_provider_id    text unique not null
email               text
created_at          timestamptz not null
updated_at          timestamptz not null
```

---

# candidate_profiles

```text
user_id               uuid primary key references users(id)
current_title          text
years_experience       numeric
location               text
remote_preference      text
minimum_salary         integer nullable
salary_currency        text nullable
created_at             timestamptz
updated_at             timestamptz
```

Allowed `remote_preference`:

```text
onsite
hybrid
remote
any
```

---

# candidate_target_roles

```text
id          uuid primary key
user_id     uuid references users(id)
role_name   text not null
priority    integer default 0
```

Unique:

```text
(user_id, role_name)
```

---

# skills

```text
id            uuid primary key
normalized    text unique not null
display_name  text not null
```

---

# candidate_skills

```text
user_id        uuid references users(id)
skill_id       uuid references skills(id)
proficiency    smallint nullable
years_used     numeric nullable
```

Primary key:

```text
(user_id, skill_id)
```

---

# jobs

```text
id                   uuid primary key
external_id          text nullable
title                text not null
company_name         text not null
description          text not null
location             text nullable
remote_mode          text nullable
seniority            text nullable
employment_type      text nullable
salary_min           integer nullable
salary_max           integer nullable
salary_currency      text nullable
source               text nullable
source_url            text nullable
posted_at             timestamptz nullable
expires_at            timestamptz nullable
is_active             boolean default true
created_at            timestamptz not null
updated_at            timestamptz not null
```

---

# job_skills

```text
job_id        uuid references jobs(id)
skill_id      uuid references skills(id)
required      boolean default false
weight        numeric default 1
```

Primary key:

```text
(job_id, skill_id)
```

---

# interactions

Append-only.

```text
id                         uuid primary key
user_id                    uuid references users(id)
job_id                     uuid references jobs(id)
event_type                 text not null
recommendation_request_id  uuid nullable
model_version              text nullable
created_at                 timestamptz not null
```

Allowed:

```text
impression
click
save
dismiss
apply
```

Indexes:

```text
(user_id, created_at desc)
(job_id, created_at desc)
(user_id, job_id)
(event_type, created_at)
```

---

# recommendation_requests

```text
id                 uuid primary key
user_id            uuid references users(id)
model_version      text not null
retrieval_version  text not null
candidate_count    integer not null
returned_count     integer not null
latency_ms         integer
fallback_used      boolean default false
created_at         timestamptz not null
```

---

# recommendation_items

Stores served order.

```text
request_id        uuid references recommendation_requests(id)
job_id            uuid references jobs(id)
position          integer not null
retrieval_score   numeric nullable
ranking_score     numeric nullable
```

Primary key:

```text
(request_id, job_id)
```

Unique:

```text
(request_id, position)
```

This table is critical for evaluation.

---

# model_versions

```text
id              uuid primary key
model_type      text not null
version         text unique not null
status          text not null
artifact_path   text not null
metrics_json    jsonb
created_at      timestamptz not null
activated_at    timestamptz nullable
```

Allowed status:

```text
training
candidate
active
archived
failed
```

---

## Derived features

Do not store every computed feature initially.

Calculate from relational data where cheap.

Potential cached features:

```text
user_interaction_count_7d
user_interaction_count_30d
user_apply_rate
user_save_rate
job_click_rate
job_apply_rate
job_popularity_7d
```

If caching later, use a dedicated feature table.

---

## Example interaction history

```text
user_42
│
├── impression → job_101
├── click      → job_101
├── save       → job_101
│
├── impression → job_205
├── dismiss    → job_205
│
└── impression → job_390
    apply      → job_390
```

---

## Privacy

Do not require for MVP:

- date of birth
- gender
- ethnicity
- photo
- marital status
- protected characteristics

Do not train ranking features on protected characteristics.

The project should recommend jobs based on professional profile and interaction data.
