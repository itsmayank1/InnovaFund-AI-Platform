import React, { useState, useEffect, useMemo } from 'react';
import { getRecommendations, generateRecommendations } from '../api/recommendations';
import { useAuth } from '../context/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import GrantDetailsModal from '../components/GrantDetailsModal';
import {
  HiSparkles, HiCurrencyDollar, HiCalendar, HiExclamationCircle,
  HiSearch, HiSortAscending, HiBookmark, HiOutlineBookmark, HiExternalLink,
} from 'react-icons/hi';

const BOOKMARK_KEY = 'innovafund_bookmarked_grants';

export default function RecommendationsPage() {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);
  const [needsGeneration, setNeedsGeneration] = useState(false);
  const [eligibleOnly, setEligibleOnly] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('score_desc');
  const [selectedGrant, setSelectedGrant] = useState(null);
  const [bookmarked, setBookmarked] = useState(() => {
    try { return JSON.parse(localStorage.getItem(BOOKMARK_KEY) || '[]'); } catch { return []; }
  });

  const researcherId = user?.id;

  useEffect(() => {
    if (researcherId) loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [researcherId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    setNeedsGeneration(false);
    try {
      const data = await getRecommendations(researcherId);
      setRecommendations(data || []);
    } catch (err) {
      if (err.response?.status === 404) {
        setNeedsGeneration(true);
      } else {
        console.error(err);
        setError('Unable to load funding recommendations right now. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError(null);
    try {
      const data = await generateRecommendations(researcherId, 10);
      setRecommendations(data || []);
      setNeedsGeneration(false);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 404) {
        setError('No research profile found — please complete your Research Profile first.');
      } else {
        setError('Could not generate recommendations right now. Please try again.');
      }
    } finally {
      setGenerating(false);
    }
  };

  const toggleBookmark = (id) => {
    setBookmarked((prev) => {
      const next = prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
      localStorage.setItem(BOOKMARK_KEY, JSON.stringify(next));
      return next;
    });
  };

  const processed = useMemo(() => {
    let list = eligibleOnly ? recommendations.filter((r) => r.eligible) : recommendations;

    if (searchTerm.trim()) {
      const q = searchTerm.trim().toLowerCase();
      list = list.filter(
        (r) => r.title?.toLowerCase().includes(q) || r.agency?.toLowerCase().includes(q)
      );
    }

    const sorted = [...list];
    switch (sortBy) {
      case 'score_desc': sorted.sort((a, b) => b.score - a.score); break;
      case 'score_asc': sorted.sort((a, b) => a.score - b.score); break;
      case 'amount_desc': sorted.sort((a, b) => (b.amount || 0) - (a.amount || 0)); break;
      case 'deadline_asc': sorted.sort((a, b) => new Date(a.deadline || 0) - new Date(b.deadline || 0)); break;
      default: break;
    }
    return sorted;
  }, [recommendations, eligibleOnly, searchTerm, sortBy]);

  const stats = useMemo(() => {
    const eligibleCount = recommendations.filter((r) => r.eligible).length;
    const totalValue = recommendations.reduce((sum, r) => sum + (r.amount || 0), 0);
    const avgScore = recommendations.length
      ? Math.round(recommendations.reduce((sum, r) => sum + (r.score || 0), 0) / recommendations.length)
      : 0;
    return { eligibleCount, totalValue, avgScore };
  }, [recommendations]);

  const scoreColor = (score) => (score >= 70 ? '#10b981' : score >= 40 ? '#f59e0b' : '#f87171');

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }} className="animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: '#38bdf8', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.4rem' }}>
          <HiSparkles /> AI Funding Match Engine
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: '800', margin: '0 0 0.5rem 0', background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Funding Recommendations
        </h1>
        <p style={{ color: '#94a3b8', margin: 0, fontSize: '0.95rem' }}>
          AI-ranked funding opportunities matched to your research profile.
        </p>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : needsGeneration ? (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center' }}>
          <HiSparkles style={{ fontSize: '2rem', color: '#38bdf8', marginBottom: '0.75rem' }} />
          <p style={{ color: '#cbd5e1', marginBottom: '1.5rem' }}>
            You haven't generated funding recommendations yet.
          </p>
          {error && <p style={{ color: '#f87171', marginBottom: '1rem' }}>{error}</p>}
          <button className="btn-primary" onClick={handleGenerate} disabled={generating}>
            {generating ? 'Generating...' : 'Generate Recommendations'}
          </button>
        </div>
      ) : error ? (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#f87171' }}>
          <HiExclamationCircle style={{ fontSize: '2rem', marginBottom: '0.75rem' }} />
          <p>{error}</p>
        </div>
      ) : (
        <>
          {/* Stats bar */}
          {recommendations.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
              <div className="glass-card" style={{ padding: '1.25rem 1.5rem' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Eligible Grants</div>
                <div style={{ color: '#10b981', fontSize: '1.6rem', fontWeight: '800' }}>{stats.eligibleCount} / {recommendations.length}</div>
              </div>
              <div className="glass-card" style={{ padding: '1.25rem 1.5rem' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Total Potential Value</div>
                <div style={{ color: '#f8fafc', fontSize: '1.6rem', fontWeight: '800' }}>${stats.totalValue.toLocaleString()}</div>
              </div>
              <div className="glass-card" style={{ padding: '1.25rem 1.5rem' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Average Score</div>
                <div style={{ color: '#38bdf8', fontSize: '1.6rem', fontWeight: '800' }}>{stats.avgScore}</div>
              </div>
              <div className="glass-card" style={{ padding: '1.25rem 1.5rem' }}>
                <div style={{ color: '#94a3b8', fontSize: '0.8rem' }}>Bookmarked</div>
                <div style={{ color: '#facc15', fontSize: '1.6rem', fontWeight: '800' }}>{bookmarked.length}</div>
              </div>
            </div>
          )}

          {/* Filter / search / sort bar */}
          <div className="glass-card" style={{ padding: '1.25rem 1.5rem', marginBottom: '2rem', display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: '1rem' }}>
            <div style={{ position: 'relative', flex: '1 1 220px' }}>
              <HiSearch style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8' }} />
              <input
                type="text"
                className="glass-input"
                style={{ width: '100%', boxSizing: 'border-box', paddingLeft: '2.5rem' }}
                placeholder="Search by title or agency..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#cbd5e1', fontSize: '0.85rem', cursor: 'pointer' }}>
              <input type="checkbox" checked={eligibleOnly} onChange={(e) => setEligibleOnly(e.target.checked)} />
              Eligible only
            </label>

            <HiSortAscending style={{ color: '#94a3b8' }} />
            <select className="glass-input" value={sortBy} onChange={(e) => setSortBy(e.target.value)} style={{ minWidth: '190px' }}>
              <option value="score_desc" style={{ background: '#030712' }}>Best Score First</option>
              <option value="score_asc" style={{ background: '#030712' }}>Lowest Score First</option>
              <option value="amount_desc" style={{ background: '#030712' }}>Highest Amount First</option>
              <option value="deadline_asc" style={{ background: '#030712' }}>Deadline Soonest</option>
            </select>

            <button className="btn-outline" onClick={handleGenerate} disabled={generating} style={{ marginLeft: 'auto' }}>
              {generating ? 'Refreshing...' : 'Regenerate'}
            </button>
          </div>

          {processed.length === 0 ? (
            <div className="glass-card" style={{ padding: '4rem', textAlign: 'center', color: '#94a3b8' }}>
              No recommendations match your filters.
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '1.75rem' }}>
              {processed.map((rec) => {
                const isBookmarked = bookmarked.includes(rec.opportunity_id);
                return (
                  <div key={rec.opportunity_id} className="glass-card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                        <span style={{
                          color: rec.eligible ? '#10b981' : '#f87171',
                          background: rec.eligible ? 'rgba(16,185,129,0.12)' : 'rgba(248,113,113,0.12)',
                          border: `1px solid ${rec.eligible ? 'rgba(16,185,129,0.3)' : 'rgba(248,113,113,0.3)'}`,
                          padding: '0.2rem 0.6rem', borderRadius: '0.5rem', fontSize: '0.75rem', fontWeight: '700',
                        }}>
                          {rec.eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <span style={{ color: scoreColor(rec.score), fontWeight: '700', fontSize: '0.9rem' }}>{rec.score?.toFixed(1)} score</span>
                          <button
                            onClick={() => toggleBookmark(rec.opportunity_id)}
                            style={{ background: 'none', border: 'none', cursor: 'pointer', color: isBookmarked ? '#facc15' : '#94a3b8', fontSize: '1.1rem' }}
                          >
                            {isBookmarked ? <HiBookmark /> : <HiOutlineBookmark />}
                          </button>
                        </div>
                      </div>

                      <h3 style={{ fontSize: '1.15rem', fontWeight: '700', margin: '0 0 0.6rem 0', color: '#f8fafc' }}>{rec.title}</h3>
                      <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: '0 0 0.75rem 0' }}>{rec.agency || 'Agency not specified'}</p>
                      <p style={{ color: '#cbd5e1', fontSize: '0.85rem', margin: 0 }}>{rec.reasoning}</p>
                    </div>

                    <div style={{ marginTop: '1.5rem', paddingTop: '0.85rem', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
                        <span style={{ color: '#10b981', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <HiCurrencyDollar /> {rec.amount ? `$${rec.amount.toLocaleString()}` : 'Amount N/A'}
                        </span>
                        <span style={{ color: '#94a3b8', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                          <HiCalendar /> {rec.deadline ? rec.deadline.split('T')[0] : 'No deadline'}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button onClick={() => setSelectedGrant(rec)} className="btn-outline" style={{ flex: 1, fontSize: '0.85rem' }}>
                          View Details
                        </button>
                        {rec.url && (
                          <a href={rec.url} target="_blank" rel="noopener noreferrer" className="btn-outline" style={{ display: 'flex', alignItems: 'center', padding: '0 0.75rem' }}>
                            <HiExternalLink />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}

      <GrantDetailsModal grant={selectedGrant} onClose={() => setSelectedGrant(null)} />
    </div>
  );
}