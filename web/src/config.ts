// API Configuration for different environments
const getApiBaseUrl = () => {
  // In development, use localhost
  if (import.meta.env.DEV) {
    return 'http://127.0.0.1:5000';
  }
  
  // In production, use the deployed backend URL
  return 'https://smart-health-ai.up.railway.app';
};

export const API_BASE_URL = getApiBaseUrl();

// Debug logging
console.log('API Configuration:', {
  isDev: import.meta.env.DEV,
  apiUrl: import.meta.env.VITE_API_URL,
  finalApiUrl: API_BASE_URL
});

export const API_ENDPOINTS = {
  sectors: `${API_BASE_URL}/api/ai/sectors`,
  companies: `${API_BASE_URL}/api/companies/dynamic`,
  health: `${API_BASE_URL}/health`,
};

