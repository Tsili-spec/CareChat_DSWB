import { Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import './App.css'
import Login from './components/Login'
import Signup from './components/Signup'
import DashboardLayout from './components/DashboardLayout'
import ProtectedRoute from './components/ProtectedRoute'
import PublicRoute from './components/PublicRoute'

function App() {
  const navigate = useNavigate()

  return (
    <Routes>
      {/* Public routes - only accessible when not authenticated */}
      <Route 
        path="/login" 
        element={
          <PublicRoute>
            <Login onSwitchToSignup={() => navigate('/signup')} />
          </PublicRoute>
        } 
      />
      <Route 
        path="/signup" 
        element={
          <PublicRoute>
            <Signup onSwitchToLogin={() => navigate('/login')} />
          </PublicRoute>
        } 
      />

      {/* Protected routes - only accessible when authenticated */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        } 
      />

      {/* Redirect root to dashboard */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Catch all route - redirect to dashboard */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default App
