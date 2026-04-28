import React, { useState, useEffect } from 'react'
import '../styles/Dashboard.css'
import JobCard from '../components/JobCard'

function Dashboard({ onNavigate }) {
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all') // all, completed, processing, failed

  useEffect(() => {
    // In a real app, fetch from API: /api/v1/jobs
    // For now, load from localStorage
    const savedJobs = localStorage.getItem('regression_jobs')
    if (savedJobs) {
      setJobs(JSON.parse(savedJobs))
    }
    setLoading(false)
  }, [])

  const filteredJobs = jobs.filter(job => {
    if (filter === 'all') return true
    return job.status === filter
  })

  const handleViewJob = (jobId) => {
    onNavigate('job-status', jobId)
  }

  const handleDeleteJob = (jobId) => {
    const confirmed = window.confirm('Are you sure you want to delete this job?')
    if (confirmed) {
      const updated = jobs.filter(j => j.job_id !== jobId)
      setJobs(updated)
      localStorage.setItem('regression_jobs', JSON.stringify(updated))
    }
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Test Generation Dashboard</h1>
        <p>View and manage all your test generation jobs</p>
      </div>

      <div className="dashboard-controls">
        <div className="filter-buttons">
          <button 
            className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
            onClick={() => setFilter('all')}
          >
            All Jobs ({jobs.length})
          </button>
          <button 
            className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
            onClick={() => setFilter('completed')}
          >
            Completed ({jobs.filter(j => j.status === 'completed').length})
          </button>
          <button 
            className={`filter-btn ${filter === 'processing' ? 'active' : ''}`}
            onClick={() => setFilter('processing')}
          >
            Processing ({jobs.filter(j => j.status === 'processing').length})
          </button>
          <button 
            className={`filter-btn ${filter === 'failed' ? 'active' : ''}`}
            onClick={() => setFilter('failed')}
          >
            Failed ({jobs.filter(j => j.status === 'failed').length})
          </button>
        </div>
      </div>

      <div className="jobs-container">
        {loading ? (
          <div className="loading-spinner">Loading jobs...</div>
        ) : filteredJobs.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📭</div>
            <h3>No jobs found</h3>
            <p>Start generating regression tests from a GitHub PR</p>
          </div>
        ) : (
          <div className="jobs-grid">
            {filteredJobs.map(job => (
              <JobCard
                key={job.job_id}
                job={job}
                onView={handleViewJob}
                onDelete={handleDeleteJob}
              />
            ))}
          </div>
        )}
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-label">Total Jobs</div>
          <div className="stat-value">{jobs.length}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Success Rate</div>
          <div className="stat-value">
            {jobs.length > 0 
              ? `${Math.round((jobs.filter(j => j.status === 'completed').length / jobs.length) * 100)}%`
              : '-'
            }
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Tests Generated</div>
          <div className="stat-value">
            {jobs.length > 0 
              ? Math.round(
                  jobs.filter(j => j.result?.test_summary).reduce(
                    (sum, j) => sum + (j.result?.test_summary?.total_tests_generated || 0), 0
                  ) / jobs.filter(j => j.result?.test_summary).length
                ) || 0
              : '-'
            }
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
