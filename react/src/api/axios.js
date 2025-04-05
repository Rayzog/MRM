import axios from 'axios';
import { API_BASE_URL } from '../config';

const instance = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
});

instance.interceptors.request.use(config => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

instance.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                const response = await axios.post('/auth/refresh', { refresh_token: refreshToken });

                localStorage.setItem('access_token', response.data.access_token);
                originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`;
                return axios(originalRequest);
            } catch (e) {
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
            }
        }

        return Promise.reject(error);
    }
);

export default instance;