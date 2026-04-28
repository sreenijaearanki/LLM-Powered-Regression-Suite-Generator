import React from 'react'

const statusColors = {
  completed: { bg: '#f0fdf4', color: '#16a34a' },
  processing: { bg: '#eff6ff', color: '#2563eb' },
  failed:     { bg: '#fef2f2', color: '#dc2626' },
}

function JobCard({ job, onView, onDelete }) {
  const s = statusColors[job.status] || { bg: '#f9fafb', color: '#555' }
  return (
    <div style={{
      background: '#fff', border: '1px solid #e5e7eb', borderRadius: '10px',
      padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ fontFamily: 'monospace', fontSize: '0.75rem', color: '#888' }}>
          {(job.job_id || '').substring(0, 12)}...
        </span>
        <span style={{
          fontSize: '0.7rem', fontWeight: 600, padding: '2px 8px', borderRadius: '99px',
          background: s.bg, color: s.color, textTransform: 'uppercase'
        }}>
          {job.status}
        </span>
      </div>
      <div style={{ fontSize: '0.875rem', fontWeight: 500, color: '#111', wordBreak: 'break-all' }}>
        {job.github_url || 'Unknown PR'}
      </div>
      <div style={{ fontSize: '0.75rem', color: '#888' }}>
        {job.created_at ? new Date(job.created_at).toLocaleString() : ''} · {job.test_framework || 'pytest'}
      </div>
      {job.status === 'processing' && (
        <div style={{ background: '#f3f4f6', borderRadius: '4px', height: '4px' }}>
          <div style={{ background: '#2563eb', height: '100%', borderRadius: '4px',
                        width: (job.progress || 0) + '%', transition: 'width 0.3s' }} />
        </div>
      )}
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.25rem' }}>
        <button onClick={() => onView(job.job_id)} style={{
          flex: 1, padding: '0.4rem', borderRadius: '6px', border: '1px solid #e5e7eb',
          cursor: 'pointer', fontSize: '0.8rem', fontWeight: 500, background: '#fff'
        }}>
          View
        </button>
        <button onClick={() => onDelete(job.job_id)} style={{
          padding: '0.4rem 0.75rem', borderRadius: '6px', border: '1px solid #fee2e2',
          cursor: 'pointer', fontSize: '0.8rem', background: '#fef2f2', color: '#dc2626'
        }}>
          Delete
        </button>
      </div>
    </div>
  )
}

export default JobCard
