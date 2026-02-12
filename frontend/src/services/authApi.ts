import api from './api'

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  name: string
  role: string
  is_active: boolean
}

export const authApi = {
  login(data: LoginRequest): Promise<TokenResponse> {
    return api.post('/auth/login', data).then((r) => r.data)
  },

  refresh(refreshToken: string): Promise<TokenResponse> {
    return api.post('/auth/refresh', { refresh_token: refreshToken }).then((r) => r.data)
  },

  me(): Promise<UserResponse> {
    return api.get('/auth/me').then((r) => r.data)
  },
}
