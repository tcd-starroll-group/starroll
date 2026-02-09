import request from '@/utils/requests';

// login
export const loginApi = (data: { username: string; password: string }) => {
  return request.post('/userLogin', data);
};

// register
export const registerApi = (data: any) => {
  return request.post('/userRegister', data);
};

// reset password
export const resetPasswordApi = (email: string) => {
  return request.post('/auth/reset-password', { email });
};