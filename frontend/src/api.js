import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const healthAPI = {
  // Health check
  checkHealth: () => api.get('/health'),

  // Upload data
  uploadFile: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  // Get records
  getSleepRecords: (days = 7) => api.get(`/sleep?days=${days}`),
  getActivityRecords: (days = 7) => api.get(`/activity?days=${days}`),
  getVitalsRecords: (days = 7) => api.get(`/vitals?days=${days}`),
  getDerivedMetrics: (days = 7) => api.get(`/metrics/derived?days=${days}`),

  // Analytics
  getSleepSummary: (days = 7) => api.get(`/analytics/sleep-summary?days=${days}`),
  getActivitySummary: (days = 7) => api.get(`/analytics/activity-summary?days=${days}`),
  getCorrelations: () => api.get('/analytics/correlations'),

  // AI Insights
  generateInsights: (days = 7) => api.post(`/insights/generate?days=${days}`),

  // Stats
  getStats: () => api.get('/stats'),
};

export default api;
