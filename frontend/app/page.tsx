"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { JobCard } from "../components/JobCard";
import { JobDetail } from "../components/JobDetail";
import { JobList } from "../components/JobList";
import { getApplications, getProfile, getRecommendations, getSavedJobs, recordInteraction, updateProfile, type Job, type Profile, type Recommendation } from "../lib/api";

type View = "discover" | "saved" | "applications" | "profile";

const defaultProfile: Profile = {
  user_id: "", current_title: null, target_roles: ["Machine Learning Engineer"], skills: ["Python", "PyTorch", "FastAPI"],
  years_experience: null, location: null, remote_preference: "any", minimum_salary: null, salary_currency: "EUR",
};

export default function Home() {
  const [view, setView] = useState<View>("discover");
  const [profile, setProfile] = useState<Profile>(defaultProfile);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [saved, setSaved] = useState<Job[]>([]);
  const [applications, setApplications] = useState<Job[]>([]);
  const [requestId, setRequestId] = useState("");
  const [selected, setSelected] = useState<Recommendation | null>(null);
  const [remoteFilter, setRemoteFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("Loading your workspace…");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    void Promise.allSettled([getProfile(), getRecommendations()]).then(([profileResult, recommendationResult]) => {
      if (profileResult.status === "fulfilled") setProfile(profileResult.value);
      if (recommendationResult.status === "fulfilled") {
        setRecommendations(recommendationResult.value.items); setRequestId(recommendationResult.value.recommendation_request_id); setStatus(`${recommendationResult.value.items.length} roles matched to your profile`);
      } else setStatus("Set up your profile to start discovering roles.");
    }).finally(() => setLoading(false));
  }, []);

  const filteredRecommendations = useMemo(() => recommendations.filter((item) => {
    const matchesSearch = !search || `${item.title} ${item.company} ${item.location ?? ""}`.toLowerCase().includes(search.toLowerCase());
    const matchesRemote = remoteFilter === "all" || item.remote_mode === remoteFilter;
    return matchesSearch && matchesRemote;
  }), [recommendations, remoteFilter, search]);

  async function refreshRecommendations() {
    setLoading(true); setError("");
    try { const response = await getRecommendations(); setRecommendations(response.items); setRequestId(response.recommendation_request_id); setStatus(`${response.items.length} roles matched to your profile`); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Recommendations could not be loaded."); }
    finally { setLoading(false); }
  }

  async function saveProfile(event: FormEvent) {
    event.preventDefault(); setSaving(true); setError("");
    try {
      const nextProfile = await updateProfile({ current_title: profile.current_title, target_roles: profile.target_roles, skills: profile.skills, years_experience: profile.years_experience, location: profile.location, remote_preference: profile.remote_preference, minimum_salary: profile.minimum_salary, salary_currency: profile.salary_currency });
      setProfile(nextProfile); setView("discover"); await refreshRecommendations();
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Profile could not be saved."); }
    finally { setSaving(false); }
  }

  async function openSaved() { setView("saved"); try { setSaved((await getSavedJobs()).items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Saved roles could not be loaded."); } }
  async function openApplications() { setView("applications"); try { setApplications((await getApplications()).items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Applications could not be loaded."); } }

  async function action(item: Recommendation, eventType: "click" | "save" | "dismiss" | "apply") {
    try {
      await recordInteraction(item.job_id, eventType, requestId);
      if (eventType === "dismiss") setRecommendations((items) => items.filter((candidate) => candidate.job_id !== item.job_id));
      if (eventType === "save") setStatus("Saved to your list");
      if (eventType === "apply") setStatus("Application marked");
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Feedback could not be recorded."); }
  }

  function updateProfileField(field: keyof Profile, value: string | string[]) { setProfile((current) => ({ ...current, [field]: value })); }

  return (
    <main className="app-shell">
      <header className="topbar"><button className="wordmark" type="button" onClick={() => setView("discover")} aria-label="Go to discovery"><span className="wordmark-dot" />TalentMatch</button><nav className="topnav" aria-label="Primary navigation"><button className={view === "discover" ? "active" : ""} type="button" onClick={() => setView("discover")}>Discover</button><button className={view === "saved" ? "active" : ""} type="button" onClick={() => void openSaved()}>Saved <span className="nav-count">{saved.length || ""}</span></button><button className={view === "applications" ? "active" : ""} type="button" onClick={() => void openApplications()}>Applications</button></nav><button className="avatar" type="button" onClick={() => setView("profile")} aria-label="Open profile">{(profile.target_roles[0] ?? "T").slice(0, 1)}</button></header>
      <div className="page-wrap">
        {error ? <div className="alert" role="alert"><span>{error}</span><button type="button" onClick={() => setError("")} aria-label="Dismiss error">×</button></div> : null}
        {view === "discover" ? <>
          <section className="hero"><div><span className="kicker">Your next move</span><h1>Find work that <em>fits.</em></h1><p>Thoughtful matches for the work you want to do next.</p></div><button className="button button-secondary desktop-refresh" type="button" onClick={() => void refreshRecommendations()}>Refresh matches <span aria-hidden="true">↻</span></button></section>
          <section className="workspace-bar"><div className="match-summary"><span className="pulse" />{loading ? "Finding your best matches" : status}</div><div className="filters"><label className="search-field"><span aria-hidden="true">⌕</span><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search roles or companies" aria-label="Search roles or companies" /></label><label className="select-field"><span className="sr-only">Work mode</span><select value={remoteFilter} onChange={(event) => setRemoteFilter(event.target.value)}><option value="all">All work modes</option><option value="remote">Remote</option><option value="hybrid">Hybrid</option><option value="onsite">On-site</option></select></label></div></section>
          {loading ? <div className="skeleton-list" aria-label="Loading recommendations"><div /><div /><div /></div> : filteredRecommendations.length ? <div className="recommendation-grid">{filteredRecommendations.map((item) => <JobCard item={item} key={item.job_id} onSelect={() => setSelected(item)} onAction={(eventType) => void action(item, eventType)} />)}</div> : <div className="empty-state"><span className="empty-icon" aria-hidden="true">⌕</span><h3>No matches here yet</h3><p>Try another search or update your profile preferences.</p><button className="button button-primary" type="button" onClick={() => setView("profile")}>Update profile</button></div>}
        </> : null}
        {view === "saved" ? <section className="subpage"><span className="kicker">Your shortlist</span><h1>Saved roles</h1><p className="subcopy">The opportunities you want to come back to.</p><JobList jobs={saved} emptyTitle="Your shortlist is empty" emptyBody="Save roles from Discover and they will appear here." /></section> : null}
        {view === "applications" ? <section className="subpage"><span className="kicker">Your progress</span><h1>Applications</h1><p className="subcopy">Keep track of the roles you have moved forward with.</p><JobList jobs={applications} emptyTitle="No applications yet" emptyBody="When you mark a role as applied, we will keep it here." /></section> : null}
        {view === "profile" ? <section className="subpage profile-page"><span className="kicker">Make it yours</span><h1>Your profile</h1><p className="subcopy">A little context helps us make better matches.</p><form className="profile-form" onSubmit={saveProfile}><label>Target role<input value={profile.target_roles.join(", ")} onChange={(event) => updateProfileField("target_roles", event.target.value.split(",").map((value) => value.trim()).filter(Boolean))} /></label><label>Skills <span className="label-note">comma separated</span><input value={profile.skills.join(", ")} onChange={(event) => updateProfileField("skills", event.target.value.split(",").map((value) => value.trim()).filter(Boolean))} /></label><div className="form-row"><label>Location<input value={profile.location ?? ""} onChange={(event) => updateProfileField("location", event.target.value)} placeholder="Paris, France" /></label><label>Years of experience<input type="number" min="0" max="80" value={profile.years_experience ?? ""} onChange={(event) => updateProfileField("years_experience", event.target.value)} placeholder="3" /></label></div><fieldset><legend>Work preference</legend><div className="choice-grid">{["any", "remote", "hybrid", "onsite"].map((option) => <label className={`choice ${profile.remote_preference === option ? "selected" : ""}`} key={option}><input type="radio" name="remote" value={option} checked={profile.remote_preference === option} onChange={() => updateProfileField("remote_preference", option)} />{option === "any" ? "Open to anything" : option.charAt(0).toUpperCase() + option.slice(1)}</label>)}</div></fieldset><button className="button button-primary" type="submit" disabled={saving}>{saving ? "Saving…" : "Save profile & find matches"}</button></form></section> : null}
      </div>
      {selected ? <JobDetail item={selected} requestId={requestId} onClose={() => setSelected(null)} onFeedback={setStatus} /> : null}
    </main>
  );
}
