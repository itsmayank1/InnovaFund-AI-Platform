import client from './client';

const DEFAULT_PROFILE = {
  id: 1,
  title: 'Senior Artificial Intelligence & DeepTech Researcher',
  bio: 'Focusing on deep learning architectures, quantum computing applications, and commercial IP development in agricultural biotechnology.',
  technology_areas: 'DeepTech / Artificial Intelligence',
  research_domains: ['Artificial Intelligence', 'Quantum Computing', 'BioTech'],
  keywords: ['deep learning', 'transformers', 'drug discovery', 'quantum ML']
};

export const getMyProfile = async () => {
  try {
    const response = await client.get('/profiles/me');
    return response.data;
  } catch (err) {
    if (err.code === 'ERR_NETWORK' || !err.response) {
      return DEFAULT_PROFILE;
    }
    throw err;
  }
};

export const updateMyProfile = async (data) => {
  const response = await client.put('/profiles/me', data);
  return response.data;
};

export const getProfileById = async (id) => {
  const response = await client.get(`/profiles/${id}`);
  return response.data;
};
