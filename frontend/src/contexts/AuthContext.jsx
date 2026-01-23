import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { message } from 'antd'
import { authApi } from '../api/auth'

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
  const [loading, setLoading] = useState(true)

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
        } catch (error) {
          // Token inválido, limpa storage
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user')
          setUser(null)
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
    message.info('Logout realizado com sucesso')
  }, [])

  // Verifica se é autenticado
  const isAuthenticated = !!user

  // Verifica permissões
  const hasPermission = useCallback(
    (allowedRoles) => {
      if (!user) return false
      return allowedRoles.includes(user.perfil)
    },
    [user]
  )

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    hasPermission,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
