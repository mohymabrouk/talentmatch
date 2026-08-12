"use client";

import { useEffect, useState } from "react";
import { getJob, recordInteraction, type Job, type Recommendation } from "../lib/api";

type Props = { item: Recommendation; requestId: string; onClose: () => void; onFeedback: (message: string) => void };

export function JobDetail({ item, requestId, onClose, onFeedback }: Props) {
  const [job, setJob] = useState<Job | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    void getJob(item.job_id).then(setJob).catch((reason: Error) => setError(reason.message));
  }, [item.job_id]);

  async function apply() {
    try { await recordInteraction(item.job_id, "apply", requestId); onFeedback("Application marked"); }
    catch (reason) { onFeedback(reason instanceof Error ? reason.message : "Could not record application"); }
  }

  return (
    <div className="detail-backdrop" role="presentation" onMouseDown={(event) => { if (event.currentTarget === event.target) onClose(); }}>
      <aside className="detail-panel" role="dialog" aria-modal="true" aria-labelledby="detail-title">
        <button className="close-button" type="button" onClick={onClose} aria-label="Close job details">×</button>
        <span className="kicker">Recommended for you</span>
        <h2 id="detail-title">{item.title}</h2>
        <p className="detail-company">{item.company} · {item.location ?? "Location flexible"}</p>
        <div className="reason-row">{item.match_reasons.map((reason) => <span className="reason" key={reason}>{reason}</span>)}</div>
        {error ? <div className="inline-error" role="alert">{error}</div> : !job ? <div className="detail-loading" role="status">Loading job details…</div> : <>
          <div className="detail-facts"><span>{job.remote_mode ?? "Flexible"}</span><span>{job.seniority ?? "All levels"}</span><span>{job.employment_type ?? "Full-time"}</span></div>
          <p className="detail-description">{job.description}</p>
          {job.salary_min || job.salary_max ? <p className="salary">{job.salary_currency} {job.salary_min?.toLocaleString()} – {job.salary_max?.toLocaleString()}</p> : null}
          <div className="detail-actions"><button className="button button-primary" type="button" onClick={() => void apply()}>Mark as applied</button>{job.source_url ? <a className="button button-secondary" href={job.source_url} target="_blank" rel="noreferrer">Open original <span aria-hidden="true">↗</span></a> : null}</div>
        </>}
      </aside>
    </div>
  );
}
