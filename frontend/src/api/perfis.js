import apiClient from './client'

export const perfisApi = {
  list: async () => {
    const response = await apiClient.get('/perfis/')
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/perfis/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/perfis/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/perfis/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    await apiClient.delete(`/perfis/${id}`)
  },

  getPermissoes: async () => {
    const response = await apiClient.get('/perfis/permissoes/todas')
    return response.data
  },
}
