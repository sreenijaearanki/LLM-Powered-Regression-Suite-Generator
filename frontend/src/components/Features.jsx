import React from 'react'

const features = [
  { icon: '🔍', title: 'PR Analysis', desc: 'Reads GitHub PR diffs and extracts changed functions automatically' },
  { icon: '🤖', title: 'LLM-Powered', desc: 'Uses GPT-4 or Gemini to understand code context and intent' },
  { icon: '🧪', title: 'Multi-Framework', desc: 'Generates pytest, unittest, Jest, or JUnit test cases' },
  { icon: '⚡', title: 'Async Processing', desc: 'Background job processing with real-time progress tracking' },
  { icon: '📤', title: 'Export Ready', desc: 'Download results as JSON, Markdown, or HTML' },
  { icon: '🔒', title: 'Secure', desc: 'API keys via env vars only — no data stored externally' },
]

function Features() {
  return (
    <div>
      <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', color: '#111' }}>
        What it does
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {features.map(({ icon, title, desc }) => (
          <div key={title} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start' }}>
            <span style={{ fontSize: '1.1rem', marginTop: '1px' }}>{icon}</span>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.875rem', color: '#111' }}>{title}</div>
              <div style={{ fontSize: '0.8rem', color: '#666', marginTop: '2px' }}>{desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Features
