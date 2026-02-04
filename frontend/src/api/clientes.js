import apiClient from './client'

export const clientesApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/clientes/', { params })
    return response.data
  },

  get: async (id) => {
    const response = await apiClient.get(`/clientes/${id}`)
    return response.data
  },

  create: async (data) => {
    const response = await apiClient.post('/clientes/', data)
    return response.data
  },

  update: async (id, data) => {
    const response = await apiClient.put(`/clientes/${id}`, data)
    return response.data
  },

  delete: async (id) => {
    await apiClient.delete(`/clientes/${id}`)
  },
}

export const utilsApi = {
  validarCPF: async (cpf) => {
    const response = await apiClient.get(`/utils/validar-cpf/${cpf}`)
    return response.data
  },

  validarCNPJ: async (cnpj) => {
    const response = await apiClient.get(`/utils/validar-cnpj/${cnpj}`)
    return response.data
  },

  buscarCEP: async (cep) => {
    const response = await apiClient.get(`/utils/buscar-cep/${cep}`)
    return response.data
  },
}

export const unidadesApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/unidades/', { params })
    return response.data
  },
}

export const empresasApi = {
  list: async (params = {}) => {
    const response = await apiClient.get('/empresas/', { params })
    return response.data
  },
}
