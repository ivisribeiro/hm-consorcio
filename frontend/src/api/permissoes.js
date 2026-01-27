import apiClient from './client'

export const perfisApi = {
  // Lista todos os perfis
  list: async () => {
    const response = await apiClient.get('/perfis/')
    return response.data
  },

  // Busca um perfil com suas permissões
  get: async (perfilId) => {
    const response = await apiClient.get(`/perfis/${perfilId}`)
    return response.data
  },

  // Cria um novo perfil
  create: async (data) => {
    const response = await apiClient.post('/perfis/', data)
    return response.data
  },

  // Atualiza um perfil
  update: async (perfilId, data) => {
    const response = await apiClient.put(`/perfis/${perfilId}`, data)
    return response.data
  },

  // Deleta um perfil
  delete: async (perfilId) => {
    const response = await apiClient.delete(`/perfis/${perfilId}`)
    return response.data
  },

  // Lista todas as permissões
  listPermissoes: async () => {
    const response = await apiClient.get('/perfis/permissoes/todas')
    return response.data
  },

  // Busca a matriz de permissões
  getMatriz: async () => {
    const response = await apiClient.get('/perfis/permissoes/matriz')
    return response.data
  },

  // Atualiza permissões de um perfil
  updatePermissoes: async (perfilId, permissoes) => {
    const response = await apiClient.put(`/perfis/${perfilId}/permissoes`, {
      permissoes
    })
    return response.data
  },

  // Popula perfis e permissões padrão
  seed: async () => {
    const response = await apiClient.post('/perfis/seed')
    return response.data
  },

  // Busca permissões do usuário logado
  getMinhasPermissoes: async () => {
    const response = await apiClient.get('/perfis/usuario/minhas-permissoes')
    return response.data
  },
}

// Manter compatibilidade com código antigo
export const permissoesApi = perfisApi
