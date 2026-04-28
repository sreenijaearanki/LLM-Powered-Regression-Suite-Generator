import React from 'react'

function Navbar({ currentPage, onNavigate }) {
  return (
    <nav style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0.75rem 2rem', borderBottom: '1px solid #e5e7eb',
      background: '#fff', position: 'sticky', top: 0, zIndex: 100
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}
           onClick={() => onNavigate('home')}>
        <span style={{ fontSize: '1.25rem' }}>🧪</span>
        <span style={{ fontWeight: 700, fontSize: '1rem', color: '#111' }}>
          LLM Regression Suite
        </span>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        {[
          { id: 'home', label: 'Home' },
          { id: 'dashboard', label: 'Dashboard' },
          { id: 'docs', label: 'Docs' },
        ].map(({ id, label }) => (
          <button key={id} onClick={() => onNavigate(id)} style={{
            padding: '0.4rem 1rem', borderRadius: '6px', border: 'none',
            cursor: 'pointer', fontWeight: 500, fontSize: '0.875rem',
            background: currentPage === id ? '#111' : 'transparent',
            color: currentPage === id ? '#fff' : '#555',
          }}>
            {label}
          </button>
        ))}
      </div>
    </nav>
  )
}

export default Navbar
