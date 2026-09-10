import axios from 'axios';

const recClient = axios.create({ baseURL: 'http://localhost:8000' });
recClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Demo-safe mock data, matches Member 1's real API_CONTRACT.md shape exactly
const MOCK_RECOMMENDATIONS = [
  {
    opportunity_id: 1,
    title: 'AI for Climate Resilience Grant',
    agency: 'Global Innovation Fund',
    amount: 250000,
    deadline: '2026-11-15T00:00:00',
    url: 'https://example.com/grant/1',
    score: 92.4,
    domain_fit_score: 0.95,
    deadline_score: 0.85,
    amount_score: 0.7,
    success_rate_score: 0.6,
    eligible: true,
    reasoning: 'Strong domain fit, deadline gives enough prep time, well-funded opportunity.',
  },
  {
    opportunity_id: 2,
    title: 'Early-Career AI Fellowship',
    agency: 'National Science Council',
    amount: 85000,
    deadline: '2026-09-30T00:00:00',
    url: 'https://example.com/grant/2',
    score: 78.1,
    domain_fit_score: 0.8,
    deadline_score: 0.5,
    amount_score: 0.4,
    success_rate_score: 0.3,
    eligible: true,
    reasoning: 'Good domain overlap, deadline is approaching soon.',
  },
  {
    opportunity_id: 3,
    title: 'CleanTech Accelerator Award',
    agency: 'Innovate Global',
    amount: 500000,
    deadline: '2026-08-20T00:00:00',
    url: 'https://example.com/grant/3',
    score: 65.3,
    domain_fit_score: 0.6,
    deadline_score: 0.3,
    amount_score: 0.9,
    success_rate_score: 0.2,
    eligible: false,
    reasoning: 'Domain overlap present but geography restrictions likely apply.',
  },
];

export const getRecommendations = async (researcherId) => {
  try {
    const response = await recClient.get(`/recommendations/${researcherId}`);
    return response.data;
  } catch (err) {
    // Backend not live yet — surface as "needs generation" like the real 404 case
    throw err;
  }
};

export const generateRecommendations = async (researcherId, topN = 10) => {
  try {
    const response = await recClient.post('/recommendations/generate', {
      researcher_id: researcherId,
      top_n: topN,
    });
    return response.data;
  } catch (err) {
    // Fallback for demo: if backend endpoint isn't live (404/network error), show mock data
    if (err.response?.status === 404 || err.code === 'ERR_NETWORK' || !err.response) {
      await new Promise((r) => setTimeout(r, 500));
      return MOCK_RECOMMENDATIONS.slice(0, topN);
    }
    throw err;
  }
};