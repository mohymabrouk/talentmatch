"use client";

import { FormEvent, useState } from "react";

type Recommendation = { position: number; job_id: string; title: string; company: string; location: string | null; remote_mode: string | null; score: number; match_reasons: string[] };
type RecommendationResponse = { recommendation_request_id: string; items: Recommendation[] };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [requestId, setRequestId] = useState("");
  const [role, setRole] = useState("Machine Learning Engineer");
  const [skills, setSkills] = useState("Python, PyTorch, FastAPI");
  const [status, setStatus] = useState("Create a profile to load recommendations.");

  async function loadRecommendations() {
    setStatus("Loading recommendations…");
    try {
      const response = await fetch(`${API_URL}/api/v1/recommendations?limit=20`);
      if (!response.ok) throw new Error("Recommendations request failed");
      const data = (await response.json()) as RecommendationResponse;
      setRecommendations(data.items);
      setRequestId(data.recommendation_request_id);
      setStatus(`${data.items.length} recommendations`);
    } catch {
      setStatus("Backend unavailable. Start the API and try again.");
    }
  }

  async function saveProfile() {
    setStatus("Saving profile…");
    const response = await fetch(`${API_URL}/api/v1/profile`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target_roles: [role], skills: skills.split(",").map((skill) => skill.trim()).filter(Boolean), remote_preference: "any" }) });
    if (!response.ok) { setStatus("Profile could not be saved."); return; }
    await loadRecommendations();
  }

  async function recordInteraction(jobId: string, eventType: "click" | "save" | "dismiss" | "apply") {
    const response = await fetch(`${API_URL}/api/v1/interactions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ job_id: jobId, event_type: eventType, recommendation_request_id: requestId }) });
    if (!response.ok) { setStatus("Feedback could not be recorded."); return; }
    setStatus(`${eventType} recorded`);
    if (eventType === "dismiss") setRecommendations((items) => items.filter((item) => item.job_id !== jobId));
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    void saveProfile();
  }

  return (
    <main className="shell">
      <nav className="nav"><span className="brand">TalentMatch</span><span>Jobs · Profile</span></nav>
      <section className="content">
        <div className="intro"><h1>Jobs ranked for you.</h1><p>Build a profile, explore relevant work, and give the system feedback as you go.</p></div>
        <form className="toolbar" onSubmit={submit}><input aria-label="Target role" placeholder="Target role" value={role} onChange={(event) => setRole(event.target.value)} /><input aria-label="Skills" placeholder="Skills, comma separated" value={skills} onChange={(event) => setSkills(event.target.value)} /><button type="submit">Recommend</button></form>
        <p className="status">{status}</p>
        <div className="jobs">{recommendations.map((item) => <article className="job" key={item.job_id}><h2>{item.position}. {item.title}</h2><div className="job-meta">{item.company} · {item.location ?? "Location not listed"} · {item.remote_mode ?? "work mode not listed"} · {Math.round(item.score * 100)}% match</div><p>{item.match_reasons.join(" · ")}</p><div className="actions"><button type="button" onClick={() => void recordInteraction(item.job_id, "click")}>Open</button><button type="button" onClick={() => void recordInteraction(item.job_id, "save")}>Save</button><button type="button" onClick={() => void recordInteraction(item.job_id, "apply")}>Apply</button><button type="button" onClick={() => void recordInteraction(item.job_id, "dismiss")}>Dismiss</button></div></article>)}</div>
      </section>
    </main>
  );
}
