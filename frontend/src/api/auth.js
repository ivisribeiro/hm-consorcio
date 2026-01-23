import axios from 'axios'
import apiClient from './client'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export const authApi = {
  // Login - usa axios direto para evitar conflito de headers
  login: async (email, senha) => {
    const formData = new URLSearchParams()
    formData.append('username', email)
    formData.append('password', senha)

    const response = await axios.post(`${API_URL}/auth/login`, formData.toString(), {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  // Refresh token
  refresh: async (refreshToken) => {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  // Obter dados do usuário atual
  getMe: async () => {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  // Logout
  logout: async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch {
      // Ignora erros no logout
    }
  },
}
