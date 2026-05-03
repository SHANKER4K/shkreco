# ShkReco Frontend 🎨

**Facial Recognition Attendance System UI** — React/Vite-based web interface for real-time face detection, employee registration, and attendance tracking.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Components](#components)
- [Pages](#pages)
- [State Management](#state-management)
- [WebSocket Integration](#websocket-integration)
- [Running the App](#running-the-app)
- [Styling System](#styling-system)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**ShkReco Frontend** is a modern React application that provides:

1. **Real-time Attendance Tracking**
   - Live camera feed with face detection
   - Automatic recognition of employees
   - Daily attendance count

2. **Employee Management**
   - View all registered employees
   - Delete employees from database
   - Browse employee photos

3. **Employee Registration**
   - Add new employees via webcam
   - Capture 15 diverse face photos
   - Auto-registration to database

**Key Features:**
- ✅ Real-time face detection overlay
- ✅ WebSocket live data streaming
- ✅ Responsive UI (Flexbox layout)
- ✅ Keyboard shortcuts (Spacebar for photo capture)
- ✅ Progress tracking (photo count)
- ✅ Live camera status indicator
- ✅ Clean, modern design (CSS variables)

---

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────────┐
│                    React App (App.jsx)                 │
│                                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │              NavBar Component                    │  │
│  │  - Fixed top bar (56px height)                   │  │
│  │  - Page navigation (Attendance / Employees)      │  │
│  │  - Mode indicator (Recognition / Adding)         │  │
│  │  - Live camera status dot                        │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Page Router (Conditional Render)        │  │
│  │                                                  │  │
│  │  ┌─────────────────┐      ┌─────────────────┐   │  │
│  │  │ Attendance Page │      │ Employees Page  │   │  │
│  │  │                 │      │                 │   │  │
│  │  │ ┌────┐ ┌─────┐ │      │ ┌─────────────┐ │   │  │
│  │  │ │Cam │ │Panel│ │      │ │   List      │ │   │  │
│  │  │ │Feed│ │     │ │      │ │ - Edit      │ │   │  │
│  │  │ │    │ │Stat │ │      │ │ - Delete    │ │   │  │
│  │  │ └────┘ │ us  │ │      │ │ - Photos    │ │   │  │
│  │  │        └─────┘ │      │ │             │ │   │  │
│  │  └─────────────────┘      └─────────────────┘   │  │
│  │        (60/40 split)       (100% width)        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
└────────────────────────────────────────────────────────┘
         │
         ├─→ WebSocket (ws://localhost:8000/ws/recognition)
         │   Real-time face detection + recognition data
         │
         └─→ HTTP APIs
             GET /api/stream (camera feed)
             GET /api/workers (employee list)
             POST /api/workers/capture-live (save photo)
             POST /api/workers/register (register employee)
             DELETE /api/workers/{name} (delete employee)
```

---

## 📦 Installation

### Prerequisites
- Node.js 18+ & npm/yarn
- Backend server running on `http://localhost:8000`
- Webcam access permissions

### Step 1: Install Dependencies

```bash
cd frontend
npm install
```

**Dependencies installed:**
- `react` (19.2.5) — UI framework
- `react-dom` (19.2.5) — React rendering
- `axios` (1.15.1) — HTTP client (if needed)
- `vite` (8.0.9) — Build tool

### Step 2: Verify Backend Connection

```bash
# Test backend API
curl http://localhost:8000/api/workers

# Test WebSocket
# (Will verify when app starts)
```

### Step 3: Run Development Server

```bash
npm run dev
# Server starts at http://localhost:5173 or http://localhost:5174
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.jsx                  # Entry point (renders App)
│   ├── index.css                 # Global styles (CSS variables)
│   ├── App.jsx                   # Root router & state management
│   │
│   ├── components/               # Reusable components
│   │   ├── NavBar.jsx            # Top navigation bar
│   │   ├── CameraFeed.jsx        # Camera stream + face bbox overlay
│   │   ├── StatusPanel.jsx       # Attendance/registration status display
│   │   └── EmployeeRow.jsx       # Single employee list item
│   │
│   ├── pages/                    # Page-level components
│   │   ├── AttendancePage.jsx    # Main recognition page
│   │   └── EmployeesPage.jsx     # Employee management page
│   │
│   └── assets/                   # Images, icons
│       ├── react.svg
│       ├── vite.svg
│       └── hero.png
│
├── public/
│   ├── favicon.svg
│   └── icons.svg
│
├── index.html                    # HTML template
├── vite.config.js                # Build config
├── package.json                  # Dependencies
├── eslint.config.js              # Linting rules
└── README.md                      # This file
```

---

## ⚙️ Configuration

### Backend URL

**File:** `src/components/CameraFeed.jsx` (Line 14)
```javascript
src="http://localhost:8000/api/stream"
```

**File:** `src/pages/AttendancePage.jsx` (Line 52)
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/recognition')
```

**To change server URL, update both files:**
```javascript
// Example: Production server
// src="http://api.example.com/api/stream"
// ws('wss://api.example.com/ws/recognition')
```

### CSS Variables

**File:** `src/index.css`

```css
:root {
  /* Colors */
  --teal: #14B8A6;
  --teal-dim: rgba(20, 184, 166, 0.1);
  --green: #10B981;
  --green-dim: rgba(16, 185, 129, 0.1);
  --red: #EF4444;
  --red-dim: rgba(239, 68, 68, 0.1);

  /* Backgrounds */
  --bg-base: #0F172A;      /* Page background */
  --bg-surface: #1E293B;   /* Cards, surfaces */
  --bg-elevated: #334155;  /* Elevated surfaces */
  --bg-border: #475569;    /* Borders */

  /* Text */
  --text-1: #F1F5F9;       /* Primary text */
  --text-2: #CBD5E1;       /* Secondary text */

  /* Fonts */
  --font-base: 'Sora', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Sizes */
  --radius: 8px;
  --gap: 20px;
}
```

---

## 🧩 Components

### **1. NavBar.jsx**
**Purpose:** Top navigation bar (fixed, 56px height)

**Props:**
- `currentPage` (string) — Active page ('attendance' | 'employees')
- `onNavigate` (function) — Page change callback
- `cameraActive` (boolean) — Camera streaming status
- `mode` (string) — Current mode ('recognition' | 'adding')
- `addingName` (string) — Employee name being added

**Features:**
- Brand name "ENIE"
- Page navigation buttons
- Live indicator dot (pulsing when camera active)
- Mode-aware title

**Code:**
```jsx
<NavBar
  currentPage={page}
  onNavigate={setPage}
  cameraActive={cameraActive}
  mode={mode}
  addingName={addingName}
/>
```

---

### **2. CameraFeed.jsx**
**Purpose:** Display live camera stream with face detection overlay

**Props:**
- `onCameraActive` (function) — Called when stream loads/fails
- `faceBox` (array | null) — Bounding box [x, y, w, h]

**Features:**
- Streams images from `/api/stream`
- Canvas overlay draws green rectangle around detected face
- Auto-scales coordinates to match display size
- Responsive (100% width, 4:3 aspect ratio)

**State:**
- `canvasRef` — Canvas element reference
- `imgRef` — Image element reference

**Flow:**
```
1. <img> loads stream
2. Canvas resizes to match image
3. If faceBox exists:
   - Scale coordinates (naturalWidth/displayWidth)
   - Draw rectangle (strokeStyle: teal, lineWidth: 3)
   - Draw label "Face Detected"
```

**Code:**
```jsx
<CameraFeed 
  onCameraActive={setCameraActive} 
  faceBox={faceBox} 
/>
```

---

### **3. StatusPanel.jsx**
**Purpose:** Display attendance stats or registration progress

**Props:**
- `lastRecognition` (object) — {name, confidence, time, status, bbox}
- `totalToday` (number) — Attendance count today
- `faceDetected` (boolean) — Is a face currently detected?
- `mode` (string) — 'recognition' | 'adding'
- `captureProgress` (number) — Photos captured (0-15)
- `onCapture` (function) — Manual capture button callback
- `onCancel` (function) — Cancel registration callback

**Recognition Mode Display:**
```
┌──────────────────────────┐
│ ● Face Detected          │  ← Status (green = face, red = no face)
├──────────────────────────┤
│ 📋 Instructions          │
│ ✓ Stand in front camera  │
│ ✓ Wait for detection     │
│ ✓ System recognizes you  │
│ ✓ Entry logged auto      │
├──────────────────────────┤
│ Last Recognition         │
│ Name: Ahmed              │
│ Time: 18:20:30           │
│ Confidence: 0.95         │
│ [recognized]             │
├──────────────────────────┤
│ Total Today: 12          │
└──────────────────────────┘
```

**Adding Mode Display:**
```
┌──────────────────────────┐
│ 📸 Capturing Mode        │
├──────────────────────────┤
│ Progress: 5 / 15         │
│ [████░░░░░░░░░░░░░░░░]  │
├──────────────────────────┤
│ 📋 Capture Instructions  │
│ ✓ Face in center         │
│ ✓ Good lighting          │
│ ✓ Natural expression     │
│ ✓ Vary angle (15+)       │
├──────────────────────────┤
│ ● Face Detected          │
├──────────────────────────┤
│ [Capture] [Cancel]       │
└──────────────────────────┘
```

---

### **4. EmployeeRow.jsx**
**Purpose:** Single employee row in the employee list

**Props:**
- `employee` (object) — {id, name, photo_count}
- `onDelete` (function) — Delete callback
- `onViewPhoto` (function) — View photo callback

**Features:**
- Displays employee photo, name, ID
- Delete button
- Photo view button

---

## 📄 Pages

### **AttendancePage.jsx**

**Purpose:** Main page — real-time face recognition + employee registration

**Layout:** 60/40 split
- **Left (60%):** Camera feed + action buttons
- **Right (40%):** Status panel

**States:**
```javascript
const [totalToday, setTotalToday] = useState(0)          // Attendance count
const [currentFaceDetected, setCurrentFaceDetected] = useState(false)
const [lastRecognition, setLastRecognition] = useState(null)
const [faceBox, setFaceBox] = useState(null)             // Bounding box

// Adding employee states
const [captureStep, setCaptureStep] = useState(1)        // 1: name, 2: capture, 3: register
const [photoCount, setPhotoCount] = useState(0)          // 0-15
const [captureError, setCaptureError] = useState('')
const [addingName, setAddingName] = useState('')
```

**WebSocket Flow:**
```javascript
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8000/ws/recognition')
  
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data)
    
    setFaceBox(data.bbox)                   // Draw rectangle
    setCurrentFaceDetected(data.status !== 'no_face')
    
    if (mode === 'recognition') {
      if (data.status === 'recognized') {
        // Only count if new or after 3 seconds
        if (!prev || prev.name !== data.name || Date.now() - prev._ts > 3000) {
          setTotalToday(t => t + 1)
        }
      }
      setLastRecognition(data)
    }
  }
  
  return () => ws.close()
}, [mode])
```

**Capture Flow (Spacebar):**
```javascript
useEffect(() => {
  const handleKeyDown = (e) => {
    if (mode === 'adding' && captureStep === 2 && e.code === 'Space') {
      e.preventDefault()
      handleCapturePhoto()
    }
  }
  window.addEventListener('keydown', handleKeyDown)
  return () => window.removeEventListener('keydown', handleKeyDown)
}, [mode, captureStep, addingName, photoCount])
```

**Registration Flow:**
```
Step 1: Enter name
  - Input field appears
  - "Start Capture" button

Step 2: Capture 15 photos
  - Press Spacebar or click "Capture"
  - POST /api/workers/capture-live for each
  - Progress bar updates (0 → 15)

Step 3: Register
  - Auto-triggers at 15 photos
  - POST /api/workers/register
  - Success message for 1.5 seconds
  - Exit to recognition mode
```

**Code Example:**
```jsx
const handleCapturePhoto = async () => {
  const formData = new FormData()
  formData.append('name', addingName)
  formData.append('photo_index', photoCount)

  const res = await fetch('http://localhost:8000/api/workers/capture-live', {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
  
  if (data.status === 'saved') {
    setPhotoCount(photoCount + 1)
    if (photoCount + 1 >= 15) {
      handleRegister()
    }
  } else {
    setCaptureError('No face detected. Try again.')
  }
}
```

---

### **EmployeesPage.jsx**

**Purpose:** View and manage registered employees

**Features:**
- List all employees with photos
- Delete employees
- View employee details
- Add new employee button

**State:**
```javascript
const [employees, setEmployees] = useState([])
const [loading, setLoading] = useState(true)
const [error, setError] = useState(null)
```

**Fetch Flow:**
```javascript
useEffect(() => {
  fetch('http://localhost:8000/api/workers')
    .then(res => res.json())
    .then(data => setEmployees(data))
}, [])
```

**Delete Flow:**
```javascript
const handleDelete = async (name) => {
  await fetch(`http://localhost:8000/api/workers/${name}`, {
    method: 'DELETE'
  })
  setEmployees(employees.filter(e => e.name !== name))
}
```

---

## 🧠 State Management

**No Redux/Context needed** — Uses React hooks in a simple hierarchy:

```
App (root state)
├── page (current page)
├── cameraActive (boolean)
├── mode ('recognition' | 'adding')
├── addingName (string)
└── AttendancePage (local state)
    ├── totalToday
    ├── faceBox
    ├── lastRecognition
    ├── photoCount
    └── captureStep
```

**State lifting:**
- App holds global state
- Passes via props to pages
- Pages have local state for details

---

## 🔌 WebSocket Integration

### **Connection Setup**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/recognition')

ws.onopen = () => console.log('Connected')
ws.onmessage = (e) => { /* Handle data */ }
ws.onerror = (e) => console.error('Error:', e)
ws.onclose = () => console.log('Closed')
```

### **Data Format Received**
```json
{
  "status": "recognized",      // or "unknown", "no_face"
  "name": "ismail",            // Employee name
  "confidence": 0.95,          // 0-1 (higher = more confident)
  "time": "18:20:30",          // Current time
  "bbox": [x, y, w, h]         // Bounding box (null if no_face)
}
```

### **Update Frequency**
- Sent every **67ms** (≈15 FPS)
- Continuous while connected

---

## ▶️ Running the App

### **Development Mode (with Hot Reload)**
```bash
npm run dev
```
- Opens at `http://localhost:5173`
- Auto-reloads on file changes
- ESLint checks on save

### **Build for Production**
```bash
npm run build
```
- Creates `dist/` folder
- Optimized, minified bundles
- Ready to deploy

### **Preview Production Build**
```bash
npm run preview
```
- Serves `dist/` locally
- Verifies production build works

### **Linting**
```bash
npm run lint
```
- Checks code quality
- Reports ESLint errors

---

## 🎨 Styling System

### **Theme Variables**
All colors defined in `src/index.css` as CSS custom properties:

```css
:root {
  --teal: #14B8A6;         /* Primary accent */
  --green: #10B981;        /* Success */
  --red: #EF4444;          /* Error/danger */
  --bg-base: #0F172A;      /* Dark background */
  --text-1: #F1F5F9;       /* Primary text */
}
```

### **Component-Level Styles**
Each component uses inline styles (no separate CSS files):

```javascript
<div style={{
  background: 'var(--bg-surface)',
  border: '1px solid var(--bg-border)',
  borderRadius: 8,
  padding: 20
}}>
  Content
</div>
```

**Advantages:**
- ✅ Scoped styles (no conflicts)
- ✅ Dynamic theming (change CSS vars globally)
- ✅ No build-time CSS processing needed

### **Global Styles** (`src/index.css`)
```css
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font: 14px var(--font-base); color: var(--text-1); background: var(--bg-base); }
button { cursor: pointer; transition: all 200ms; }
input { background: var(--bg-surface); border: 1px solid var(--bg-border); }

/* Animations */
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.live-dot { display: inline-block; width: 8px; height: 8px; background: var(--green); border-radius: 50%; animation: pulse 2s ease-in-out infinite; }
```

---

## 🔨 Development

### **Adding a New Component**

```javascript
// src/components/MyComponent.jsx
export default function MyComponent({ prop1, prop2 }) {
  return (
    <div style={{ padding: 20 }}>
      {prop1}
    </div>
  )
}
```

### **Adding a New Page**

```javascript
// src/pages/MyPage.jsx
export default function MyPage({ onNavigate }) {
  return (
    <div style={{ padding: '24px 28px' }}>
      <h1>My Page</h1>
    </div>
  )
}

// Then add to App.jsx router
```

### **Common Patterns**

**Fetching Data:**
```javascript
useEffect(() => {
  fetch('/api/workers')
    .then(res => res.json())
    .then(data => setState(data))
    .catch(err => console.error(err))
}, [])
```

**Form Submission:**
```javascript
const handleSubmit = async () => {
  const formData = new FormData()
  formData.append('name', value)
  
  const res = await fetch('/api/endpoint', {
    method: 'POST',
    body: formData
  })
  const data = await res.json()
}
```

---

## 🐛 Troubleshooting

### **Issue: "Cannot connect to WebSocket"**
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS headers from backend

### **Issue: "Camera not loading"**
- Backend server must be running
- Check `/api/stream` endpoint responds with images
- Browser must have webcam permission

### **Issue: "Face not detected in capture"**
- Ensure good lighting
- Face should be centered in frame
- Try different angles

### **Issue: "Port 5173 already in use"**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
# Or use different port
npm run dev -- --port 5174
```

### **Issue: Hot reload not working**
- Restart dev server
- Check Vite version: `npm list vite`
- Clear `.vite` cache: `rm -rf node_modules/.vite`

### **Issue: Slow performance**
- Check network latency (WebSocket/HTTP)
- Monitor CPU usage (JavaScript execution)
- Check camera FPS in StatusPanel
- Consider reducing quality in backend

---

## 📊 Performance Tips

| Optimization | Implementation |
|---|---|
| **Lazy Loading** | Not needed (small app) |
| **Code Splitting** | Vite handles automatically |
| **Memoization** | Use `React.memo()` for static components |
| **WebSocket** | Already optimal (15 FPS) |
| **Image Compression** | Backend handles (70% JPEG quality) |

---

## 🔐 Security Considerations

- **CORS:** Configured for localhost only (change for production)
- **Webcam Access:** Browser prompts user for permission
- **Data:** No sensitive data stored client-side
- **WebSocket:** No authentication (add JWT if needed)

---

## 📝 License

Part of ShkReco project. Contact maintainer for details.

---

## 👨‍💼 Author

**Ismail Abu Muawiya** (@OxIsmail)

---

**Last Updated:** April 26, 2026
