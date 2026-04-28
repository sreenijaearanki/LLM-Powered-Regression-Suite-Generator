import React, { useState } from 'react'
import '../styles/Home.css'
import PRForm from '../components/PRForm'
import Features from '../components/Features'

function Home({ onNavigate }) {
  const [isLoading, setIsLoading] = useState(false)

  const handleFormSubmit = async (formData) => {
    setIsLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/v1/generate-tests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      const data = await response.json()
      
      if (data.job_id) {
        // Navigate to job status page
        onNavigate('job-status', data.job_id)
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error starting test generation: ' + error.message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1 className="hero-title">LLM-Powered Regression Suite Generator</h1>
        <p className="hero-subtitle">
          Automatically generate comprehensive regression tests from GitHub pull requests
          using advanced AI models (GPT-4, Gemini)
        </p>
      </div>

      <div className="content-grid">
        <div className="form-section">
          <PRForm onSubmit={handleFormSubmit} isLoading={isLoading} />
        </div>
        
        <div className="features-section">
          <Features />
        </div>
      </div>

      <div className="benefits-section">
        <h2>Why Use Our Tool?</h2>
        <div className="benefits-grid">
          <div className="benefit-card">
            <div className="benefit-icon">⚡</div>
            <h3>Fast Test Generation</h3>
            <p>Generate comprehensive test suites in minutes, not days</p>
          </div>
          <div className="benefit-card">
            <div className="benefit-icon">🤖</div>
            <h3>AI-Powered Analysis</h3>
            <p>Uses GPT-4 and Gemini for intelligent test case creation</p>
          </div>
          <div className="benefit-card">
            <div className="benefit-icon">🎯</div>
            <h3>Smart Coverage</h3>
            <p>Analyzes code changes to identify critical test paths</p>
          </div>
          <div className="benefit-card">
            <div className="benefit-icon">📊</div>
            <h3>Multiple Frameworks</h3>
            <p>Support for pytest, unittest, jest, and JUnit</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
