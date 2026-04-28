import React from 'react'

const statusColor = {
  completed: '#16a34a',
  failed:    '#dc2626',
  processing:'#2563eb',
}

function ProgressBar({ progress, status }) {
  const color = statusColor[status] || '#2563eb'
  return (
    <div style={{ width: '100%' }}>
      <div style={{ background: '#f3f4f6', borderRadius: '99px', height: '8px', overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: '99px', background: color,
          width: `${Math.min(progress, 100)}%`, transition: 'width 0.4s ease'
        }} />
      </div>
    </div>
  )
}

export default ProgressBar
