import apiClient from './client'

export const empresasApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/empresas/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/empresas/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/empresas/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/empresas/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    const response = await apiClient.delete(`/empresas/${id}`)
    return response.data
  },
}
