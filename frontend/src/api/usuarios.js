import apiClient from './client'

export const usuariosApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/usuarios/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/usuarios/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/usuarios/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/usuarios/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    const response = await apiClient.delete(`/usuarios/${id}`)
    return response.data
  },

  changePassword: async (id, nova_senha) => {
    const response = await apiClient.put(`/usuarios/${id}/senha`, { nova_senha })
    return response.data
  },
}
