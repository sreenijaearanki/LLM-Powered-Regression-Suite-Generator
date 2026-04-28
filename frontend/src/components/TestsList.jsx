import React, { useState } from 'react'

function TestsList({ tests }) {
  const [copied, setCopied] = useState(null)

  const handleCopy = (idx, code) => {
    navigator.clipboard.writeText(code)
    setCopied(idx)
    setTimeout(() => setCopied(null), 2000)
  }

  if (!tests || tests.length === 0) {
    return <p style={{ color: '#888', fontSize: '0.875rem' }}>No tests generated yet.</p>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {tests.map((test, idx) => (
        <div key={idx} style={{
          border: '1px solid #e5e7eb', borderRadius: '10px', overflow: 'hidden'
        }}>
          <div style={{
            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            padding: '0.75rem 1rem', background: '#f9fafb', borderBottom: '1px solid #e5e7eb'
          }}>
            <div>
              <span style={{ fontFamily: 'monospace', fontSize: '0.8rem', fontWeight: 600, color: '#111' }}>
                {test.name || `test_${idx + 1}`}
              </span>
              {test.priority && (
                <span style={{
                  marginLeft: '8px', fontSize: '0.7rem', padding: '1px 6px', borderRadius: '99px',
                  background: test.priority === 'high' ? '#fef2f2' : '#fefce8',
                  color: test.priority === 'high' ? '#dc2626' : '#ca8a04', fontWeight: 500
                }}>
                  {test.priority}
                </span>
              )}
            </div>
            <button onClick={() => handleCopy(idx, test.code || '')} style={{
              padding: '0.3rem 0.75rem', borderRadius: '6px', border: '1px solid #e5e7eb',
              cursor: 'pointer', fontSize: '0.75rem', background: '#fff',
              color: copied === idx ? '#16a34a' : '#555', fontWeight: 500
            }}>
              {copied === idx ? '✓ Copied' : 'Copy'}
            </button>
          </div>
          {test.description && (
            <p style={{ padding: '0.5rem 1rem', fontSize: '0.8rem', color: '#666', background: '#fff', margin: 0 }}>
              {test.description}
            </p>
          )}
          <pre style={{
            margin: 0, padding: '1rem', background: '#1e1e2e', color: '#cdd6f4',
            fontSize: '0.78rem', lineHeight: 1.6, overflowX: 'auto',
            fontFamily: 'monospace', whiteSpace: 'pre-wrap', wordBreak: 'break-word'
          }}>
            {test.code || ''}
          </pre>
        </div>
      ))}
    </div>
  )
}

export default TestsList
