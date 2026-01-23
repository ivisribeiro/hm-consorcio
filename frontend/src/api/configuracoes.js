import apiClient from './client'

export const configuracoesApi = {
  list: async (categoria = null) => {
    const params = categoria ? { categoria } : {}
    const response = await apiClient.get('/configuracoes', { params })
    return response.data
  },

  // Configuracoes da Empresa
  getEmpresa: async () => {
    const response = await apiClient.get('/configuracoes/empresa')
    return response.data
  },

  updateEmpresa: async (data) => {
    const response = await apiClient.put('/configuracoes/empresa', data)
    return response.data
  },

  // Configuracoes de PDF
  getPdf: async () => {
    const response = await apiClient.get('/configuracoes/pdf')
    return response.data
  },

  updatePdf: async (data) => {
    const response = await apiClient.put('/configuracoes/pdf', data)
    return response.data
  },

  // Configuracoes do Sistema
  getSistema: async () => {
    const response = await apiClient.get('/configuracoes/sistema')
    return response.data
  },

  updateSistema: async (data) => {
    const response = await apiClient.put('/configuracoes/sistema', data)
    return response.data
  },

  // Seed configuracoes padrao
  seed: async () => {
    const response = await apiClient.post('/configuracoes/seed')
    return response.data
  }
}
