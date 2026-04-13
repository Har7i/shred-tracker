import axios from 'axios';

// 1. 创建实例
const api = axios.create({
  baseURL: 'http://3.26.130.155:8000', // 对应 vite.config.js 里的代理路径
});

// 2. 请求拦截器：在请求发出去之前，自动塞入 Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      // 必须按照 FastAPI (OAuth2) 的标准格式：Bearer <token>
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. 响应拦截器：统一处理后端返回的报错
// 响应拦截器：专门处理后端的“赶人”信号
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // 只要后端报 401（未授权），就说明登录状态丢了
      localStorage.removeItem('token');
      // 强制刷新当前页面，由于本地没 token 了，App.jsx 会自动显示登录框
      window.location.reload(); 
    }
    return Promise.reject(error);
  }
);

export default api;