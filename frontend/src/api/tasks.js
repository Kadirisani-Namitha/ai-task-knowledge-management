import apiClient from './client';

export const tasksApi = {
  list:   (status) => apiClient.get('/tasks', { params: status ? { status } : {} }),
  get:    (id)     => apiClient.get(`/tasks/${id}`),
  create: (data)   => apiClient.post('/tasks', data),
  update: (id, data) => apiClient.patch(`/tasks/${id}`, data),
  delete: (id)     => apiClient.delete(`/tasks/${id}`),
};
