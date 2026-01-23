import apiClient from './client'

export const relatoriosApi = {
  // Gera PDF do cliente
  gerarPdfCliente: async (clienteId) => {
    const response = await apiClient.get(`/relatorios/cliente/${clienteId}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Gera PDF do benefício
  gerarPdfBeneficio: async (beneficioId) => {
    const response = await apiClient.get(`/relatorios/beneficio/${beneficioId}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Gera PDF do contrato
  gerarContratoPdf: async (beneficioId) => {
    const response = await apiClient.get(`/relatorios/contrato/${beneficioId}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Gera PDF do termo de adesão
  gerarTermoAdesaoPdf: async (beneficioId) => {
    const response = await apiClient.get(`/relatorios/termo-adesao/${beneficioId}/pdf`, {
      responseType: 'blob'
    })
    return response.data
  },

  // Helper para download do blob
  downloadPdf: (blob, filename) => {
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
