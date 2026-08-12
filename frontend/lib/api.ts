export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Profile = {
  user_id: string;
  current_title: string | null;
  target_roles: string[];
  skills: string[];
  years_experience: number | null;
  location: string | null;
  remote_preference: "onsite" | "hybrid" | "remote" | "any" | null;
  minimum_salary: number | null;
  salary_currency: string | null;
};

export type Job = {
  id: string;
  title: string;
  company_name: string;
  description: string;
  location: string | null;
  remote_mode: string | null;
  seniority: string | null;
  employment_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  source_url: string | null;
  posted_at: string | null;
};

export type JobList = { items: Job[]; page: number; page_size: number; total: number };

export type Recommendation = {
  position: number;
  job_id: string;
  title: string;
  company: string;
  location: string | null;
  remote_mode: string | null;
  score: number;
  match_reasons: string[];
};

export type RecommendationResponse = {
  recommendation_request_id: string;
  model_version: string;
  retrieval_version: string;
  feature_schema_version: string;
  items: Recommendation[];
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options?.headers ?? {}) },
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => null) as { detail?: string } | null;
    throw new Error(detail?.detail ?? "The request could not be completed.");
  }
  return response.json() as Promise<T>;
}

export function getProfile() { return request<Profile>("/api/v1/profile"); }

export function updateProfile(payload: Partial<Profile>) {
  return request<Profile>("/api/v1/profile", { method: "PATCH", body: JSON.stringify(payload) });
}

export function getRecommendations() { return request<RecommendationResponse>("/api/v1/recommendations?limit=20"); }

export function getJob(jobId: string) { return request<Job>(`/api/v1/jobs/${jobId}`); }

export function getSavedJobs() { return request<JobList>("/api/v1/saved-jobs"); }

export function getApplications() { return request<JobList>("/api/v1/applications"); }

export function recordInteraction(jobId: string, eventType: "click" | "save" | "dismiss" | "apply", requestId: string) {
  return request<{ id: string }>("/api/v1/interactions", {
    method: "POST",
    body: JSON.stringify({ job_id: jobId, event_type: eventType, recommendation_request_id: requestId }),
  });
}
