import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../providers/AuthProvider'
import LoadingSpinner from './LoadingSpinner'

interface PublicRouteProps {
  children: React.ReactNode
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (isAuthenticated) {
    // If user is authenticated, redirect to dashboard or the intended page
    const from = location.state?.from?.pathname || '/dashboard'
    return <Navigate to={from} replace />
  }

  return <>{children}</>
}

export default PublicRoute