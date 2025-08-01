import { useState } from 'react'
import Sidebar from './Sidebar'
import Header from './Header'
import Dashboard from './Dashboard'
import '../App.css'

const DashboardLayout = () => {
  const [activeSection, setActiveSection] = useState('dashboard')

  return (
    <div className="app">
      <Sidebar activeSection={activeSection} onSectionChange={setActiveSection} />
      <div className="main-content">
        <Header />
        <main className="content">
          <Dashboard activeSection={activeSection} />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout