import apiClient from './client'

export const beneficiosApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/beneficios/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/beneficios/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/beneficios/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/beneficios/${id}`, data)
    return response.data
  },

  updateStatus: async (id, data) => {
    const response = await apiClient.patch(`/beneficios/${id}/status`, data)
    return response.data
  },

  getHistorico: async (id) => {
    const response = await apiClient.get(`/beneficios/${id}/historico`)
    return response.data
  },

  simular: async (data) => {
    const response = await apiClient.post('/beneficios/simular', data)
    return response.data
  },
}

export const tabelasCreditoApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/beneficios/tabelas/', { params })
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/beneficios/tabelas/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/beneficios/tabelas/${id}`, data)
    return response.data
  },

  importarCSV: async (file, administradoraId = null) => {
    const formData = new FormData()
    formData.append('file', file)
    const params = administradoraId ? `?administradora_id=${administradoraId}` : ''
    const response = await apiClient.post(`/beneficios/tabelas/importar-csv${params}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  },
}

export const administradorasApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/beneficios/administradoras/', { params })
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/beneficios/administradoras/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/beneficios/administradoras/${id}`, data)
    return response.data
  },
}
