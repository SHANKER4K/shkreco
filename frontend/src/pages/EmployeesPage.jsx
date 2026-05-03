import React, { useState, useEffect } from 'react'
import axios from 'axios'
import EmployeeRow from '../components/EmployeeRow'

export default function EmployeesPage({ onNavigate, onAddEmployeeClick }) {
  const [workers, setWorkers] = useState([])

  useEffect(() => {
    axios.get('http://localhost:8000/api/workers')
      .then(res => setWorkers(res.data))
      .catch(err => console.error(err))
  }, [])

  const handleDelete = (name) => {
    setWorkers(prev => prev.filter(w => w.name !== name))
  }

  return (
    <div style={{ padding: '32px 40px', maxWidth: 800, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 20, fontWeight: 600 }}>Employees ({workers.length})</h2>
        <button className="btn" onClick={() => { onNavigate('attendance'); if(onAddEmployeeClick) onAddEmployeeClick(); }}>+ Add Employee</button>
      </div>

      <div style={{
        background: 'var(--bg-surface)',
        border: '1px solid var(--bg-border)',
        borderRadius: 8, overflow: 'hidden'
      }}>
        {workers.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '80px 0', color: 'var(--text-2)' }}>
            <p>No employees registered yet.</p>
            <button className="btn-outline" style={{ marginTop: 16 }}
              onClick={() => { onNavigate('attendance'); if(onAddEmployeeClick) onAddEmployeeClick(); }}>
              + Add Employee
            </button>
          </div>
        ) : (
          workers.map(w => (
            <EmployeeRow key={w.name} worker={w} onDelete={handleDelete} />
          ))
        )}
      </div>
    </div>
  )
}
