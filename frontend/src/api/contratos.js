import apiClient from './client'

export const contratosApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/contratos', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/contratos/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/contratos', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/contratos/${id}`, data)
    return response.data
  },

  updateStatus: async (id, data) => {
    const response = await apiClient.patch(`/contratos/${id}/status`, data)
    return response.data
  },

  updateAssinaturas: async (id, data) => {
    const response = await apiClient.patch(`/contratos/${id}/assinaturas`, data)
    return response.data
  },

  delete: async (id) => {
    const response = await apiClient.delete(`/contratos/${id}`)
    return response.data
  },

  downloadPdf: async (id) => {
    const response = await apiClient.get(`/contratos/${id}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Helper para download do blob
  savePdf: (blob, filename) => {
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }
}
