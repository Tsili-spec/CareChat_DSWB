import React, { useState } from 'react';
import './Login.css';

interface LoginFormData {
  username: string;
  password: string;
  role: string;
}

const Login: React.FC = () => {
  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: '',
    role: 'staff'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('https://blood-management-system-xplx.onrender.com/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      
      // Store token and user data
      localStorage.setItem('authToken', data.access_token);
      localStorage.setItem('refreshToken', data.refresh_token);
      localStorage.setItem('userData', JSON.stringify({
        user_id: data.user_id,
        username: data.username,
        role: data.role,
        permissions: data.permissions
      }));

      // Redirect to dashboard
      console.log('Login successful:', data);
      window.location.href = '/dashboard';
      
    } catch (error) {
      console.error('Login error:', error);
      setError(error instanceof Error ? error.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <form onSubmit={handleSubmit} className="login-form">
          <div className="input-group">
            <div className="input-wrapper">
              <span className="input-icon">👤</span>
              <input
                type="text"
                name="username"
                placeholder="Name or Email"
                value={formData.username}
                onChange={handleInputChange}
                required
                className="login-input"
              />
            </div>
          </div>

          <div className="input-group">
            <div className="input-wrapper password-wrapper">
              <span className="input-icon">🔒</span>
              <input
                type={showPassword ? "text" : "password"}
                name="password"
                placeholder="Password"
                value={formData.password}
                onChange={handleInputChange}
                required
                className="login-input"
              />
              <button
                type="button"
                className="password-toggle"
                onClick={togglePasswordVisibility}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "👁️" : "🙈"}
              </button>
            </div>
          </div>

          <div className="input-group">
            <div className="input-wrapper">
              <span className="input-icon">👥</span>
              <select
                name="role"
                value={formData.role}
                onChange={handleInputChange}
                className="login-input role-select"
              >
                <option value="admin">Admin</option>
                <option value="manager">Manager</option>
                <option value="staff">Staff</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? 'LOGGING IN...' : 'LOGIN'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
