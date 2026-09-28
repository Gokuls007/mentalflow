import axios, { AxiosInstance } from 'axios';
import { useUserStore } from '../store/user.store';

// In dev (Vite), use localhost:8000 directly. In production (Docker/nginx), use relative path.
const API_URL = import.meta.env.DEV
  ? 'http://localhost:8000/api/v1'
  : '/api/v1';

class APIClient {
  private instance: AxiosInstance;

  constructor() {
    this.instance = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor: add auth token
    this.instance.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor: handle errors gracefully
    this.instance.interceptors.response.use(
      (response) => response,
      (error) => {
        // Log but don't redirect — demo mode operates without auth
        if (error.response?.status === 401) {
          console.warn('[API] 401 Unauthorized — running in demo mode without auth');
        }
        return Promise.reject(error);
      }
    );
  }

  get instance_() {
    return this.instance;
  }
}

export const apiClient = new APIClient().instance_;

// Seeded demo account used when nobody is logged in (backend DEMO_MODE)
export const DEMO_USER_ID = 1;

// Id of the logged-in user, or the demo account when nobody is logged in
export const getActiveUserId = (): number => useUserStore.getState().user?.id || DEMO_USER_ID;

export const apiService = {
  // Auth
  login: async (credentials: any) => {
    const response = await apiClient.post('/users/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
    }
    return response.data;
  },

  getMe: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
  
  // Games & Clinical Tracking
  submitGameSession: async (data: any) => {
    const response = await apiClient.post('/rl/submit-game-results', data);
    return response.data;
  },

  // RL & Personalization
  getDifficultyPrediction: async (userId: number = getActiveUserId()) => {
    const response = await apiClient.get(`/rl/predict-difficulty/${userId}`);
    return response.data;
  },

  generateActivity: async (userId: number) => {
    const response = await apiClient.post(`/gan/generate-activity/${userId}`);
    return response.data;
  },

  getRLMetrics: async (userId: number) => {
    const response = await apiClient.get(`/rl/metrics/${userId}`);
    return response.data;
  },

  // Assessments
  submitPHQ9: async (data: any) => {
    const response = await apiClient.post('/assessments/phq9', data);
    return response.data;
  },

  // Saves a PHQ-9 / GAD-7 and returns { score, total_score, severity, crisis_level, date }.
  // Throws on failure so the caller can fall back to local scoring.
  submitAssessment: async (type: 'phq9' | 'gad7', responses: number[]) => {
    const response = await apiClient.post(`/assessments/${type}`, { responses });
    return response.data;
  }
};

export default apiService;
