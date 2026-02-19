import axios from 'axios';

const request = axios.create({
  baseURL: 'http://localhost:8000/api',  // 如果前端运行在不同端口（如 3000），建议改为相对路径或使用代理（见下文）
  timeout: 5000,  // 可选：设置超时，单位 ms
  headers: {
    'Content-Type': 'application/json',  // 明确设置 JSON 类型
    'Accept': 'application/json'
  },
  withCredentials: true  // 可选：如果需要跨域携带 cookie，启用它；否则可删除
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