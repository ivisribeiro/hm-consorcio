import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { message } from 'antd'
import { authApi } from '../api/auth'
import { perfisApi } from '../api/permissoes'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [permissoes, setPermissoes] = useState([])
  const [loading, setLoading] = useState(true)

  // Carrega permissões do usuário
  const loadPermissoes = async () => {
    try {
      const data = await perfisApi.getMinhasPermissoes()
      setPermissoes(data.permissoes || [])
    } catch (error) {
      console.error('Erro ao carregar permissões:', error)
      setPermissoes([])
    }
  }

  // Verifica se há sessão ativa ao carregar
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      const savedUser = localStorage.getItem('user')

      if (token && savedUser) {
        try {
          // Verifica se o token ainda é válido
          const userData = await authApi.getMe()
          setUser(userData)
          await loadPermissoes()
        } catch (error) {
          // Token inválido, limpa storage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          setUser(null)
          setPermissoes([])
        }
      }

      setLoading(false)
    }

    checkAuth()
  }, [])

  // Login
  const login = useCallback(async (email, senha) => {
    try {
      const data = await authApi.login(email, senha)

      // Salva tokens e dados do usuário
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('user', JSON.stringify(data.user))

      setUser(data.user)
      await loadPermissoes()
      message.success(`Bem-vindo, ${data.user.nome}!`)

      return { success: true }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erro ao fazer login'
      message.error(errorMessage)
      return { success: false, error: errorMessage }
    }
  }, [])

  // Logout
  const logout = useCallback(async () => {
    await authApi.logout()

    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')

    setUser(null)
    setPermissoes([])
    message.info('Logout realizado com sucesso')
  }, [])

  // Verifica se é autenticado
  const isAuthenticated = !!user

  // Verifica se usuário tem um dos perfis permitidos
  const hasRole = useCallback(
    (allowedRoles) => {
      if (!user) return false
      return allowedRoles.includes(user.perfil)
    },
    [user]
  )

  // Verifica se usuário tem permissão específica (pelo código)
  const hasPermission = useCallback(
    (permissionCode) => {
      if (!user) return false
      // Admin tem todas as permissões
      if (user.perfil?.codigo === 'admin') return true
      return permissoes.includes(permissionCode)
    },
    [user, permissoes]
  )

  // Verifica se tem pelo menos uma das permissões
  const hasAnyPermission = useCallback(
    (permissionCodes) => {
      if (!user) return false
      if (user.perfil?.codigo === 'admin') return true
      return permissionCodes.some(code => permissoes.includes(code))
    },
    [user, permissoes]
  )

  const value = {
    user,
    permissoes,
    loading,
    isAuthenticated,
    login,
    logout,
    hasRole,
    hasPermission,
    hasAnyPermission,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
