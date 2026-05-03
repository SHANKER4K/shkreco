import { useState } from 'react'
import NavBar from './components/NavBar'
import AttendancePage from './pages/AttendancePage'
import EmployeesPage from './pages/EmployeesPage'

export default function App() {
  const [page, setPage] = useState('attendance')
  const [cameraActive, setCameraActive] = useState(false)
  const [triggerAddEmployee, setTriggerAddEmployee] = useState(false)
  const [mode, setMode] = useState('recognition')
  const [addingName, setAddingName] = useState('')

  return (
    <div style={{ background: 'var(--bg-base)', minHeight: '100vh', width: '100%' }}>
      <NavBar
        currentPage={page}
        onNavigate={setPage}
        cameraActive={cameraActive}
        mode={mode}
        addingName={addingName}
      />
      <div style={{ paddingTop: 56 }}>
        {page === 'attendance'
          ? <AttendancePage 
              onCameraActive={setCameraActive} 
              addingEmployeeMode={triggerAddEmployee}
              onExitAddingEmployee={() => setTriggerAddEmployee(false)}
              mode={mode}
              setMode={setMode}
              addingName={addingName}
              setAddingName={setAddingName}
            />
          : <EmployeesPage 
              onNavigate={setPage} 
              onAddEmployeeClick={() => setTriggerAddEmployee(true)} 
            />
        }
      </div>
    </div>
  )
}
