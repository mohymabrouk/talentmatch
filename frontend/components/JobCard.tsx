"use client";

import type { Recommendation } from "../lib/api";

type Props = {
  item: Recommendation;
  onSelect: () => void;
  onAction: (eventType: "click" | "save" | "dismiss" | "apply") => void;
};

export function JobCard({ item, onSelect, onAction }: Props) {
  return (
    <article className="job-card">
      <div className="job-card-topline">
        <span className="eyebrow">#{String(item.position).padStart(2, "0")}</span>
        <span className="score">{Math.round(item.score * 100)}% match</span>
      </div>
      <button className="job-card-heading" type="button" onClick={onSelect} aria-label={`View ${item.title}`}>
        <span className="company-mark" aria-hidden="true">{item.company.slice(0, 1)}</span>
        <span><strong>{item.title}</strong><small>{item.company}</small></span>
      </button>
      <p className="job-location">{item.location ?? "Location flexible"} <span>·</span> {item.remote_mode ?? "Work mode flexible"}</p>
      <div className="reason-row">{item.match_reasons.map((reason) => <span className="reason" key={reason}>{reason}</span>)}</div>
      <div className="card-actions" aria-label={`${item.title} actions`}>
        <button className="button button-quiet" type="button" onClick={() => { onAction("click"); onSelect(); }}>View details</button>
        <button className="icon-button" type="button" onClick={() => onAction("save")} aria-label={`Save ${item.title}`}>♡</button>
        <button className="icon-button" type="button" onClick={() => onAction("dismiss")} aria-label={`Dismiss ${item.title}`}>×</button>
      </div>
    </article>
  );
}
