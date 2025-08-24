// API Configuration for different environments
const getApiBaseUrl = () => {
  // In development, use localhost
  if (import.meta.env.DEV) {
    return 'http://127.0.0.1:5001';
  }
  
  // In production, use the deployed backend URL
  // You'll need to replace this with your actual deployed backend URL
  return import.meta.env.VITE_API_URL || 'https://your-backend-url.vercel.app';
};

export const API_BASE_URL = getApiBaseUrl();

export const API_ENDPOINTS = {
  sectors: `${API_BASE_URL}/api/ai/sectors`,
  companies: `${API_BASE_URL}/api/companies/dynamic`,
  health: `${API_BASE_URL}/api/health`,
};
