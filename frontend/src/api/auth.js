import apiClient from './client';

export const authApi = {
  login: (username, password) =>
    apiClient.post('/auth/login', { username, password }),
};
