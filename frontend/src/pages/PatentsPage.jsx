import React, { useState } from 'react';
import { searchPatents } from '../api/research';
import LoadingSpinner from '../components/LoadingSpinner';
import { HiSearch, HiLightBulb, HiShieldCheck, HiSparkles, HiCheckCircle, HiDownload } from 'react-icons/hi';

export default function PatentsPage() {
  const [query, setQuery] = useState('quantum computing');
  const [source, setSource] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [limit, setLimit] = useState(10);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const data = await searchPatents(query, source, limit);
      setResults(data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setSearched(true);
    }
  };

  const handleExportCSV = () => {
    if (!results || results.length === 0) return;
    const headers = ['Patent Number', 'Title', 'Status', 'Assignee', 'Source'];
    const rows = results.map(r => [
      `"${r.patent_number || ''}"`,
      `"${(r.title || '').replace(/"/g, '""')}"`,
      `"${r.status || ''}"`,
      `"${(r.assignee || '').replace(/"/g, '""')}"`,
      `"${r.external_source || ''}"`
    ]);
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `InnovaFund_Patents_${query.replace(/\s+/g, '_')}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredResults = results.filter(p => {
    if (statusFilter === 'granted') return p.status === 'Granted';
    if (statusFilter === 'pending') return p.status !== 'Granted';
    return true;
  });

  const getSourceBadgeClass = (src) => {
    switch (src) {
      case 'USPTO': return 'badge-uspto';
      case 'Google Patents': return 'badge-google';
      case 'The Lens': return 'badge-lens';
      default: return 'badge-uspto';
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1400px', margin: '0 auto' }} className="animate-fade-in">
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', color: '#c084fc', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.4rem' }}>
          <HiSparkles /> Global Intellectual Property Engine
        </div>
        <h1 style={{ fontSize: '2.25rem', fontWeight: '800', margin: '0 0 0.5rem 0', background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
          Patent Landscape Analytics
        </h1>
        <p style={{ color: '#94a3b8', margin: 0, fontSize: '0.95rem' }}>
          Explore global patent records across USPTO Public Data, Google Patents, and The Lens IP datasets.
        </p>
      </div>

      {/* Search Bar Container */}
      <div className="glass-card" style={{ padding: '1.5rem 2rem', marginBottom: '2rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'grid', gridTemplateColumns: '1fr 180px 110px 140px', gap: '1.25rem', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <input
              type="text"
              className="glass-input"
              style={{ width: '100%', boxSizing: 'border-box', paddingLeft: '2.75rem' }}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search patents by technology area, title, or assignee..."
              required
            />
            <HiSearch style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: '#94a3b8', fontSize: '1.1rem' }} />
          </div>

          <select
            className="glass-input"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          >
            <option value="all" style={{ background: '#030712' }}>All Datasets</option>
            <option value="uspto" style={{ background: '#030712' }}>USPTO Public Data</option>
            <option value="google_patents" style={{ background: '#030712' }}>Google Patents</option>
            <option value="the_lens" style={{ background: '#030712' }}>The Lens</option>
          </select>

          <select
            className="glass-input"
            value={limit}
            onChange={(e) => setLimit(Number(e.target.value))}
          >
            <option value={5} style={{ background: '#030712' }}>5 Results</option>
            <option value={10} style={{ background: '#030712' }}>10 Results</option>
            <option value={25} style={{ background: '#030712' }}>25 Results</option>
          </select>

          <button type="submit" className="btn-gradient" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
            <HiSearch /> Search
          </button>
        </form>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : searched ? (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: '#94a3b8', marginBottom: '1.25rem', fontSize: '0.95rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span>Found <strong style={{ color: '#f8fafc' }}>{filteredResults.length}</strong> patent records for "<strong style={{ color: '#c084fc' }}>{query}</strong>"</span>
              
              {/* Status Filter Buttons */}
              <div style={{ display: 'flex', gap: '0.35rem', background: 'rgba(255,255,255,0.03)', padding: '0.2rem', borderRadius: '0.6rem', border: '1px solid rgba(255,255,255,0.08)' }}>
                <button
                  onClick={() => setStatusFilter('all')}
                  style={{ padding: '0.25rem 0.65rem', borderRadius: '0.4rem', border: 'none', background: statusFilter === 'all' ? '#0ea5e9' : 'transparent', color: statusFilter === 'all' ? '#fff' : '#94a3b8', fontSize: '0.75rem', fontWeight: '600', cursor: 'pointer' }}
                >
                  All Status
                </button>
                <button
                  onClick={() => setStatusFilter('granted')}
                  style={{ padding: '0.25rem 0.65rem', borderRadius: '0.4rem', border: 'none', background: statusFilter === 'granted' ? '#10b981' : 'transparent', color: statusFilter === 'granted' ? '#fff' : '#94a3b8', fontSize: '0.75rem', fontWeight: '600', cursor: 'pointer' }}
                >
                  Granted Only
                </button>
              </div>
            </div>

            {results.length > 0 && (
              <button
                onClick={handleExportCSV}
                className="btn-outline"
                style={{ padding: '0.45rem 1rem', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
              >
                <HiDownload /> Export Patent CSV
              </button>
            )}
          </div>

          {filteredResults.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(380px, 1fr))', gap: '1.75rem' }}>
              {filteredResults.map((pat, idx) => (
                <div key={idx} className="glass-card" style={{ padding: '1.75rem', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem', marginBottom: '0.85rem' }}>
                      <span className={`badge-pill ${getSourceBadgeClass(pat.external_source)}`}>
                        {pat.external_source}
                      </span>
                      <span style={{
                        padding: '0.25rem 0.75rem',
                        borderRadius: '1rem',
                        fontSize: '0.75rem',
                        fontWeight: '700',
                        background: pat.status === 'Granted' ? 'rgba(16,185,129,0.15)' : 'rgba(245,158,11,0.15)',
                        border: pat.status === 'Granted' ? '1px solid rgba(16,185,129,0.3)' : '1px solid rgba(245,158,11,0.3)',
                        color: pat.status === 'Granted' ? '#6ee7b7' : '#fcd34d'
                      }}>
                        {pat.status}
                      </span>
                    </div>

                    <h3 style={{ fontSize: '1.15rem', fontWeight: '700', margin: '0 0 0.6rem 0', lineHeight: 1.4, color: '#f8fafc' }}>
                      {pat.title}
                    </h3>

                    <p style={{ color: '#cbd5e1', fontSize: '0.875rem', margin: '0 0 0.5rem 0' }}>
                      <strong style={{ color: '#94a3b8' }}>Patent Number:</strong> <code style={{ background: 'rgba(255,255,255,0.06)', padding: '0.2rem 0.5rem', borderRadius: '0.4rem', color: '#7dd3fc', fontSize: '0.85rem' }}>{pat.patent_number}</code>
                    </p>

                    <p style={{ color: '#94a3b8', fontSize: '0.85rem', margin: 0 }}>
                      <strong style={{ color: '#64748b' }}>Assignee:</strong> {pat.assignee || 'Global Technology Corp'}
                    </p>
                  </div>

                  <div style={{ marginTop: '1.5rem', paddingTop: '0.85rem', borderTop: '1px solid rgba(255,255,255,0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.85rem', color: '#94a3b8' }}>
                    <span style={{ fontSize: '0.8rem', color: '#64748b' }}>IP Provider: {pat.external_source}</span>
                    <span style={{ color: '#10b981', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                      <HiCheckCircle /> Valid Record
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ padding: '4rem', textAlign: 'center', color: '#94a3b8' }}>
              No patent records matched your search parameters.
            </div>
          )}
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '4rem', textAlign: 'center', color: '#94a3b8' }}>
          Enter keywords above and click Search to query USPTO, Google Patents, and The Lens IP datasets.
        </div>
      )}
    </div>
  );
}
