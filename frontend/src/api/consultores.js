import apiClient from './client'

export const consultoresApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/consultores/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/consultores/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/consultores/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/consultores/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    const response = await apiClient.delete(`/consultores/${id}`)
    return response.data
  },
}
