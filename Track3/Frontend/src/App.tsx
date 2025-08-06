import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import AddSample from './components/AddSample'
import BloodUsage from './components/BloodUsage'
import Forecasting from './components/Forecasting'
import FeedbackAnalytics from './components/FeedbackAnalytics'
import './App.css'

// Check if user is authenticated
const isAuthenticated = () => {
  // Temporary bypass for testing - remove in production
  return true;
  // return localStorage.getItem('authToken') !== null;
}

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  return isAuthenticated() ? <>{children}</> : <Navigate to="/" replace />;
}

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/add-sample" 
            element={
              <ProtectedRoute>
                <AddSample />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/blood-usage" 
            element={
              <ProtectedRoute>
                <BloodUsage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/forecasting" 
            element={
              <ProtectedRoute>
                <Forecasting />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/feedback-analytics" 
            element={
              <ProtectedRoute>
                <FeedbackAnalytics />
              </ProtectedRoute>
            } 
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
