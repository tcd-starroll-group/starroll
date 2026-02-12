import axios from 'axios';

const request = axios.create({
  // 后端 API 的基础地址
  baseURL: '/api', 
  timeout: 10000,
});

// 请求拦截器：自动在 Header 中加入 Token
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}
);

export default request;