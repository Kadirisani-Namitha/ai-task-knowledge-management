import apiClient from './client';

export const searchApi = {
  search: (query, top_k = 5) =>
    apiClient.post('/search', { query, top_k }),
};
