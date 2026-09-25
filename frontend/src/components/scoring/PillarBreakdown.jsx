import React, { useEffect, useState } from 'react';
import { Layers, ShieldAlert } from 'lucide-react';
import { getScoringWeights } from '../../api/scoring';

const PILLAR_LABELS = {
  research_novelty: 'Research Novelty',
  patent_strength: 'Patent Strength',
  technology_maturity: 'Technology Maturity',
  market_potential: 'Market Potential',
  funding_relevance: 'Funding Relevance'
};

const PILLAR_COLORS = {
  research_novelty: '#0ea5e9',      // Sky
  patent_strength: '#8b5cf6',       // Violet
  technology_maturity: '#10b981',   // Emerald
  market_potential: '#f59e0b',      // Amber
  funding_relevance: '#ec4899'      // Pink
};

const DEFAULT_WEIGHTS = {
  research_novelty: 0.30,
  patent_strength: 0.20,
  technology_maturity: 0.15,
  market_potential: 0.20,
  funding_relevance: 0.15
};

export default function PillarBreakdown({ pillars, customWeights }) {
  const [weights, setWeights] = useState(customWeights || DEFAULT_WEIGHTS);

  useEffect(() => {
    if (!weights) {
      getScoringWeights()
        .then((res) => {
          if (res?.primary_weights || res?.weights) {
            setWeights(res.primary_weights || res.weights);
          }
        })
        .catch(() => {
          setWeights(DEFAULT_WEIGHTS);
        });
    }
  }, [weights]);

  if (!pillars) return null;

  return (
    <div style={{
      background: 'var(--bg-card, rgba(15, 23, 42, 0.75))',
      border: '1px solid var(--border-card, rgba(255, 255, 255, 0.1))',
      borderRadius: '16px',
      padding: '24px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Layers size={18} color="#0ea5e9" />
          <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: 'var(--text-main, #f8fafc)' }}>
            5-Pillar Breakdown & Weight Contributions
          </h4>
        </div>
        <span style={{ fontSize: '11px', color: '#64748b' }}>
          Weights dynamic from engine
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {Object.entries(pillars).map(([key, pillarRaw]) => {
          const label = PILLAR_LABELS[key] || key.replace(/_/g, ' ');
          const color = PILLAR_COLORS[key] || '#0ea5e9';
          const isObj = typeof pillarRaw === 'object' && pillarRaw !== null;
          
          const val = isObj ? (pillarRaw.value ?? 0) : Number(pillarRaw || 0);
          const weight = isObj ? (pillarRaw.weight ?? weights?.[key] ?? DEFAULT_WEIGHTS[key] ?? 0.2) : (weights?.[key] ?? DEFAULT_WEIGHTS[key] ?? 0.2);
          const contrib = isObj ? (pillarRaw.weighted_score ?? pillarRaw.contribution ?? (val * weight)) : (val * weight);
          const weightPct = (weight * 100).toFixed(0);

          return (
            <div key={key}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-sub, #cbd5e1)' }}>
                    {label}
                  </span>
                  <span style={{
                    fontSize: '10px',
                    fontWeight: 700,
                    padding: '2px 6px',
                    borderRadius: '4px',
                    background: 'rgba(255,255,255,0.06)',
                    color: '#94a3b8'
                  }}>
                    {weightPct}% Weight
                  </span>
                </div>

                <div style={{ display: 'flex', alignItems: 'baseline', gap: '6px' }}>
                  <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text-main, #f8fafc)' }}>
                    {val.toFixed(1)}
                  </span>
                  <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                    (+{contrib.toFixed(2)} pts)
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div style={{
                height: '8px',
                width: '100%',
                background: 'rgba(255,255,255,0.08)',
                borderRadius: '4px',
                overflow: 'hidden'
              }}>
                <div style={{
                  height: '100%',
                  width: `${Math.min(100, Math.max(0, val))}%`,
                  background: color,
                  borderRadius: '4px',
                  transition: 'width 0.4s ease'
                }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
