import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json', // 明确设置 JSON 类型
    Accept: 'application/json',
  },
})

// 请求拦截器：自动在 Header 中加入 Token
request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default request
