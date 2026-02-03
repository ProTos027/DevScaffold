import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api';

// Create axios instance
const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            const refreshToken = localStorage.getItem('refreshToken');
            if (refreshToken) {
                try {
                    const { data } = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                        refresh: refreshToken,
                    });
                    localStorage.setItem('accessToken', data.access);
                    apiClient.defaults.headers.Authorization = `Bearer ${data.access}`;
                    return apiClient(originalRequest);
                } catch (refreshError) {
                    localStorage.removeItem('accessToken');
                    localStorage.removeItem('refreshToken');
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    register: (email, password, firstName, lastName) =>
        apiClient.post('/auth/register/', {
            email,
            password,
            password2: password,
            first_name: firstName,
            last_name: lastName
        }),

    login: (email, password) =>
        apiClient.post('/auth/login/', { email, password }),

    getProfile: () =>
        apiClient.get('/auth/profile/'),

    updateAPIKeys: (openaiKey, anthropicKey) =>
        apiClient.put('/auth/api-keys/', { openai_api_key: openaiKey, anthropic_api_key: anthropicKey }),

    checkKeys: () =>
        apiClient.get('/auth/check-keys/'),
};

// API Keys Management (New)
export const apiKeysAPI = {
    list: () =>
        apiClient.get('/auth/keys/'),

    create: (provider, name, apiKey) =>
        apiClient.post('/auth/keys/', { provider, name, api_key: apiKey }),

    delete: (id) =>
        apiClient.delete(`/auth/keys/${id}/`),
};

// Projects API
export const projectsAPI = {
    list: () =>
        apiClient.get('/projects/'),

    create: (prompt, geminiModel, name, geminiApiKeyId) =>
        apiClient.post('/projects/', {
            prompt,
            gemini_model: geminiModel,
            name,
            gemini_api_key_id: geminiApiKeyId
        }),

    get: (id) =>
        apiClient.get(`/projects/${id}/`),

    getIntentSpec: (id) =>
        apiClient.get(`/projects/${id}/intent_spec/`),

    updateIntentSpec: (id, spec) =>
        apiClient.put(`/projects/${id}/update_intent_spec/`, spec),

    getStatus: (id) =>
        apiClient.get(`/projects/${id}/status/`),

    download: (id) =>
        apiClient.get(`/projects/${id}/download/`, { responseType: 'blob' }),

    cancel: (id) =>
        apiClient.post(`/projects/${id}/cancel/`),

    delete: (id) =>
        apiClient.delete(`/projects/${id}/`),
};

export default apiClient;
