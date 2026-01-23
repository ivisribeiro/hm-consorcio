import apiClient from './client'

export const unidadesApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/unidades/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/unidades/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/unidades/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/unidades/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    const response = await apiClient.delete(`/unidades/${id}`)
    return response.data
  },
}
