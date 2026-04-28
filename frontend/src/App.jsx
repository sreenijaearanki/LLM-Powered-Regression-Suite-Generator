import React, { useState } from 'react'
import './App.css'
import Home from './pages/Home'
import Dashboard from './pages/Dashboard'
import JobStatus from './pages/JobStatus'
import Documentation from './pages/Documentation'
import Navbar from './components/Navbar'

function App() {
  const [currentPage, setCurrentPage] = useState('home')
  const [selectedJobId, setSelectedJobId] = useState(null)

  const navigateTo = (page, jobId = null) => {
    setCurrentPage(page)
    if (jobId) setSelectedJobId(jobId)
  }

  return (
    <div className="app">
      <Navbar currentPage={currentPage} onNavigate={navigateTo} />
      
      <main className="main-content">
        {currentPage === 'home' && <Home onNavigate={navigateTo} />}
        {currentPage === 'dashboard' && <Dashboard onNavigate={navigateTo} />}
        {currentPage === 'job-status' && <JobStatus jobId={selectedJobId} onNavigate={navigateTo} />}
        {currentPage === 'docs' && <Documentation />}
      </main>

      <footer className="app-footer">
        <p>&copy; 2026 LLM Regression Suite Generator. All rights reserved.</p>
      </footer>
    </div>
  )
}

export default App
