import React, { useState, useEffect } from 'react'
import { API_BASE } from '../config'
import '../styles/JobStatus.css'
import ProgressBar from '../components/ProgressBar'
import TestsList from '../components/TestsList'

function JobStatus({ jobId, onNavigate }) {
  const [jobStatus, setJobStatus] = useState(null)
  const [tests, setTests] = useState([])
  const [loading, setLoading] = useState(true)
  const [polling, setPolling] = useState(true)
  const [exportFormat, setExportFormat] = useState('json')

  useEffect(() => {
    if (!jobId) {
      onNavigate('home')
      return
    }

    const pollJob = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/v1/jobs/${jobId}`)
        const data = await response.json()
        
        setJobStatus(data)
        setLoading(false)

        if (data.status === 'completed' || data.status === 'failed') {
          setPolling(false)

          // Fetch generated tests
          if (data.status === 'completed') {
            const testsResponse = await fetch(
              `${API_BASE}/api/v1/jobs/${jobId}/tests`
            )
            const testsData = await testsResponse.json()
            setTests(testsData.generated_tests || [])
          }
        }
      } catch (error) {
        console.error('Error fetching job status:', error)
      }
    }

    // Poll immediately and then every 2 seconds
    pollJob()
    
    if (polling) {
      const interval = setInterval(pollJob, 2000)
      return () => clearInterval(interval)
    }
  }, [jobId, polling, onNavigate])

  const handleDownload = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/v1/jobs/${jobId}`)
      const data = await response.json()

      const content = exportFormat === 'json' 
        ? JSON.stringify(data.result, null, 2)
        : exportFormat === 'md'
        ? formatAsMarkdown(data.result)
        : formatAsHTML(data.result)

      const element = document.createElement('a')
      const file = new Blob([content], {
        type: exportFormat === 'json' ? 'application/json' : 'text/plain'
      })
      element.href = URL.createObjectURL(file)
      element.download = `test-results.${exportFormat === 'json' ? 'json' : exportFormat === 'md' ? 'md' : 'html'}`
      document.body.appendChild(element)
      element.click()
      document.body.removeChild(element)
    } catch (error) {
      console.error('Error downloading results:', error)
    }
  }

  const formatAsMarkdown = (result) => {
    let md = '# Test Generation Results\n\n'
    
    if (result?.pr_info) {
      md += '## PR Information\n'
      md += `- **Title**: ${result.pr_info.title}\n`
      md += `- **Author**: ${result.pr_info.author}\n`
      md += `- **Files Changed**: ${result.pr_info.changed_files}\n\n`
    }

    if (result?.generated_tests) {
      md += '## Generated Tests\n\n'
      result.generated_tests.forEach((test, idx) => {
        md += `### Test ${idx + 1}: ${test.name}\n\n`
        md += '```python\n' + test.code + '\n```\n\n'
      })
    }

    return md
  }

  const formatAsHTML = (result) => {
    return `<!DOCTYPE html>
<html>
<head>
    <title>Test Results</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .test { background: #f5f5f5; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Test Generation Results</h1>
    <p>Generated ${result?.generated_tests?.length || 0} tests</p>
</body>
</html>`
  }

  if (loading) {
    return (
      <div className="job-status-container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading job information...</p>
        </div>
      </div>
    )
  }

  if (!jobStatus) {
    return (
      <div className="job-status-container">
        <div className="error-message">
          <h2>Job Not Found</h2>
          <p>The requested job ID was not found.</p>
          <button onClick={() => onNavigate('dashboard')}>Back to Dashboard</button>
        </div>
      </div>
    )
  }

  return (
    <div className="job-status-container">
      <div className="status-header">
        <div className="status-info">
          <h1>Job Status: {jobStatus.job_id.substring(0, 8)}...</h1>
          <div className={`status-badge status-${jobStatus.status}`}>
            {jobStatus.status.toUpperCase()}
          </div>
        </div>

        <div className="header-actions">
          {jobStatus.status === 'completed' && (
            <div className="export-controls">
              <select value={exportFormat} onChange={(e) => setExportFormat(e.target.value)}>
                <option value="json">JSON</option>
                <option value="md">Markdown</option>
                <option value="html">HTML</option>
              </select>
              <button className="btn-download" onClick={handleDownload}>
                ⬇ Download
              </button>
            </div>
          )}
        </div>
      </div>

      <div className="progress-section">
        <h2>Generation Progress</h2>
        <ProgressBar progress={jobStatus.progress} status={jobStatus.status} />
        <p className="progress-text">{jobStatus.progress}% Complete</p>
      </div>

      {jobStatus.error && (
        <div className="error-banner">
          <strong>Error:</strong> {jobStatus.error}
        </div>
      )}

      {jobStatus.result && (
        <>
          <div className="results-section">
            <h2>Analysis Results</h2>
            
            {jobStatus.result.pr_info && (
              <div className="pr-info-card">
                <h3>Pull Request Information</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <label>Title</label>
                    <p>{jobStatus.result.pr_info.title}</p>
                  </div>
                  <div className="info-item">
                    <label>Author</label>
                    <p>{jobStatus.result.pr_info.author}</p>
                  </div>
                  <div className="info-item">
                    <label>Files Changed</label>
                    <p>{jobStatus.result.pr_info.changed_files}</p>
                  </div>
                  <div className="info-item">
                    <label>Additions</label>
                    <p>+{jobStatus.result.pr_info.additions}</p>
                  </div>
                  <div className="info-item">
                    <label>Deletions</label>
                    <p>-{jobStatus.result.pr_info.deletions}</p>
                  </div>
                  <div className="info-item">
                    <label>Status</label>
                    <p>{jobStatus.result.pr_info.state}</p>
                  </div>
                </div>
              </div>
            )}

            {jobStatus.result.test_summary && (
              <div className="test-summary-card">
                <h3>Test Summary</h3>
                <div className="summary-grid">
                  <div className="summary-item">
                    <div className="summary-label">Tests Generated</div>
                    <div className="summary-value">
                      {jobStatus.result.test_summary.total_tests_generated}
                    </div>
                  </div>
                  <div className="summary-item">
                    <div className="summary-label">Framework</div>
                    <div className="summary-value">
                      {jobStatus.result.test_summary.framework}
                    </div>
                  </div>
                  <div className="summary-item">
                    <div className="summary-label">Functions Covered</div>
                    <div className="summary-value">
                      {jobStatus.result.test_summary.functions_covered}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {tests.length > 0 && (
            <div className="tests-section">
              <h2>Generated Test Cases ({tests.length})</h2>
              <TestsList tests={tests} />
            </div>
          )}

          {tests.length === 0 && jobStatus.result && (
            <div style={{background:'#fef2f2',border:'1px solid #fecaca',borderRadius:'10px',padding:'1.25rem',marginTop:'1rem'}}>
              <strong style={{color:'#dc2626'}}>⚠ No tests generated</strong>
              {jobStatus.result.llm_errors && jobStatus.result.llm_errors.length > 0 ? (
                <div style={{marginTop:'0.5rem',fontSize:'0.875rem',color:'#444'}}>
                  <strong>LLM Error:</strong> {jobStatus.result.llm_errors.join('; ')}
                </div>
              ) : (
                <p style={{marginTop:'0.5rem',fontSize:'0.875rem',color:'#666'}}>
                  The LLM call failed silently. Check that OPENAI_API_KEY is set correctly on Render.
                  Visit <code>/api/v1/test-llm</code> on the backend to diagnose.
                </p>
              )}
            </div>
          )}
        </>
      )}

      <div className="status-actions">
        <button className="btn-back" onClick={() => onNavigate('dashboard')}>
          ← Back to Dashboard
        </button>
        {jobStatus.status !== 'completed' && (
          <button className="btn-refresh" onClick={() => setPolling(true)}>
            🔄 Refresh
          </button>
        )}
      </div>
    </div>
  )
}

export default JobStatus
