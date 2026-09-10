import React from 'react';
import { HiX, HiCurrencyDollar, HiCalendar, HiExternalLink } from 'react-icons/hi';

export default function GrantDetailsModal({ grant, onClose }) {
  if (!grant) return null;

  const breakdown = [
    { label: 'Domain Fit', value: grant.domain_fit_score },
    { label: 'Deadline Timing', value: grant.deadline_score },
    { label: 'Funding Amount Fit', value: grant.amount_score },
    { label: 'Historical Success Rate', value: grant.success_rate_score },
  ];

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed',
        inset: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '1.5rem',
      }}
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="glass-card"
        style={{
          maxWidth: '560px',
          width: '100%',
          padding: '2rem',
          maxHeight: '85vh',
          overflowY: 'auto',
        }}
      >
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            marginBottom: '1rem',
          }}
        >
          <h2
            style={{
              fontSize: '1.4rem',
              fontWeight: '800',
              color: '#f8fafc',
              margin: 0,
            }}
          >
            {grant.title}
          </h2>

          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '1.4rem',
            }}
          >
            <HiX />
          </button>
        </div>

        <p style={{ color: '#94a3b8', marginBottom: '1rem' }}>
          {grant.agency || 'Agency not specified'}
        </p>

        <div
          style={{
            display: 'flex',
            gap: '1.5rem',
            marginBottom: '0.75rem',
            flexWrap: 'wrap',
          }}
        >
          <span
            style={{
              color: '#10b981',
              fontWeight: '700',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            <HiCurrencyDollar />
            {grant.amount
              ? `$${grant.amount.toLocaleString()}`
              : 'Amount N/A'}
          </span>

          <span
            style={{
              color: '#94a3b8',
              display: 'flex',
              alignItems: 'center',
              gap: '0.35rem',
            }}
          >
            <HiCalendar />
            {grant.deadline
              ? grant.deadline.split('T')[0]
              : 'No deadline'}
          </span>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <span
            style={{
              color: grant.eligible ? '#10b981' : '#f87171',
              background: grant.eligible
                ? 'rgba(16,185,129,0.12)'
                : 'rgba(248,113,113,0.12)',
              border: `1px solid ${
                grant.eligible
                  ? 'rgba(16,185,129,0.3)'
                  : 'rgba(248,113,113,0.3)'
              }`,
              padding: '0.2rem 0.6rem',
              borderRadius: '0.5rem',
              fontSize: '0.75rem',
              fontWeight: '700',
            }}
          >
            {grant.eligible ? 'ELIGIBLE' : 'NOT ELIGIBLE'}
          </span>

          <span
            style={{
              color: '#38bdf8',
              fontWeight: '700',
              fontSize: '0.85rem',
              marginLeft: '0.75rem',
            }}
          >
            Overall score: {grant.score?.toFixed(1)} / 100
          </span>
        </div>

        <h3
          style={{
            fontSize: '0.95rem',
            color: '#38bdf8',
            fontWeight: '700',
            marginBottom: '0.75rem',
          }}
        >
          Score Breakdown
        </h3>

        {breakdown.map((c, idx) => {
          const pct = Math.round((c.value || 0) * 100);

          return (
            <div key={idx} style={{ marginBottom: '0.9rem' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  fontSize: '0.85rem',
                  color: '#cbd5e1',
                  marginBottom: '0.3rem',
                }}
              >
                <span>{c.label}</span>

                <span
                  style={{
                    fontWeight: '700',
                    color:
                      pct >= 70
                        ? '#10b981'
                        : pct >= 40
                        ? '#f59e0b'
                        : '#f87171',
                  }}
                >
                  {pct}%
                </span>
              </div>

              <div
                style={{
                  height: '6px',
                  background: 'rgba(255,255,255,0.08)',
                  borderRadius: '3px',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    width: `${pct}%`,
                    height: '100%',
                    background:
                      pct >= 70
                        ? '#10b981'
                        : pct >= 40
                        ? '#f59e0b'
                        : '#f87171',
                  }}
                />
              </div>
            </div>
          );
        })}

        <p
          style={{
            fontSize: '0.85rem',
            color: '#94a3b8',
            marginTop: '1.25rem',
            fontStyle: 'italic',
          }}
        >
          {grant.reasoning}
        </p>

        {grant.url && (
          <a
            href={grant.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-outline"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              marginTop: '1.25rem',
              fontSize: '0.85rem',
            }}
          >
            View Original Listing <HiExternalLink />
          </a>
        )}
      </div>
    </div>
  );
}