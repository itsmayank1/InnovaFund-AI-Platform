import { useState, useEffect } from "react";
import { getProfile, saveProfile } from "../services/api";

function Profile({ token, onLogout }) {
  const [domains, setDomains] = useState("");
  const [keywords, setKeywords] = useState("");
  const [publications, setPublications] = useState("");
  const [technologyAreas, setTechnologyAreas] = useState("");
  const [organization, setOrganization] = useState("");
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await getProfile(token);
        const p = res.data;
        setDomains((p.research_domains || []).join(", "));
        setKeywords((p.keywords || []).join(", "));
        setPublications((p.publications || []).join(", "));
        setTechnologyAreas((p.technology_areas || []).join(", "));
        setOrganization(p.organization || "");
      } catch (err) {
        // No profile yet
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, [token]);

  const toList = (str) =>
    str.split(",").map((s) => s.trim()).filter((s) => s.length > 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage("");
    try {
      await saveProfile(
        {
          research_domains: toList(domains),
          keywords: toList(keywords),
          publications: toList(publications),
          patents: [],
          technology_areas: toList(technologyAreas),
          organization,
        },
        token
      );
      setMessage("Profile saved successfully!");
    } catch (err) {
      setMessage("Failed to save profile.");
    }
  };

  return (
    <div className="dashboard-body">
      <nav className="navbar">
        <div className="navbar-logo">InnovaFund</div>
        <div className="navbar-actions">
          <button onClick={onLogout}>Logout</button>
        </div>
      </nav>

      <div className="page-content">
        <div className="page-title">Research Profile</div>
        <div className="page-subtitle">Keep your research identity up to date</div>

        <div className="profile-card">
          {loading ? (
            <p>Loading profile...</p>
          ) : (
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group full-width">
                  <label>Organization</label>
                  <input
                    type="text"
                    value={organization}
                    onChange={(e) => setOrganization(e.target.value)}
                    placeholder="Dayananda Sagar University"
                  />
                </div>
                <div className="form-group">
                  <label>Research Domains</label>
                  <input
                    type="text"
                    value={domains}
                    onChange={(e) => setDomains(e.target.value)}
                    placeholder="Artificial Intelligence, NLP"
                  />
                </div>
                <div className="form-group">
                  <label>Keywords</label>
                  <input
                    type="text"
                    value={keywords}
                    onChange={(e) => setKeywords(e.target.value)}
                    placeholder="transformers, trend detection"
                  />
                </div>
                <div className="form-group">
                  <label>Publications</label>
                  <input
                    type="text"
                    value={publications}
                    onChange={(e) => setPublications(e.target.value)}
                    placeholder="Paper title one, Paper title two"
                  />
                </div>
                <div className="form-group">
                  <label>Technology Areas</label>
                  <input
                    type="text"
                    value={technologyAreas}
                    onChange={(e) => setTechnologyAreas(e.target.value)}
                    placeholder="Machine Learning, Cloud Computing"
                  />
                </div>
              </div>
              <button type="submit" className="btn-primary" style={{ marginTop: 8, maxWidth: 200 }}>
                Save Profile
              </button>
            </form>
          )}

          {message && (
            <p className={message.includes("success") ? "success-msg" : "error-msg"}>
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Profile;