import React, { useState } from 'react'
import '../styles/PRForm.css'

function PRForm({ onSubmit, isLoading }) {
  const [formData, setFormData] = useState({
    github_url: '',
    github_token: '',
    llm_provider: 'openai',
    llm_api_key: '',
    test_framework: 'pytest',
    output_format: 'pytest'
  })

  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.github_url.trim()) {
      newErrors.github_url = 'GitHub PR URL is required'
    } else if (!formData.github_url.includes('github.com') || !formData.github_url.includes('pull')) {
      newErrors.github_url = 'Please enter a valid GitHub PR URL'
    }

    // LLM API key is optional — server uses env var if not provided

    return newErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const newErrors = validateForm()
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      return
    }

    // Save to localStorage for dashboard display
    const jobData = {
      ...formData,
      job_id: Date.now().toString(),
      status: 'processing',
      progress: 0,
      created_at: new Date().toISOString()
    }

    const savedJobs = JSON.parse(localStorage.getItem('regression_jobs') || '[]')
    savedJobs.unshift(jobData)
    localStorage.setItem('regression_jobs', JSON.stringify(savedJobs))

    await onSubmit(formData)
  }

  return (
    <form className="pr-form" onSubmit={handleSubmit}>
      <h2>Generate Regression Tests</h2>

      <div className="form-group">
        <label htmlFor="github_url">
          GitHub PR URL *
          <span className="help-text">e.g., https://github.com/owner/repo/pull/123</span>
        </label>
        <input
          id="github_url"
          type="text"
          name="github_url"
          placeholder="https://github.com/..."
          value={formData.github_url}
          onChange={handleChange}
          disabled={isLoading}
          className={errors.github_url ? 'error' : ''}
        />
        {errors.github_url && <span className="error-text">{errors.github_url}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="github_token">
          GitHub Token (Optional)
          <span className="help-text">For private repositories</span>
        </label>
        <input
          id="github_token"
          type="password"
          name="github_token"
          placeholder="ghp_..."
          value={formData.github_token}
          onChange={handleChange}
          disabled={isLoading}
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="llm_provider">
            LLM Provider *
          </label>
          <select
            id="llm_provider"
            name="llm_provider"
            value={formData.llm_provider}
            onChange={handleChange}
            disabled={isLoading}
          >
            <option value="openai">OpenAI (GPT-4)</option>
            <option value="gemini">Google Gemini</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="llm_api_key">
            LLM API Key
            <span className="help-text">Leave blank — uses server key</span>
          </label>
          <input
            id="llm_api_key"
            type="password"
            name="llm_api_key"
            placeholder="Optional — server key used if blank"
            value={formData.llm_api_key}
            onChange={handleChange}
            disabled={isLoading}
            className={errors.llm_api_key ? 'error' : ''}
          />
          {errors.llm_api_key && <span className="error-text">{errors.llm_api_key}</span>}
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label htmlFor="test_framework">
            Test Framework *
          </label>
          <select
            id="test_framework"
            name="test_framework"
            value={formData.test_framework}
            onChange={handleChange}
            disabled={isLoading}
          >
            <option value="pytest">pytest (Python)</option>
            <option value="unittest">unittest (Python)</option>
            <option value="jest">Jest (JavaScript/TypeScript)</option>
            <option value="junit">JUnit (Java)</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="output_format">
            Output Format
          </label>
          <select
            id="output_format"
            name="output_format"
            value={formData.output_format}
            onChange={handleChange}
            disabled={isLoading}
          >
            <option value="pytest">Python (pytest)</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
          </select>
        </div>
      </div>

      <div className="form-info">
        <div className="info-icon">ℹ️</div>
        <div>
          <p><strong>How it works:</strong></p>
          <ul>
            <li>Enter a GitHub PR URL to analyze code changes</li>
            <li>Select an LLM provider (GPT-4 recommended for best results)</li>
            <li>Choose your preferred test framework</li>
            <li>We'll generate comprehensive regression tests automatically</li>
          </ul>
        </div>
      </div>

      <button 
        type="submit" 
        className="btn-submit"
        disabled={isLoading}
      >
        {isLoading ? (
          <>
            <span className="spinner"></span>
            Generating Tests...
          </>
        ) : (
          '✨ Generate Tests'
        )}
      </button>

      <p className="form-disclaimer">
        * Required fields. Your PR data is analyzed locally and not stored.
      </p>
    </form>
  )
}

export default PRForm
