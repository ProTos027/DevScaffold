import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api', // Default local backend URL
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;
            try {
                const refresh = localStorage.getItem('refreshToken');
                const { data } = await axios.post('http://localhost:8000/api/auth/token/refresh/', {
                    refresh,
                });
                localStorage.setItem('accessToken', data.access);
                api.defaults.headers.common['Authorization'] = `Bearer ${data.access}`;
                return api(originalRequest);
            } catch (refreshError) {
                localStorage.clear();
                window.location.href = '/';
                return Promise.reject(refreshError);
            }
        }
        return Promise.reject(error);
    }
);

export const authAPI = {
    login: (email, password) => api.post('/auth/login/', { email, password }),
    register: (email, password, firstName, lastName) =>
        api.post('/auth/register/', { email, password, password2: password, first_name: firstName, last_name: lastName }),
    getProfile: () => api.get('/auth/profile/'),
};

export const projectsAPI = {
    list: () => api.get('/projects/'),
    create: (prompt, geminiModel, name) =>
        api.post('/projects/', { prompt, gemini_model: geminiModel, name }),
    get: (id) => api.get(`/projects/${id}/`),
    getStatus: (id) => api.get(`/projects/${id}/status/`),
    download: (id) => api.get(`/projects/${id}/download/`, { responseType: 'blob' }),
    cancel: (id) => api.post(`/projects/${id}/cancel/`),
    delete: (id) => api.delete(`/projects/${id}/`),
    confirmSpec: (id) => api.post(`/projects/${id}/confirm_spec/`),
    updateSpec: (id, spec) => api.put(`/projects/${id}/update_intent_spec/`, spec),
    browseFiles: (id) => api.get(`/projects/${id}/browse_files/`),
    readFile: (id, path) => api.get(`/projects/${id}/read_file/`, { params: { path } }),
    getVersions: () => api.get('/projects/versions/'),
};

export const apiKeysAPI = {
    list: () => api.get('/auth/keys/'),
    create: (provider, name, apiKey) => api.post('/auth/keys/', { provider, name, api_key: apiKey }),
    delete: (id) => api.delete(`/auth/keys/${id}/`),
};

export default api;
