import type { Job } from "../lib/api";

export function JobList({ jobs, emptyTitle, emptyBody }: { jobs: Job[]; emptyTitle: string; emptyBody: string }) {
  if (!jobs.length) return <div className="empty-state"><span className="empty-icon" aria-hidden="true">◌</span><h3>{emptyTitle}</h3><p>{emptyBody}</p></div>;
  return <div className="saved-grid">{jobs.map((job) => <article className="saved-card" key={job.id}><span className="company-mark" aria-hidden="true">{job.company_name.slice(0, 1)}</span><div><h3>{job.title}</h3><p>{job.company_name} · {job.location ?? "Location flexible"}</p><span className="saved-meta">{job.remote_mode ?? "Flexible"} · {job.seniority ?? "All levels"}</span></div></article>)}</div>;
}
