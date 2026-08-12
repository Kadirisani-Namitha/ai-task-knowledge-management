import apiClient from './client';

export const usersApi = {
  me:     ()     => apiClient.get('/users/me'),
  list:   ()     => apiClient.get('/users'),
  create: (data) => apiClient.post('/users', data),
};
