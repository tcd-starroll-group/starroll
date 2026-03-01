import request from '@/utils/requests'

// login
export const loginApi = (data: { username: string; password: string }) => {
  return request.post('/userLogin', data)
}

// register
export const registerApi = (data: any) => {
  return request.post('/userReg', data)
}

export const changePasswordApi = (data: any) => {
  return request.post('/changePassword', data)
}

export const getProfileApi = () => {
  return request.post('/userProfile', {})
}

// reset password
export const resetPasswordApi = (email: string) => {
  return request.post('/auth/reset-password', { email })
}
