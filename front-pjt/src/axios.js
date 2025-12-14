// src/axios.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
});

// 요청 시 Authorization 헤더 자동 추가
api.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 - 토큰 만료 시 자동 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem('refreshToken');

      try {
        const res = await axios.post('http://localhost:8000/api/auth/token/refresh/', {
          refresh: refreshToken,
        });

        const newAccess = res.data.access;
        localStorage.setItem('accessToken', newAccess);
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;

        return api(originalRequest); // 재요청
      } catch (refreshError) {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
