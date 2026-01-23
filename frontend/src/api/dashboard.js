import apiClient from './client'

export const dashboardApi = {
  getMetricas: async () => {
    const response = await apiClient.get('/dashboard/metricas')
    return response.data
  },

  getAtividadesRecentes: async (limit = 10) => {
    const response = await apiClient.get('/dashboard/atividades-recentes', {
      params: { limit }
    })
    return response.data
  },

  getVendasPorPeriodo: async (dias = 30) => {
    const response = await apiClient.get('/dashboard/vendas-por-periodo', {
      params: { dias }
    })
    return response.data
  },

  getStatusDistribuicao: async () => {
    const response = await apiClient.get('/dashboard/status-distribuicao')
    return response.data
  },

  getTipoBemDistribuicao: async () => {
    const response = await apiClient.get('/dashboard/tipo-bem-distribuicao')
    return response.data
  },

  getVendasMensal: async (meses = 12) => {
    const response = await apiClient.get('/dashboard/vendas-mensal', {
      params: { meses }
    })
    return response.data
  },

  getTopRepresentantes: async (limit = 5) => {
    const response = await apiClient.get('/dashboard/top-representantes', {
      params: { limit }
    })
    return response.data
  },
}
