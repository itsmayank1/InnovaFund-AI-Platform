import React, { useEffect, useMemo, useState } from 'react';
import {
  HiSparkles,
  HiChartBar,
  HiExclamationCircle,
  HiLightBulb,
  HiArrowTrendingUp,
  HiRocketLaunch,
  HiCube,
  HiDocumentText,
  HiUserGroup,
  HiCheckCircle,
  HiClock,
  HiBeaker,
} from 'react-icons/hi2';

import LoadingSpinner from '../components/LoadingSpinner';
import InnovationScoreBreakdown from '../components/InnovationScoreBreakdown';
import PipelineTracker from '../components/PipelineTracker';
import CommercializationCard from '../components/CommercializationCard';

import {
  getInnovationPortfolio,
  getInnovationPipeline,
  getCommercializationRecommendations,
  USE_MOCK,
} from '../api/innovation';

import './InnovationManagerPage.css';

const STAGE_META = {
  ideation: {
    label: 'Ideation',
    color: '#94a3b8',
  },
  evaluation: {
    label: 'Evaluation',
    color: '#0ea5e9',
  },
  productization: {
    label: 'Productization',
    color: '#8b5cf6',
  },
  licensing: {
    label: 'Licensing',
    color: '#06b6d4',
  },
  startup: {
    label: 'Startup',
    color: '#10b981',
  },
};

function getScoreLabel(score) {
  if (score >= 85) return 'Excellent';
  if (score >= 75) return 'Strong';
  if (score >= 60) return 'Moderate';
  return 'Needs Attention';
}

function getScoreColor(score) {
  if (score >= 80) return '#10b981';
  if (score >= 60) return '#f59e0b';
  return '#f87171';
}

function getStageLabel(stage) {
  return STAGE_META[stage]?.label || stage || 'Unknown';
}

function generateInsight(project) {
  if (!project) {
    return {
      title: 'Portfolio insight',
      text: 'Select an innovation from the pipeline to generate a focused AI-style portfolio insight.',
      type: 'neutral',
    };
  }

  const components = project.components || {};

  const entries = [
    ['research_novelty', 'Research Novelty'],
    ['patent_strength', 'Patent Strength'],
    ['technology_maturity', 'Technology Maturity'],
    ['market_potential', 'Market Potential'],
    ['funding_relevance', 'Funding Relevance'],
  ];

  const sorted = entries
    .map(([key, label]) => ({
      key,
      label,
      value: Number(components[key] || 0),
    }))
    .sort((a, b) => b.value - a.value);

  const strongest = sorted[0];
  const weakest = sorted[sorted.length - 1];

  if (weakest.value < 60) {
    return {
      title: 'Primary opportunity',
      text: `${strongest.label} is a major strength at ${strongest.value}. The main improvement area is ${weakest.label} at ${weakest.value}. Strengthening this factor could improve the project's commercialization readiness.`,
      type: 'warning',
    };
  }

  if (project.overall_score >= 85) {
    return {
      title: 'High-potential innovation',
      text: `${project.title} has an overall score of ${project.overall_score}, with ${strongest.label} as its strongest signal. The innovation appears well positioned for commercialization evaluation.`,
      type: 'success',
    };
  }

  return {
    title: 'Portfolio insight',
    text: `${strongest.label} is currently the strongest signal at ${strongest.value}. The project is in the ${getStageLabel(project.stage)} stage and has an overall innovation score of ${project.overall_score}.`,
    type: 'info',
  };
}

export default function InnovationManagerPage() {
  const [portfolio, setPortfolio] = useState(null);
  const [pipeline, setPipeline] = useState(null);
  const [selectedProjectId, setSelectedProjectId] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  const [loading, setLoading] = useState(true);
  const [recLoading, setRecLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError(null);

      try {
        const [portfolioRes, pipelineRes] = await Promise.all([
          getInnovationPortfolio(),
          getInnovationPipeline(),
        ]);

        if (cancelled) return;

        setPortfolio(portfolioRes);
        setPipeline(pipelineRes);

        const firstProject =
          portfolioRes?.projects?.[0]?.project_id || null;

        setSelectedProjectId(firstProject);
      } catch (err) {
        if (!cancelled) {
          setError(
            err?.message ||
              'Failed to load the Innovation Manager dashboard.'
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!selectedProjectId) {
      setRecommendations([]);
      return;
    }

    let cancelled = false;

    async function loadRecommendations() {
      setRecLoading(true);

      try {
        const response =
          await getCommercializationRecommendations(selectedProjectId);

        if (!cancelled) {
          setRecommendations(response?.recommendations || []);
        }
      } catch {
        if (!cancelled) {
          setRecommendations([]);
        }
      } finally {
        if (!cancelled) {
          setRecLoading(false);
        }
      }
    }

    loadRecommendations();

    return () => {
      cancelled = true;
    };
  }, [selectedProjectId]);

  const projects = portfolio?.projects || [];

  const selectedProject = useMemo(() => {
    return (
      projects.find(
        (project) => project.project_id === selectedProjectId
      ) || null
    );
  }, [projects, selectedProjectId]);

  const analytics = useMemo(() => {
    const total = projects.length;

    const highPotential = projects.filter(
      (project) => Number(project.overall_score || 0) >= 80
    ).length;

    const commercializationReady = projects.filter((project) =>
      ['productization', 'licensing', 'startup'].includes(project.stage)
    ).length;

    const averageScore =
      portfolio?.portfolio_average ??
      (total
        ? Math.round(
            projects.reduce(
              (sum, project) =>
                sum + Number(project.overall_score || 0),
              0
            ) / total
          )
        : 0);

    const stageCounts = Object.keys(STAGE_META).reduce(
      (result, stage) => {
        result[stage] = projects.filter(
          (project) => project.stage === stage
        ).length;

        return result;
      },
      {}
    );

    const strongestProject = [...projects].sort(
      (a, b) =>
        Number(b.overall_score || 0) -
        Number(a.overall_score || 0)
    )[0] || null;

    return {
      total,
      highPotential,
      commercializationReady,
      averageScore,
      stageCounts,
      strongestProject,
    };
  }, [projects, portfolio]);

  const insight = useMemo(
    () => generateInsight(selectedProject),
    [selectedProject]
  );

  const scoreColor = getScoreColor(analytics.averageScore);

  if (loading) {
    return (
      <div className="innovation-loading">
        <LoadingSpinner />
        <span>Loading innovation portfolio...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="innovation-error-page animate-fade-in">
        <div className="innovation-error-card">
          <HiExclamationCircle className="innovation-error-icon" />

          <h3>
            Couldn't load the Innovation Manager dashboard
          </h3>

          <p>{error}</p>

          <button
            className="btn-outline"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const hasProjects = projects.length > 0;

  return (
    <div className="innovation-page animate-fade-in">

      {/* ============================================================
          HEADER
      ============================================================ */}
      <section className="innovation-hero">

        <div className="innovation-hero-content">

          <div className="innovation-eyebrow">
            <HiSparkles />
            Innovation Intelligence
          </div>

          <h1>
            Innovation Manager
            <span>Dashboard</span>
          </h1>

          <p>
            Monitor innovation performance, evaluate portfolio potential,
            track commercialization readiness, and identify the strongest
            opportunities.
          </p>

          <div className="innovation-status-row">

            <span
              className={
                USE_MOCK
                  ? 'innovation-status mock'
                  : 'innovation-status live'
              }
            >
              <span className="status-dot" />

              {USE_MOCK
                ? 'Demo data active'
                : 'Live API connected'}
            </span>

            <span className="innovation-status-secondary">
              {projects.length} innovations monitored
            </span>

          </div>

        </div>

        <div className="hero-score">

          <div className="hero-score-label">
            Portfolio Average
          </div>

          <div
            className="hero-score-value"
            style={{ color: scoreColor }}
          >
            {analytics.averageScore}
          </div>

          <div className="hero-score-scale">
            <span>Innovation Score</span>
            <span>/ 100</span>
          </div>

          <div className="hero-score-bar">
            <div
              style={{
                width: `${Math.min(
                  Math.max(analytics.averageScore, 0),
                  100
                )}%`,
                background: scoreColor,
              }}
            />
          </div>

          <span className="hero-score-rating">
            {getScoreLabel(analytics.averageScore)}
          </span>

        </div>

      </section>

      {/* ============================================================
          MOCK DATA NOTICE
      ============================================================ */}
      {USE_MOCK && (
        <div className="mock-notice">
          <div className="mock-notice-icon">
            <HiBeaker />
          </div>

          <div>
            <strong>Development mode</strong>

            <span>
              Showing mock innovation data. The dashboard is ready to
              switch to Member 4's Innovation Scoring API and Member 5's
              Commercialization API when they are deployed.
            </span>
          </div>
        </div>
      )}

      {!hasProjects ? (
        <section className="innovation-empty">
          <HiChartBar />

          <h3>No innovations in the portfolio yet</h3>

          <p>
            Once patent and technology signals are scored, innovations
            will appear here for portfolio and commercialization review.
          </p>
        </section>
      ) : (
        <>
          {/* ========================================================
              KPI CARDS
          ======================================================== */}
          <section className="kpi-grid">

            <div className="kpi-card">
              <div className="kpi-icon blue">
                <HiChartBar />
              </div>

              <div className="kpi-content">
                <span className="kpi-label">
                  Portfolio Average
                </span>

                <strong>{analytics.averageScore}</strong>

                <small>
                  Overall innovation score
                </small>
              </div>

              <div className="kpi-badge">
                /100
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon green">
                <HiArrowTrendingUp />
              </div>

              <div className="kpi-content">
                <span className="kpi-label">
                  High Potential
                </span>

                <strong>{analytics.highPotential}</strong>

                <small>
                  Score ≥ 80
                </small>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon purple">
                <HiRocketLaunch />
              </div>

              <div className="kpi-content">
                <span className="kpi-label">
                  Commercialization Ready
                </span>

                <strong>
                  {analytics.commercializationReady}
                </strong>

                <small>
                  Product, license or startup
                </small>
              </div>
            </div>

            <div className="kpi-card">
              <div className="kpi-icon orange">
                <HiClock />
              </div>

              <div className="kpi-content">
                <span className="kpi-label">
                  Active Pipeline
                </span>

                <strong>{analytics.total}</strong>

                <small>
                  Innovations monitored
                </small>
              </div>
            </div>

          </section>

          {/* ========================================================
              PIPELINE
          ======================================================== */}
          <section className="dashboard-section">

            <div className="section-heading">

              <div>
                <span className="section-kicker">
                  Portfolio workflow
                </span>

                <h2>
                  Innovation Pipeline
                </h2>

                <p>
                  Select an innovation to inspect its score and
                  commercialization opportunities.
                </p>
              </div>

              <div className="pipeline-summary">
                <HiCheckCircle />
                {analytics.total} active innovations
              </div>

            </div>

            <div className="pipeline-card">
              <PipelineTracker
                stages={pipeline?.stages || []}
                grouped={pipeline?.grouped || {}}
                onSelectProject={setSelectedProjectId}
                selectedProjectId={selectedProjectId}
              />
            </div>

          </section>

          {/* ========================================================
              SELECTED PROJECT
          ======================================================== */}
          {selectedProject && (
            <div className="selected-project-banner">

              <div className="selected-project-main">

                <div className="selected-project-icon">
                  <HiLightBulb />
                </div>

                <div>
                  <span>Selected innovation</span>

                  <h3>
                    {selectedProject.title}
                  </h3>

                  <p>
                    {selectedProject.domain}
                    <span>•</span>
                    {getStageLabel(selectedProject.stage)}
                  </p>
                </div>

              </div>

              <div className="selected-project-score">

                <span>Innovation Score</span>

                <strong
                  style={{
                    color: getScoreColor(
                      selectedProject.overall_score
                    ),
                  }}
                >
                  {selectedProject.overall_score}
                </strong>

              </div>

            </div>
          )}

          {/* ========================================================
              SCORE + AI INSIGHT
          ======================================================== */}
          <section className="main-analytics-grid">

            <div className="analytics-panel">

              <div className="section-heading compact">

                <div>
                  <span className="section-kicker">
                    Weighted evaluation
                  </span>

                  <h2>
                    Innovation Score Breakdown
                  </h2>
                </div>

              </div>

              <InnovationScoreBreakdown
                project={selectedProject}
                weights={portfolio?.weights}
              />

            </div>

            <div className="analytics-side">

              {/* AI INSIGHT */}
              <div
                className={`ai-insight-card ${insight.type}`}
              >

                <div className="ai-insight-header">

                  <div className="ai-insight-icon">
                    <HiSparkles />
                  </div>

                  <div>
                    <span>AI Portfolio Insight</span>
                    <h3>{insight.title}</h3>
                  </div>

                </div>

                <p>
                  {insight.text}
                </p>

                {selectedProject && (
                  <div className="insight-metrics">

                    <div>
                      <span>Stage</span>
                      <strong>
                        {getStageLabel(
                          selectedProject.stage
                        )}
                      </strong>
                    </div>

                    <div>
                      <span>Domain</span>
                      <strong>
                        {selectedProject.domain}
                      </strong>
                    </div>

                  </div>
                )}

              </div>

              {/* PORTFOLIO ANALYTICS */}
              <div className="portfolio-analytics-card">

                <div className="section-heading compact">
                  <div>
                    <span className="section-kicker">
                      Portfolio analytics
                    </span>

                    <h2>
                      Pipeline Distribution
                    </h2>
                  </div>
                </div>

                <div className="distribution-list">

                  {Object.entries(STAGE_META).map(
                    ([stage, meta]) => {

                      const count =
                        analytics.stageCounts[stage] || 0;

                      const percentage =
                        analytics.total > 0
                          ? Math.round(
                              (count /
                                analytics.total) *
                                100
                            )
                          : 0;

                      return (
                        <div
                          className="distribution-row"
                          key={stage}
                        >

                          <div className="distribution-label">
                            <span
                              className="distribution-dot"
                              style={{
                                background:
                                  meta.color,
                              }}
                            />

                            <span>
                              {meta.label}
                            </span>

                            <strong>
                              {count}
                            </strong>
                          </div>

                          <div className="distribution-track">
                            <div
                              style={{
                                width: `${percentage}%`,
                                background:
                                  meta.color,
                              }}
                            />
                          </div>

                        </div>
                      );
                    }
                  )}

                </div>

              </div>

            </div>

          </section>

          {/* ========================================================
              COMMERCIALIZATION
          ======================================================== */}
          <section className="dashboard-section">

            <div className="section-heading">

              <div>
                <span className="section-kicker">
                  Strategic recommendations
                </span>

                <h2>
                  Commercialization Opportunities
                </h2>

                <p>
                  Recommended paths for taking the selected innovation
                  toward market impact.
                </p>
              </div>

              <div className="recommendation-types">

                <span>
                  <HiCube />
                  Product
                </span>

                <span>
                  <HiDocumentText />
                  Licensing
                </span>

                <span>
                  <HiRocketLaunch />
                  Startup
                </span>

                <span>
                  <HiUserGroup />
                  Partnership
                </span>

              </div>

            </div>

            {recLoading ? (
              <div className="recommendation-loading">
                <LoadingSpinner />
                <span>
                  Generating commercialization recommendations...
                </span>
              </div>
            ) : recommendations.length === 0 ? (
              <div className="recommendation-empty">

                <HiLightBulb />

                <h3>
                  No recommendations available
                </h3>

                <p>
                  Commercialization recommendations for this innovation
                  are not available yet.
                </p>

              </div>
            ) : (
              <div className="recommendation-grid">

                {recommendations.map(
                  (recommendation, index) => (
                    <CommercializationCard
                      key={`${recommendation.type}-${index}`}
                      recommendation={recommendation}
                      projectTitle={
                        selectedProject?.title
                      }
                    />
                  )
                )}

              </div>
            )}

          </section>

          {/* ========================================================
              TOP PORTFOLIO OPPORTUNITY
          ======================================================== */}
          {analytics.strongestProject && (
            <section className="top-opportunity">

              <div className="top-opportunity-icon">
                <HiArrowTrendingUp />
              </div>

              <div className="top-opportunity-content">

                <span>
                  Highest-scoring portfolio opportunity
                </span>

                <h3>
                  {analytics.strongestProject.title}
                </h3>

                <p>
                  {analytics.strongestProject.domain}
                  <span>•</span>
                  {getStageLabel(
                    analytics.strongestProject.stage
                  )}
                </p>

              </div>

              <div className="top-opportunity-score">
                <strong>
                  {analytics.strongestProject.overall_score}
                </strong>

                <span>
                  / 100
                </span>
              </div>

              <button
                type="button"
                className="opportunity-button"
                onClick={() =>
                  setSelectedProjectId(
                    analytics.strongestProject.project_id
                  )
                }
              >
                Review Opportunity
              </button>

            </section>
          )}

        </>
      )}

    </div>
  );
}