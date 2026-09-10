import { useEffect, useState } from "react";
import { api } from "../services/api";
import { useAuth } from "../context/AuthContext";

const SOURCE_TYPES = [
  "All Sources",
  "Government Grants",
  "Research Councils",
  "Innovation Funds",
  "Startup Accelerators",
  "Venture Programs",
  "International Funding Agencies",
];

function Icon({ name, size = 18 }) {
  const icons = {
    search: (
      <>
        <circle cx="10.8" cy="10.8" r="6.5" />
        <path d="m16 16 5 5" />
      </>
    ),
    dollar: (
      <>
        <line x1="12" y1="1" x2="12" y2="23" />
        <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
      </>
    ),
    bookmark: (
      <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" />
    ),
    sparkles: (
      <>
        <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z" />
      </>
    ),
    bell: (
      <>
        <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
        <path d="M10 21h4" />
      </>
    ),
    plus: (
      <>
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
      </>
    ),
  };

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {icons[name]}
    </svg>
  );
}

export default function Funding() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("all"); // "all" | "recs" | "alerts"
  const [q, setQ] = useState("");
  const [selectedSource, setSelectedSource] = useState("All Sources");

  const [opportunities, setOpportunities] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  // Admin Create Form Modal state
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [newOpp, setNewOpp] = useState({
    title: "",
    description: "",
    source_type: "Government Grants",
    agency: "",
    amount: "$500,000",
    deadline: "2026-12-31",
    eligibility_criteria: "",
    tags_str: "AI, Machine Learning",
    application_url: "",
  });

  // Apply to Grant Modal state
  const [applyModalOpp, setApplyModalOpp] = useState(null);
  const [proposalTitle, setProposalTitle] = useState("");
  const [proposalAbstract, setProposalAbstract] = useState("");

  const openApplyModal = (opp) => {
    setApplyModalOpp(opp);
    setProposalTitle(`Research Proposal: ${opp.title}`);
    setProposalAbstract("");
  };

  const handleSubmission = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (applyModalOpp) {
        await api(`/profile/funding/${applyModalOpp.id}`, { method: "POST" });
      }
      setSuccessMsg(`Application for "${applyModalOpp?.title}" successfully submitted & saved to your profile!`);
      setApplyModalOpp(null);
      setTimeout(() => setSuccessMsg(""), 5000);
    } catch (err) {
      setError(err.message || "Failed to submit application");
    }
  };

  const loadData = async () => {
    setLoading(true);
    setError("");
    try {
      let url = "/funding/opportunities";
      const params = new URLSearchParams();
      if (q.trim()) params.append("q", q.trim());
      if (selectedSource !== "All Sources") params.append("source_type", selectedSource);
      if (params.toString()) url += `?${params.toString()}`;

      const [oppRes, recRes, alertRes] = await Promise.all([
        api(url),
        api("/funding/recommendations"),
        api("/funding/alerts"),
      ]);

      setOpportunities(oppRes || []);
      setRecommendations(recRes || []);
      setAlerts(alertRes || []);
    } catch (e) {
      setError(e.message || "Failed to load funding data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedSource, activeTab]);

  const handleSearch = (e) => {
    e.preventDefault();
    loadData();
  };

  const handleBookmark = async (oppId) => {
    try {
      await api(`/profile/funding/${oppId}`, { method: "POST" });
      setSuccessMsg("Opportunity bookmarked to your research profile!");
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (e) {
      setError(e.message || "Failed to bookmark opportunity");
    }
  };

  const handleCreateOpp = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const tags = newOpp.tags_str
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);

      await api("/funding/opportunities", {
        method: "POST",
        body: JSON.stringify({
          ...newOpp,
          tags,
        }),
      });

      setSuccessMsg("New funding opportunity created successfully!");
      setShowAdminModal(false);
      setNewOpp({
        title: "",
        description: "",
        source_type: "Government Grants",
        agency: "",
        amount: "$500,000",
        deadline: "2026-12-31",
        eligibility_criteria: "",
        tags_str: "AI, Machine Learning",
        application_url: "",
      });
      loadData();
    } catch (e) {
      setError(e.message || "Failed to create opportunity");
    }
  };

  const isAdmin = user?.role === "Administrator";

  return (
    <section>
      {/* PAGE HEADER */}
      <div className="page-head">
        <div>
          <span className="eyebrow">Grant & Capital Intelligence</span>
          <h1>Funding Opportunities</h1>
          <p>
            Discover research grants, innovation funds, and venture programs tailored to your research profile.
          </p>
        </div>

        {isAdmin && (
          <button className="button" onClick={() => setShowAdminModal(true)}>
            <Icon name="plus" size={16} /> Add Opportunity
          </button>
        )}
      </div>

      {/* SUCCESS / ERROR ALERTS */}
      {successMsg && <div className="card success" style={{ marginBottom: 16 }}>{successMsg}</div>}
      {error && <div className="card error" style={{ marginBottom: 16 }}>{error}</div>}

      {/* CONTROLS BAR: SEARCH & SOURCE TYPE FILTER */}
      <form onSubmit={handleSearch} className="search-box" style={{ marginBottom: 20 }}>
        <Icon name="search" />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search grants by keyword, agency, or eligibility..."
        />
        <select
          value={selectedSource}
          onChange={(e) => setSelectedSource(e.target.value)}
          style={{ width: 220, padding: "8px 12px", borderRadius: 6, border: "1px solid #d1d5db" }}
        >
          {SOURCE_TYPES.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
        <button type="submit" className="button">
          Search
        </button>
      </form>

      {/* TABS */}
      <div className="trend-summary" style={{ gridTemplateColumns: "repeat(3, 1fr)", marginBottom: 20 }}>
        <button
          className={`card metric ${activeTab === "all" ? "active" : ""}`}
          style={{ cursor: "pointer", border: activeTab === "all" ? "2px solid #1769e0" : "1px solid #e5e7eb" }}
          onClick={() => setActiveTab("all")}
        >
          <span className="metric-icon" style={{ background: "#eaf2ff", color: "#1769e0" }}>
            <Icon name="dollar" />
          </span>
          <strong>All Opportunities</strong>
          <small>{opportunities.length} active programs</small>
        </button>

        <button
          className={`card metric ${activeTab === "recs" ? "active" : ""}`}
          style={{ cursor: "pointer", border: activeTab === "recs" ? "2px solid #1769e0" : "1px solid #e5e7eb" }}
          onClick={() => setActiveTab("recs")}
        >
          <span className="metric-icon" style={{ background: "#f1ecff", color: "#7356d8" }}>
            <Icon name="sparkles" />
          </span>
          <strong>Recommendations</strong>
          <small>Profile match scoring</small>
        </button>

        <button
          className={`card metric ${activeTab === "alerts" ? "active" : ""}`}
          style={{ cursor: "pointer", border: activeTab === "alerts" ? "2px solid #1769e0" : "1px solid #e5e7eb" }}
          onClick={() => setActiveTab("alerts")}
        >
          <span className="metric-icon" style={{ background: "#fff2e8", color: "#d97706" }}>
            <Icon name="bell" />
          </span>
          <strong>Funding Alerts</strong>
          <small>{alerts.length} high-priority matches</small>
        </button>
      </div>

      {/* CONTENT PANELS */}
      {loading ? (
        <div className="card state">Loading funding opportunities…</div>
      ) : activeTab === "all" ? (
        <div className="stack">
          {opportunities.length === 0 ? (
            <div className="card state">No funding opportunities found matching your criteria.</div>
          ) : (
            opportunities.map((opp) => (
              <OpportunityCard
                key={opp.id}
                item={opp}
                onBookmark={() => handleBookmark(opp.id)}
                onApply={() => openApplyModal(opp)}
              />
            ))
          )}
        </div>
      ) : activeTab === "recs" ? (
        <div className="stack">
          {recommendations.length === 0 ? (
            <div className="card state">No personalized recommendations calculated yet. Complete your profile research interests.</div>
          ) : (
            recommendations.map((rec) => (
              <OpportunityCard
                key={rec.opportunity.id}
                item={rec.opportunity}
                matchScore={rec.match_score}
                matchedTags={rec.matched_tags}
                onBookmark={() => handleBookmark(rec.opportunity.id)}
                onApply={() => openApplyModal(rec.opportunity)}
              />
            ))
          )}
        </div>
      ) : (
        <div className="stack">
          {alerts.length === 0 ? (
            <div className="card state">No funding alerts active currently.</div>
          ) : (
            alerts.map((rec) => (
              <OpportunityCard
                key={rec.opportunity.id}
                item={rec.opportunity}
                matchScore={rec.match_score}
                matchedTags={rec.matched_tags}
                isAlert
                onBookmark={() => handleBookmark(rec.opportunity.id)}
                onApply={() => openApplyModal(rec.opportunity)}
              />
            ))
          )}
        </div>
      )}

      {/* APPLY TO GRANT MODAL */}
      {applyModalOpp && (
        <div className="modal-backdrop" style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.6)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 100 }}>
          <div className="card" style={{ width: 560, maxHeight: "90vh", overflowY: "auto" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <span className="eyebrow">{applyModalOpp.source_type}</span>
                <h2 style={{ margin: "4px 0 8px" }}>{applyModalOpp.title}</h2>
                <p className="muted" style={{ margin: 0, fontSize: 13 }}>
                  Provider: <strong>{applyModalOpp.agency}</strong> · Maximum Funding: <strong style={{ color: "#2563eb" }}>{applyModalOpp.amount}</strong>
                </p>
              </div>
            </div>

            <hr style={{ border: 0, borderTop: "1px solid var(--border)", margin: "16px 0" }} />

            <form onSubmit={handleSubmission} className="form-grid" style={{ gridTemplateColumns: "1fr" }}>
              <label>
                Lead Principal Investigator / Applicant
                <input readOnly value={user?.full_name ? `${user.full_name} (${user.email})` : "Current Researcher"} style={{ background: "var(--hover-bg)" }} />
              </label>

              <label>
                Proposal Title
                <input
                  required
                  value={proposalTitle}
                  onChange={(e) => setProposalTitle(e.target.value)}
                  placeholder="Enter title of your proposed research project..."
                />
              </label>

              <label>
                Project Executive Summary / Abstract
                <textarea
                  required
                  rows={4}
                  value={proposalAbstract}
                  onChange={(e) => setProposalAbstract(e.target.value)}
                  placeholder="Describe your research methodology, expected innovation impact, and alignment with grant criteria..."
                />
              </label>

              <div style={{ display: "flex", gap: 12, justifyContent: "space-between", alignItems: "center", marginTop: 12 }}>
                {applyModalOpp.application_url && (
                  <a
                    href={applyModalOpp.application_url.startsWith("http") ? applyModalOpp.application_url : `https://${applyModalOpp.application_url}`}
                    target="_blank"
                    rel="noreferrer"
                    className="button secondary"
                    style={{ fontSize: 12 }}
                  >
                    Official Agency Portal ↗
                  </a>
                )}
                <div style={{ display: "flex", gap: 10 }}>
                  <button type="button" className="button secondary" onClick={() => setApplyModalOpp(null)}>
                    Cancel
                  </button>
                  <button type="submit" className="button">
                    Submit Application
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      )}
    </section>
  );
}

function OpportunityCard({ item, matchScore, matchedTags, isAlert, onBookmark, onApply }) {
  const safeUrl = item.application_url
    ? item.application_url.startsWith("http")
      ? item.application_url
      : `https://${item.application_url}`
    : "https://www.grants.gov";

  return (
    <article className="card funding-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 16 }}>
        <div>
          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6 }}>
            <span className="chip hot">{item.source_type}</span>
            {matchScore !== undefined && (
              <span className="chip" style={{ background: "rgba(34, 197, 94, 0.12)", color: "var(--green)", fontWeight: 700 }}>
                {matchScore}% Profile Match
              </span>
            )}
            {isAlert && (
              <span className="chip" style={{ background: "rgba(245, 158, 11, 0.12)", color: "var(--amber)", fontWeight: 700 }}>
                Deadline Alert
              </span>
            )}
          </div>

          <h3 className="result-title" style={{ marginTop: 4 }}>{item.title}</h3>

          <div className="meta" style={{ marginTop: 4 }}>
            <span><strong>Agency:</strong> {item.agency}</span>
            <span>·</span>
            <span className="accent"><strong>Funding:</strong> {item.amount}</span>
            <span>·</span>
            <span><strong>Deadline:</strong> {item.deadline}</span>
          </div>

          <p style={{ marginTop: 8 }}>{item.description}</p>

          {item.eligibility_criteria && (
            <p className="muted" style={{ fontSize: "0.85rem", marginTop: 4 }}>
              <strong>Eligibility:</strong> {item.eligibility_criteria}
            </p>
          )}

          <div className="chips" style={{ marginTop: 10 }}>
            {item.tags?.map((tag, i) => (
              <span
                className="chip"
                key={i}
                style={{
                  background: matchedTags?.includes(tag.toLowerCase()) ? "var(--blue-light)" : "var(--hover-bg)",
                  color: matchedTags?.includes(tag.toLowerCase()) ? "var(--blue)" : "var(--muted)",
                  fontWeight: matchedTags?.includes(tag.toLowerCase()) ? 700 : 400,
                }}
              >
                #{tag}
              </span>
            ))}
          </div>
        </div>

        <div className="result-actions" style={{ flexDirection: "column", gap: 8, minWidth: 100 }}>
          <button className="button" onClick={onApply} title="Apply to this funding program">
            Apply Now
          </button>
          <button className="button secondary" onClick={onBookmark} title="Save to profile">
            <Icon name="bookmark" size={14} /> Bookmark
          </button>
          <a
            href={safeUrl}
            target="_blank"
            rel="noreferrer"
            className="muted"
            style={{ fontSize: 11, textAlign: "center", marginTop: 2, textDecoration: "underline" }}
          >
            Agency Portal ↗
          </a>
        </div>
      </div>
    </article>
  );
}
