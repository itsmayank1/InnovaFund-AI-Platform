import client from './client';

export const searchPublications = async (query = 'artificial intelligence', source = 'all', limit = 10) => {
  const response = await client.get('/datasets/publications/search', {
    params: { query, source, limit },
  });
  return response.data;
};

export const searchPatents = async (query = 'quantum computing', source = 'all', limit = 10) => {
  const response = await client.get('/datasets/patents/search', {
    params: { query, source, limit },
  });
  return response.data;
};
