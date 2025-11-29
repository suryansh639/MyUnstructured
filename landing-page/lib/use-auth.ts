'use client'

import { useState, useEffect } from 'react'
import { apiClient } from './api-client'

export function useAuth() {
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = apiClient.getToken()
      if (token) {
        const userData = await apiClient.getCredits()
        setUser(userData)
      }
    } catch (error) {
      console.error('Auth check failed:', error)
    } finally {
      setLoading(false)
    }
  }

  const register = async (email: string, password: string, name: string) => {
    const result = await apiClient.register(email, password, name)
    return result
  }

  const logout = () => {
    apiClient.setToken('')
    setUser(null)
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token')
    }
  }

  return { user, loading, register, logout, checkAuth }
}
