import apiClient from './client';

export const documentsApi = {
  list: () => apiClient.get('/documents'),

  upload: (file) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.post('/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};
