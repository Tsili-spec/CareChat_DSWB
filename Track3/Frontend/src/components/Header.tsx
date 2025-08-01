import { useState, useEffect, useRef } from 'react'
import './Header.css'
import { useAuth } from '../providers/AuthProvider'

const Header = () => {
  const [showUserMenu, setShowUserMenu] = useState(false)
  const { user, logout } = useAuth()
  const userMenuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  const handleLogout = () => {
    logout()
    setShowUserMenu(false)
  }

  const getUserDisplayName = () => {
    if ('username' in user!) {
      return user.username
    }
    return user?.full_name || 'User'
  }

  const getUserRole = () => {
    return user?.role || 'Staff'
  }

  return (
    <header className="header">
      <div className="header-left">
        <h1>Blood Bank Management System</h1>
        <p>Welcome back, {getUserDisplayName()}! Managing blood inventory and donations.</p>
      </div>
      
      <div className="header-right">
        <div className="search-box">
          <input 
            type="text" 
            placeholder="Search donors, inventory..." 
            className="search-input"
          />
          <span className="search-icon">🔍</span>
        </div>
        
        <div className="header-actions">
          <button className="notification-btn">
            🔔
            <span className="notification-badge">3</span>
          </button>
          
          <div className="user-menu" ref={userMenuRef}>
            <button 
              className="user-avatar"
              onClick={() => setShowUserMenu(!showUserMenu)}
            >
              🩸
            </button>
            
            {showUserMenu && (
              <div className="user-dropdown">
                <div className="user-info">
                  <div className="user-name">{getUserDisplayName()}</div>
                  <div className="user-role">{getUserRole()}</div>
                </div>
                <hr />
                <button className="dropdown-item" onClick={handleLogout}>
                  🚪 Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header