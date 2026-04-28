import React, { useState } from 'react'
import '../styles/Documentation.css'

function Documentation() {
  const [activeTab, setActiveTab] = useState('setup')

  return (
    <div className="docs-container">
      <div className="docs-header">
        <h1>Documentation</h1>
        <p>Complete guide to using the LLM Regression Suite Generator</p>
      </div>

      <div className="docs-nav">
        <button 
          className={`doc-tab ${activeTab === 'setup' ? 'active' : ''}`}
          onClick={() => setActiveTab('setup')}
        >
          Setup & Installation
        </button>
        <button 
          className={`doc-tab ${activeTab === 'usage' ? 'active' : ''}`}
          onClick={() => setActiveTab('usage')}
        >
          Usage Guide
        </button>
        <button 
          className={`doc-tab ${activeTab === 'api' ? 'active' : ''}`}
          onClick={() => setActiveTab('api')}
        >
          API Reference
        </button>
        <button 
          className={`doc-tab ${activeTab === 'examples' ? 'active' : ''}`}
          onClick={() => setActiveTab('examples')}
        >
          Examples
        </button>
        <button 
          className={`doc-tab ${activeTab === 'faq' ? 'active' : ''}`}
          onClick={() => setActiveTab('faq')}
        >
          FAQ
        </button>
      </div>

      <div className="docs-content">
        {activeTab === 'setup' && (
          <div className="doc-section">
            <h2>Setup & Installation</h2>
            
            <h3>Backend Setup</h3>
            <div className="code-block">
              <pre>{`# Clone the repository
git clone https://github.com/sreenijaearanki/LLM-Powered-Regression-Suite-Generator.git
cd LLM-Powered-Regression-Suite-Generator

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"
export GITHUB_TOKEN="your-github-token"

# Run the backend server
python -m uvicorn main:app --host 0.0.0.0 --port 8000`}</pre>
            </div>

            <h3>Frontend Setup</h3>
            <div className="code-block">
              <pre>{`# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev`}</pre>
            </div>

            <h3>Configuration</h3>
            <ul>
              <li><strong>OpenAI:</strong> Set OPENAI_API_KEY environment variable with your API key</li>
              <li><strong>Gemini:</strong> Set GEMINI_API_KEY environment variable with your API key</li>
              <li><strong>GitHub:</strong> Optional GITHUB_TOKEN for private repositories</li>
            </ul>
          </div>
        )}

        {activeTab === 'usage' && (
          <div className="doc-section">
            <h2>Usage Guide</h2>
            
            <h3>Basic Workflow</h3>
            <ol>
              <li>Navigate to the home page</li>
              <li>Enter a GitHub PR URL (e.g., https://github.com/owner/repo/pull/123)</li>
              <li>Select your preferred LLM provider (GPT-4 or Gemini)</li>
              <li>Choose the test framework (pytest, unittest, jest, etc.)</li>
              <li>Click "Generate Tests"</li>
              <li>Monitor progress in real-time</li>
              <li>Download or view generated tests</li>
            </ol>

            <h3>Supported PR URL Formats</h3>
            <div className="code-block">
              <pre>{`# Standard GitHub URL
https://github.com/owner/repo/pull/123

# API URL
https://api.github.com/repos/owner/repo/pulls/123`}</pre>
            </div>

            <h3>Test Frameworks</h3>
            <table className="docs-table">
              <thead>
                <tr>
                  <th>Framework</th>
                  <th>Language</th>
                  <th>Best For</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>pytest</td>
                  <td>Python</td>
                  <td>Python projects, comprehensive testing</td>
                </tr>
                <tr>
                  <td>unittest</td>
                  <td>Python</td>
                  <td>Standard library testing</td>
                </tr>
                <tr>
                  <td>jest</td>
                  <td>JavaScript/TypeScript</td>
                  <td>Frontend and Node.js projects</td>
                </tr>
                <tr>
                  <td>junit</td>
                  <td>Java</td>
                  <td>Java applications</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'api' && (
          <div className="doc-section">
            <h2>API Reference</h2>

            <h3>Generate Tests</h3>
            <div className="endpoint">
              <div className="method-post">POST</div>
              <div className="url">/api/v1/generate-tests</div>
            </div>
            <p>Generate regression tests for a GitHub PR</p>
            <div className="code-block">
              <pre>{`Request Body:
{
  "github_url": "https://github.com/owner/repo/pull/123",
  "github_token": "optional-github-token",
  "llm_provider": "openai",  // or "gemini"
  "llm_api_key": "optional-api-key",
  "test_framework": "pytest",
  "output_format": "pytest"
}

Response:
{
  "status": "accepted",
  "job_id": "uuid-here",
  "message": "Test generation job queued"
}`}</pre>
            </div>

            <h3>Job Status</h3>
            <div className="endpoint">
              <div className="method-get">GET</div>
              <div className="url">/api/v1/jobs/{job_id}</div>
            </div>
            <p>Get the status of a test generation job</p>
            <div className="code-block">
              <pre>{`Response:
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 50,
  "result": { ... }
}`}</pre>
            </div>

            <h3>Get Generated Tests</h3>
            <div className="endpoint">
              <div className="method-get">GET</div>
              <div className="url">/api/v1/jobs/{job_id}/tests</div>
            </div>
            <p>Get the generated test cases for a completed job</p>
          </div>
        )}

        {activeTab === 'examples' && (
          <div className="doc-section">
            <h2>Examples</h2>

            <h3>Example 1: Python Project with pytest</h3>
            <div className="code-block">
              <pre>{`# Input PR
https://github.com/django/django/pull/12345

# Generated Test (sample)
import pytest
from mymodule import calculate_total

class TestCalculateTotal:
    def test_simple_calculation(self):
        result = calculate_total([1, 2, 3])
        assert result == 6
    
    def test_empty_list(self):
        result = calculate_total([])
        assert result == 0
    
    def test_negative_numbers(self):
        result = calculate_total([-1, -2, -3])
        assert result == -6`}</pre>
            </div>

            <h3>Example 2: JavaScript Project with Jest</h3>
            <div className="code-block">
              <pre>{`// Input PR
https://github.com/facebook/react/pull/56789

// Generated Test (sample)
describe('calculateTotal', () => {
  test('should sum array correctly', () => {
    expect(calculateTotal([1, 2, 3])).toBe(6);
  });

  test('should handle empty array', () => {
    expect(calculateTotal([])).toBe(0);
  });

  test('should handle negative numbers', () => {
    expect(calculateTotal([-1, -2, -3])).toBe(-6);
  });
});`}</pre>
            </div>
          </div>
        )}

        {activeTab === 'faq' && (
          <div className="doc-section">
            <h2>Frequently Asked Questions</h2>

            <div className="faq-item">
              <h3>How accurate are the generated tests?</h3>
              <p>
                The generated tests are about 85-90% accurate. They cover major code paths
                and edge cases identified by the LLM. We recommend reviewing and adjusting
                tests based on your specific business logic.
              </p>
            </div>

            <div className="faq-item">
              <h3>What's the difference between GPT-4 and Gemini?</h3>
              <p>
                <strong>GPT-4:</strong> More advanced, better code understanding, slightly higher cost
                <br/>
                <strong>Gemini:</strong> Good balance of quality and cost, faster responses
              </p>
            </div>

            <div className="faq-item">
              <h3>Can I use private GitHub repositories?</h3>
              <p>
                Yes! Set the GITHUB_TOKEN environment variable with a personal access token
                that has access to private repositories.
              </p>
            </div>

            <div className="faq-item">
              <h3>How long does test generation take?</h3>
              <p>
                Typically 30 seconds to 2 minutes depending on the PR size and complexity.
                Larger PRs with more functions take longer.
              </p>
            </div>

            <div className="faq-item">
              <h3>Can I modify the generated tests?</h3>
              <p>
                Absolutely! The generated tests are a starting point. You can modify, extend,
                or remove tests as needed for your project.
              </p>
            </div>

            <div className="faq-item">
              <h3>What happens to my data?</h3>
              <p>
                All processing happens on your own infrastructure. We don't store PR data
                unless you explicitly export results. Check our privacy policy for details.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Documentation
