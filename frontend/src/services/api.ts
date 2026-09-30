import axios, { AxiosInstance } from 'axios';
import { useUserStore } from '../store/user.store';

// Relative path everywhere: the Vite dev server proxies /api to BACKEND_URL (see vite.config.js),
// and nginx does the same in Docker. VITE_API_URL overrides it if the API lives elsewhere.
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

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

// Must match PASSWORD_MIN_LENGTH in backend/app/schemas/user.py
export const PASSWORD_MIN_LENGTH = 8;

export const DEMO_PROFILE = {
  id: DEMO_USER_ID,
  email: 'demo@example.com',
  firstName: 'Demo',
  lastName: 'User',
  role: 'patient',
  isDemo: true
};

export const isLoggedIn = (): boolean => !!localStorage.getItem('authToken');

// Map the backend /users/me payload to the store's user shape
export const toStoreUser = (me: any) => ({
  ...me,
  firstName: me.first_name,
  lastName: me.last_name,
  isDemo: false
});

// Human-readable message for a failed auth/API request
export const describeApiError = (error: any, fallback = 'Something went wrong. Please try again.'): string => {
  const status = error?.response?.status;
  const detail = error?.response?.data?.detail;
  if (!error?.response) return 'Cannot reach the server. Check that the backend is running.';
  if (status === 422 && Array.isArray(detail)) {
    return detail.map((d: any) => {
      const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : '';
      const msg = String(d.msg || '').replace(/^Value error, /, '');
      return field && field !== 'body' ? `${field}: ${msg}` : msg;
    }).join(' ');
  }
  if (status === 401) return typeof detail === 'string' && detail !== 'Invalid credentials' ? detail : 'Incorrect email or password.';
  if (status === 409) return 'An account with this email already exists. Try signing in instead.';
  if (typeof detail === 'string') return detail;
  return fallback;
};

export const apiService = {
  // Auth
  login: async (credentials: any) => {
    const response = await apiClient.post('/users/login', credentials);
    if (response.data.access_token) {
      localStorage.setItem('authToken', response.data.access_token);
    }
    return response.data;
  },

  register: async (data: { email: string; password: string; first_name?: string; last_name?: string }) => {
    const response = await apiClient.post('/users/register', data);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('authToken');
  },

  getAuthConfig: async (): Promise<{ demo_mode: boolean; password_min_length: number }> => {
    const response = await apiClient.get('/users/auth-config');
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
