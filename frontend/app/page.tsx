"use client";

import { FormEvent, useEffect, useState } from "react";

type Job = { id: string; title: string; company_name: string; location: string | null; remote_mode: string | null; description: string };
type JobResponse = { items: Job[]; total: number };

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("Loading jobs…");

  async function loadJobs(location = "") {
    setStatus("Loading jobs…");
    const params = location ? `?location=${encodeURIComponent(location)}` : "";
    try {
      const response = await fetch(`${API_URL}/api/v1/jobs${params}`);
      if (!response.ok) throw new Error("Jobs request failed");
      const data = (await response.json()) as JobResponse;
      setJobs(data.items);
      setStatus(`${data.total} active jobs`);
    } catch {
      setStatus("Backend unavailable. Start the API and try again.");
    }
  }

  useEffect(() => { void loadJobs(); }, []);

  function submit(event: FormEvent) {
    event.preventDefault();
    void loadJobs(query.trim());
  }

  return (
    <main className="shell">
      <nav className="nav"><span className="brand">TalentMatch</span><span>Jobs · Profile</span></nav>
      <section className="content">
        <div className="intro"><h1>Jobs ranked for you.</h1><p>Build a profile, explore relevant work, and give the system feedback as you go.</p></div>
        <form className="toolbar" onSubmit={submit}><input aria-label="Filter jobs by location" placeholder="Filter by location" value={query} onChange={(event) => setQuery(event.target.value)} /><button type="submit">Search</button></form>
        <p className="status">{status}</p>
        <div className="jobs">{jobs.map((job) => <article className="job" key={job.id}><h2>{job.title}</h2><div className="job-meta">{job.company_name} · {job.location ?? "Location not listed"} · {job.remote_mode ?? "work mode not listed"}</div><p>{job.description}</p></article>)}</div>
      </section>
    </main>
  );
}

