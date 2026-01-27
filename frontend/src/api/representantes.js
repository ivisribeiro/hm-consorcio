import apiClient from './client'

export const representantesApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/representantes/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/representantes/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/representantes/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/representantes/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    const response = await apiClient.delete(`/representantes/${id}`)
    return response.data
  },
}
