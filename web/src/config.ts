// API Configuration for different environments
const getApiBaseUrl = () => {
         // In development, use localhost
       if (import.meta.env.DEV) {
         return 'http://127.0.0.1:5000';
       }
  
  // In production, use the deployed backend URL
  // You'll need to replace this with your actual deployed backend URL
  const apiUrl = import.meta.env.VITE_API_URL;
  if (!apiUrl) {
    console.error('VITE_API_URL environment variable is not set. Please set it to your deployed backend URL.');
    return 'http://127.0.0.1:5001'; // Fallback to localhost for now
  }
  return apiUrl;
};

export const API_BASE_URL = getApiBaseUrl();

// Debug logging
console.log('API Configuration:', {
  isDev: import.meta.env.DEV,
  apiUrl: import.meta.env.VITE_API_URL,
  finalApiUrl: API_BASE_URL
});

export const API_ENDPOINTS = {
  sectors: `/api/ai/sectors`,
  companies: `/api/companies/dynamic`,
  health: `/api/health`,
};

