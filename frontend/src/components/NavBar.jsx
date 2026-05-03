import React from 'react'

export default function NavBar({ currentPage, onNavigate, cameraActive, mode, addingName }) {
  const getTitle = () => {
    if (mode === 'adding') {
      return `Adding Employee: ${addingName ? addingName.replace(/_/g, ' ') : ''}`
    }
    return 'Attendance'
  }

  return (
    <nav style={{
      height: 56,
      background: 'var(--bg-surface)',
      borderBottom: '1px solid var(--bg-border)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 28px',
      position: 'fixed',
      top: 0, left: 0, right: 0,
      gap: 40,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', fontWeight: 600, fontSize: 16 }}>
        ENIE
        <span style={{ color: 'var(--teal)', marginLeft: 4 }}>•</span>
      </div>

      <div style={{ flex: 1, fontSize: 14, color: 'var(--text-2)' }}>
        {getTitle()}
      </div>

      <div style={{ display: 'flex', gap: 24 }}>
        <button 
          onClick={() => onNavigate('attendance')}
          style={{
            background: 'none', border: 'none',
            color: currentPage === 'attendance' ? 'var(--teal)' : 'var(--text-2)',
            fontWeight: currentPage === 'attendance' ? 600 : 400,
            fontSize: 14,
            display: 'flex', alignItems: 'center', gap: 8
          }}
          disabled={mode === 'adding'}
        >
          Attendance
          {cameraActive && mode === 'recognition' && <span className="live-dot"></span>}
        </button>

        <button 
          onClick={() => onNavigate('employees')}
          style={{
            background: 'none', border: 'none',
            color: currentPage === 'employees' ? 'var(--teal)' : 'var(--text-2)',
            fontWeight: currentPage === 'employees' ? 600 : 400,
            fontSize: 14
          }}
          disabled={mode === 'adding'}
        >
          Employees
        </button>
      </div>
    </nav>
  )
}
