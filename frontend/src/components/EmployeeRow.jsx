import React from 'react'

export default function EmployeeRow({ worker, onDelete }) {
  const displayName = worker.name.replace(/_/g, ' ')

  const handleDelete = () => {
    if (window.confirm(`Delete ${displayName}?`)) {
      fetch(`http://localhost:8000/api/workers/${worker.name}`, { method: 'DELETE' })
        .then(() => onDelete(worker.name))
        .catch(err => console.error(err))
    }
  }

  return (
    <div className="employee-row">
      <img
        src={`http://localhost:8000/api/workers/${worker.name}/photo`}
        onError={(e) => { e.target.style.display = 'none'; }}
        style={{ width: 40, height: 40, borderRadius: '50%', objectFit: 'cover' }}
        alt={displayName}
      />
      <div>
        <div style={{ fontWeight: 500, color: 'var(--text-1)' }}>{displayName}</div>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--text-2)' }}>
          {worker.photo_count} photos · {worker.id}
        </div>
      </div>
      <button className="delete-btn" onClick={handleDelete}>
        [✕]
      </button>
    </div>
  )
}
