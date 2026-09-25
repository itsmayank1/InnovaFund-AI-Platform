import React from 'react';
import { Target, Zap, Activity, DollarSign, Rocket, Compass, Shield } from 'lucide-react';

export default function DerivedScoresPanel({ derivedScores }) {
  if (!derivedScores) return null;

  // Extract derived metrics supporting both backend schema representations
  const defensibility = derivedScores.defensibility ?? derivedScores.research_impact ?? 75.0;
  const commercialReadiness = derivedScores.commercial_readiness ?? derivedScores.commercial_viability ?? 72.5;
  const grantCompetitiveness = derivedScores.grant_competitiveness ?? derivedScores.funding_attractiveness ?? 78.0;
  const innovationPotential = derivedScores.innovation_potential ?? derivedScores.overall_score ?? 80.0;
  
  const trlVal = derivedScores.technology_readiness?.trl ?? (commercialReadiness >= 80 ? 7 : (commercialReadiness >= 65 ? 6 : 4));
  const trlScore = derivedScores.technology_readiness?.score ?? commercialReadiness;

  const derivedMetrics = [
    { name: 'Defensibility', val: defensibility, icon: Shield, color: '#8b5cf6' },
    { name: 'Commercial Readiness', val: commercialReadiness, icon: DollarSign, color: '#f59e0b' },
    { name: 'Grant Competitiveness', val: grantCompetitiveness, icon: Rocket, color: '#ec4899' },
    { name: 'Innovation Potential', val: innovationPotential, icon: Zap, color: '#0ea5e9' }
  ];

  return (
    <div style={{
      background: 'var(--bg-card, rgba(15, 23, 42, 0.75))',
      border: '1px solid var(--border-card, rgba(255, 255, 255, 0.1))',
      borderRadius: '16px',
      padding: '24px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '18px' }}>
        <Activity size={18} color="#0ea5e9" />
        <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: 'var(--text-main, #f8fafc)' }}>
          Derived Strategic Dimensions & TRL Scale
        </h4>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '14px',
        marginBottom: '16px'
      }}>
        {derivedMetrics.map(({ name, val, icon: Icon, color }) => (
          <div
            key={name}
            style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Icon size={16} color={color} />
              <span style={{ fontSize: '18px', fontWeight: 800, color: 'var(--text-main, #f8fafc)' }}>
                {Number(val || 0).toFixed(1)}
              </span>
            </div>
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--text-sub, #cbd5e1)' }}>
              {name}
            </span>
          </div>
        ))}
      </div>

      {/* Technology Readiness Level (TRL) Card */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(99, 102, 241, 0.05) 100%)',
        border: '1px solid rgba(14, 165, 233, 0.25)',
        borderRadius: '12px',
        padding: '16px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            background: '#0284c7',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 800,
            fontSize: '15px'
          }}>
            TRL {trlVal}
          </div>
          <div>
            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-main, #f8fafc)' }}>
              Technology Readiness Level (NASA 1–9)
            </div>
            <div style={{ fontSize: '11px', color: '#94a3b8' }}>
              Engineering readiness score: {Number(trlScore || 0).toFixed(1)} / 100
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '3px' }}>
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((lvl) => {
            const active = lvl <= trlVal;
            return (
              <div
                key={lvl}
                style={{
                  width: '18px',
                  height: '8px',
                  borderRadius: '2px',
                  background: active ? '#0ea5e9' : 'rgba(255, 255, 255, 0.1)',
                  transition: 'background 0.3s'
                }}
                title={`TRL Level ${lvl}`}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
}
