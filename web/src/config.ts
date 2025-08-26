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
  earnings: `${API_BASE_URL}/api/earnings`,
  earningsWeek: `${API_BASE_URL}/api/earnings_week`,
  scoreStocks: `${API_BASE_URL}/api/score-stocks`,
  recommend: `${API_BASE_URL}/api/recommend`,
};

// Helper function for API calls with better error handling
export const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    console.log(`Making API call to: ${url}`);
    const response = await fetch(url, defaultOptions);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`API Error ${response.status}:`, errorText);
      throw new Error(`API Error ${response.status}: ${errorText}`);
    }
    
    const data = await response.json();
    console.log(`API call successful:`, data);
    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

