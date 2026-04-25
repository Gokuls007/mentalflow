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

export const apiService = {
  // Auth
  login: async (credentials: any) => {
    const response = await apiClient.post('/users/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
    }
    return response.data;
  },
  
  // Games
  submitGameSession: async (data: any) => {
    const response = await apiClient.post('/activities/complete', data);
    return response.data;
  },

  // RL & Personalization
  getDifficultyPrediction: async (userId: number = 1) => {
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

  submitAssessment: async (type: string, responses: number[]) => {
    try {
      const response = await apiClient.post(`/assessments/${type}`, {
        responses,
        total_score: responses.reduce((a, b) => a + b, 0)
      });
      return response.data;
    } catch (error) {
      // Fallback for demo mode when backend is unavailable
      console.warn('[API] Assessment submission failed, using demo fallback');
      const totalScore = responses.reduce((a, b) => a + b, 0);
      return {
        type,
        total_score: totalScore,
        severity: totalScore <= 4 ? 'minimal' : totalScore <= 9 ? 'mild' : totalScore <= 14 ? 'moderate' : totalScore <= 19 ? 'moderately_severe' : 'severe',
        submitted_at: new Date().toISOString()
      };
    }
  }
};

export default apiService;
