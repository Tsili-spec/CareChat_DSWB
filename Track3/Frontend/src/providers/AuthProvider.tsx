import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { RegisterResponse, LoginResponse, apiService } from '../services/api'

interface AuthContextType {
  user: LoginResponse | RegisterResponse | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (userData: any) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<LoginResponse | RegisterResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('authToken')
      const savedUser = localStorage.getItem('user')
      
      if (token && savedUser) {
        try {
          setUser(JSON.parse(savedUser))
        } catch (error) {
          localStorage.removeItem('authToken')
          localStorage.removeItem('user')
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (username: string, password: string) => {
    try {
      const response = await apiService.login({ username, password })
      localStorage.setItem('authToken', response.access_token)
      localStorage.setItem('user', JSON.stringify(response))
      setUser(response)
      
      // Navigate to intended page or dashboard
      const from = location.state?.from?.pathname || '/dashboard'
      navigate(from, { replace: true })
    } catch (error) {
      throw error
    }
  }

  const register = async (userData: any) => {
    try {
      const response = await apiService.register(userData)
      localStorage.setItem('authToken', response.user_id)
      localStorage.setItem('user', JSON.stringify(response))
      setUser(response)
      
      // Navigate to dashboard after successful registration
      navigate('/dashboard', { replace: true })
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    apiService.logout()
    setUser(null)
    navigate('/login', { replace: true })
  }

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}