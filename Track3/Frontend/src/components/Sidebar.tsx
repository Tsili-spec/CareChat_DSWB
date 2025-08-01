import './Sidebar.css'

interface SidebarProps {
  activeSection: string
  onSectionChange: (section: string) => void
}

const Sidebar = ({ activeSection, onSectionChange }: SidebarProps) => {
  const menuItems = [
    { id: 'dashboard', label: 'Analytics Dashboard', icon: '📊' },
    { id: 'collections', label: 'Blood Collections', icon: '🩸' },
    { id: 'usage', label: 'Blood Usage', icon: '💉' },
    { id: 'inventory', label: 'Blood Inventory', icon: '🏥' },
    { id: 'low-stock', label: 'Low Stock Alerts', icon: '⚠️' },
    { id: 'donors', label: 'Donor Management', icon: '👥' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ]

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo">🩸</div>
        <h2>Blood Bank</h2>
        <p>Management System</p>
      </div>
      
      <nav className="sidebar-nav">
        {menuItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeSection === item.id ? 'active' : ''}`}
            onClick={() => onSectionChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.label}</span>
          </button>
        ))}
      </nav>
      
      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">👤</div>
          <div className="user-details">
            <div className="user-name">John Doe</div>
            <div className="user-role">Admin</div>
          </div>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar