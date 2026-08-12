CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    auth_provider_id VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(320),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS candidate_profiles (
    user_id VARCHAR(36) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    current_title VARCHAR(160),
    years_experience DOUBLE PRECISION,
    location VARCHAR(160),
    remote_preference VARCHAR(20),
    minimum_salary INTEGER,
    salary_currency VARCHAR(8),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (remote_preference IS NULL OR remote_preference IN ('onsite', 'hybrid', 'remote', 'any')),
    CHECK (years_experience IS NULL OR years_experience >= 0)
);

CREATE TABLE IF NOT EXISTS candidate_target_roles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_name VARCHAR(160) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    UNIQUE (user_id, role_name)
);

CREATE TABLE IF NOT EXISTS skills (
    id VARCHAR(36) PRIMARY KEY,
    normalized VARCHAR(120) NOT NULL UNIQUE,
    display_name VARCHAR(120) NOT NULL
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    skill_id VARCHAR(36) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    proficiency INTEGER,
    years_used DOUBLE PRECISION,
    PRIMARY KEY (user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS jobs (
    id VARCHAR(36) PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,
    title VARCHAR(240) NOT NULL,
    company_name VARCHAR(240) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(160),
    remote_mode VARCHAR(20),
    seniority VARCHAR(40),
    employment_type VARCHAR(40),
    salary_min INTEGER,
    salary_max INTEGER,
    salary_currency VARCHAR(8),
    source VARCHAR(80),
    source_url VARCHAR(1000),
    posted_at TIMESTAMP,
    expires_at TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (remote_mode IS NULL OR remote_mode IN ('onsite', 'hybrid', 'remote'))
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id VARCHAR(36) NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    required BOOLEAN NOT NULL DEFAULT FALSE,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    PRIMARY KEY (job_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_jobs_active_posted ON jobs(is_active, posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_location_remote ON jobs(location, remote_mode);
CREATE INDEX IF NOT EXISTS idx_candidate_roles_user ON candidate_target_roles(user_id, priority);

CREATE TABLE IF NOT EXISTS recommendation_requests (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_version VARCHAR(80) NOT NULL,
    retrieval_version VARCHAR(80) NOT NULL,
    candidate_count INTEGER NOT NULL,
    returned_count INTEGER NOT NULL,
    latency_ms INTEGER,
    fallback_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recommendation_items (
    request_id VARCHAR(36) NOT NULL REFERENCES recommendation_requests(id) ON DELETE CASCADE,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    position INTEGER NOT NULL,
    retrieval_score DOUBLE PRECISION,
    ranking_score DOUBLE PRECISION,
    PRIMARY KEY (request_id, job_id),
    UNIQUE (request_id, position)
);

CREATE TABLE IF NOT EXISTS interactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_id VARCHAR(36) NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    event_type VARCHAR(20) NOT NULL,
    recommendation_request_id VARCHAR(36) REFERENCES recommendation_requests(id) ON DELETE SET NULL,
    model_version VARCHAR(80),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (event_type IN ('impression', 'click', 'save', 'dismiss', 'apply'))
);

CREATE INDEX IF NOT EXISTS idx_interactions_user_created ON interactions(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_job_created ON interactions(job_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_interactions_event_created ON interactions(event_type, created_at);
CREATE INDEX IF NOT EXISTS idx_recommendation_items_position ON recommendation_items(request_id, position);

CREATE TABLE IF NOT EXISTS model_versions (
    id VARCHAR(36) PRIMARY KEY,
    model_type VARCHAR(80) NOT NULL,
    version VARCHAR(80) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL,
    artifact_path VARCHAR(1000) NOT NULL,
    metrics_json TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activated_at TIMESTAMP
);

