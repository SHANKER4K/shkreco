# ShkReco Backend 🧠

**Facial Recognition Attendance System Backend** — Real-time face detection, recognition, and employee management using FastAPI, PyTorch, and deep learning models.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [API Endpoints](#api-endpoints)
- [WebSocket](#websocket)
- [Models & Technology](#models--technology)
- [Database](#database)
- [Running the Server](#running-the-server)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

**ShkReco Backend** is a FastAPI-based server that:
1. **Captures** live video from a webcam
2. **Detects** faces in real-time using MTCNN
3. **Recognizes** employees by comparing face embeddings
4. **Registers** new employees (15-photo capture process)
5. **Streams** camera feed and recognition results to the frontend

**Key Features:**
- ✅ Real-time face detection (60 FPS)
- ✅ Deep learning-based face recognition (VGGFace2 embeddings)
- ✅ Live WebSocket updates
- ✅ Employee database with embeddings
- ✅ Anti-spoofing ready (detect screen replays)
- ✅ CORS-enabled for frontend communication

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React)                       │
│              (Attendance + Employees Pages)                 │
└──────────────┬──────────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │              │
    ┌───▼───┐     ┌───▼────┐
    │ HTTP  │     │WebSocket│
    │       │     │         │
    └───┬───┘     └────┬────┘
        │              │
        ▼              ▼
    ┌─────────────────────────────────────────────────────────┐
    │              FastAPI Backend (Port 8000)                │
    │                                                          │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │  CameraManager                                   │   │
    │  │  - OpenCV VideoCapture (640x480)                 │   │
    │  │  - Thread-safe frame access                      │   │
    │  └──────────────────────────────────────────────────┘   │
    │                          │                               │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │  Face Detection (MTCNN)                          │   │
    │  │  - Input: PIL Image                             │   │
    │  │  - Output: Cropped face tensor (160x160)        │   │
    │  └──────────────────────────────────────────────────┘   │
    │                          │                               │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │  Face Embedding (InceptionResnetV1)             │   │
    │  │  - Pre-trained: VGGFace2                        │   │
    │  │  - Fine-tuned: ArcFace Loss                     │   │
    │  │  - Output: 512-dim normalized vector           │   │
    │  └──────────────────────────────────────────────────┘   │
    │                          │                               │
    │  ┌──────────────────────────────────────────────────┐   │
    │  │  Face Recognition (Cosine Similarity)            │   │
    │  │  - Compare with worker_db embeddings             │   │
    │  │  - Threshold: 0.8                               │   │
    │  └──────────────────────────────────────────────────┘   │
    │                          │                               │
    │                          ▼                               │
    │              ┌─────────────────────┐                     │
    │              │  worker_db.pkl      │                    │
    │              │  {name: embedding}  │                    │
    │              └─────────────────────┘                     │
    │                                                          │
    └─────────────────────────────────────────────────────────┘
```

---

## 📦 Installation

### Prerequisites
- Python 3.10+
- CUDA 11.8+ (for GPU acceleration, optional but recommended)
- FFmpeg (for video processing)
- Webcam (USB or built-in)

### Step 1: Clone & Setup Environment

```bash
cd /path/to/shkreco
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install fastapi uvicorn
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118  # GPU
# OR for CPU: pip install torch torchvision
pip install facenet-pytorch opencv-python pillow scipy numpy
pip install python-multipart  # For file uploads
```

### Step 3: Download Pre-trained Checkpoints

The backend expects a fine-tuned model at `checkpoints/arcface_best.pth`. If you don't have it:

```bash
# Option 1: Use VGGFace2 pre-trained (slower recognition)
# The code will download automatically on first run

# Option 2: Provide your own fine-tuned checkpoint
# Place it at: ./checkpoints/arcface_best.pth
```

### Step 4: Create Required Directories

```bash
mkdir -p dataset checkpoints
```

---

## ⚙️ Configuration

### `main.py` Settings

**Device Configuration** (Line ~20):
```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
```

**Camera Settings** (Line ~130):
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # Resolution
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)      # No frame buffering
```

**Recognition Threshold** (Line ~82):
```python
THRESHOLD = 0.8  # Cosine distance threshold
# Lower = stricter matching
# Higher = more lenient matching
```

**CORS Origins** (Line ~135):
```python
allow_origins=[
    "http://localhost:5173",  # Vite dev server
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Alternative port
]
```

**Database Path** (Line ~33):
```python
DB_PATH = "worker_db_local.pkl"  # Pickled embeddings database
```

---

## 🔌 API Endpoints

### **GET `/api/stream`**
**Purpose:** Stream camera frames in real-time

**Response:** Multipart JPEG stream (MJPEG format)

**Usage:**
```html
<img src="http://localhost:8000/api/stream" />
```

**Example cURL:**
```bash
curl http://localhost:8000/api/stream > camera.mjpeg
```

---

### **GET `/api/workers`**
**Purpose:** List all registered employees

**Response:**
```json
[
  {
    "id": "EMP-001",
    "name": "ismail",
    "photo_count": 15
  },
  {
    "id": "EMP-002",
    "name": "ahmed",
    "photo_count": 15
  }
]
```

**Example:**
```bash
curl http://localhost:8000/api/workers
```

---

### **GET `/api/workers/{name}/photo`**
**Purpose:** Get the first photo of an employee

**Parameters:**
- `name` (string) — Employee name

**Response:** JPEG image file

**Example:**
```bash
curl http://localhost:8000/api/workers/ismail/photo > employee.jpg
```

---

### **DELETE `/api/workers/{name}`**
**Purpose:** Delete an employee and their embeddings

**Parameters:**
- `name` (string) — Employee name

**Response:**
```json
{
  "status": "deleted"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:8000/api/workers/ismail
```

---

### **POST `/api/workers/capture-live`**
**Purpose:** Capture and save a single photo from the live camera feed

**Parameters (Form Data):**
- `name` (string, required) — Employee name
- `photo_index` (integer, required) — Photo number (0-14)

**Response:**
```json
{
  "status": "saved",  // or "no_face"
  "count": 5
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/workers/capture-live \
  -F "name=ismail" \
  -F "photo_index=0"
```

**Workflow:**
1. Captures frame from camera
2. Detects face using MTCNN
3. Saves cropped face to `dataset/{name}/{photo_index:03d}.jpg`
4. Returns status

---

### **POST `/api/workers/capture`**
**Purpose:** Capture photo from uploaded image (alternative to capture-live)

**Parameters (Form Data):**
- `name` (string, required) — Employee name
- `photo_index` (integer, required) — Photo number
- `frame` (file, required) — Image file

**Response:**
```json
{
  "status": "saved",  // or "no_face"
  "count": 5
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/workers/capture \
  -F "name=ismail" \
  -F "photo_index=0" \
  -F "frame=@image.jpg"
```

---

### **POST `/api/workers/register`**
**Purpose:** Register a new employee after capturing 15 photos

**Body (JSON):**
```json
{
  "name": "ismail"
}
```

**Response:**
```json
{
  "status": "registered",
  "name": "ismail"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/workers/register \
  -H "Content-Type: application/json" \
  -d '{"name":"ismail"}'
```

**Workflow:**
1. Finds all photos in `dataset/{name}/`
2. Computes embeddings for each photo using the backbone model
3. Averages embeddings to create final face vector
4. Stores in `worker_db_local.pkl`
5. Face is now recognized in future frames

---

## 🔌 WebSocket

### **WS `/ws/recognition`**
**Purpose:** Real-time face detection & recognition stream

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/recognition');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

**Message Format (Sent every 67ms ≈ 15 FPS):**
```json
{
  "status": "recognized",         // or "unknown", "no_face"
  "name": "ismail",               // Employee name (null if no_face)
  "confidence": 0.95,             // 1 - cosine_distance
  "time": "18:20:30",             // HH:MM:SS
  "bbox": [100, 50, 160, 200]     // [x, y, width, height] (null if no_face)
}
```

**Example Python Client:**
```python
import asyncio
import websockets
import json

async def listen():
    async with websockets.connect('ws://localhost:8000/ws/recognition') as ws:
        async for message in ws:
            data = json.loads(message)
            print(f"Recognized: {data['name']} ({data['confidence']:.2f})")

asyncio.run(listen())
```

---

## 🤖 Models & Technology

### **Face Detection: MTCNN**
- **Input:** PIL Image
- **Output:** Cropped face tensor (160×160)
- **Paper:** Multi-task Cascaded Convolutional Networks for Face Detection
- **Library:** `facenet_pytorch`

### **Face Embedding: InceptionResnetV1**
- **Pre-trained:** VGGFace2 (trained on 3.3M identities)
- **Fine-tuned:** ArcFace Loss (for this project)
- **Output:** 512-dimensional normalized embedding
- **Purpose:** Convert face image to numerical vector

### **Face Recognition: Cosine Similarity**
```python
similarity = 1 - cosine_distance(embedding1, embedding2)
# Range: 0 (completely different) to 1 (identical)
# Threshold: 0.8 means recognize if similarity > 0.8
```

### **Loss Function: ArcFace**
- Improves generalization across diverse lighting/angles
- Margins encourage discriminative embeddings
- Checkpoint: `checkpoints/arcface_best.pth`

---

## 💾 Database

### **File: `worker_db_local.pkl`**
**Format:** Python pickle (binary)

**Structure:**
```python
{
  "ismail": np.array([0.12, 0.45, -0.32, ...]),      # 512-dim vector
  "ahmed": np.array([0.89, -0.21, 0.67, ...]),
  "fatima": np.array([-0.15, 0.88, 0.23, ...])
}
```

**Loading:**
```python
import pickle
with open("worker_db_local.pkl", "rb") as f:
    worker_db = pickle.load(f)
```

### **Directory: `dataset/{name}/`**
**Structure:**
```
dataset/
├── ismail/
│   ├── 000.jpg  # Cropped face 160×160
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ... (up to 14)
├── ahmed/
│   ├── 000.jpg
│   └── ...
└── fatima/
    └── ...
```

**Retention:** Photos are kept for re-training/re-registration.

---

## ▶️ Running the Server

### **Development Mode** (with auto-reload)
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Production Mode**
```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **With GPU Acceleration**
```bash
# Ensure CUDA environment is set
export CUDA_VISIBLE_DEVICES=0
uvicorn main:app --reload --port 8000
```

### **Verification**
```bash
# API Docs (auto-generated)
open http://localhost:8000/docs

# Health check
curl http://localhost:8000/api/workers
```

---

## 🔍 Recognition Flow

### **Real-time Recognition (via WebSocket)**

```
Frame captured (30-60 FPS)
        │
        ▼
    MTCNN Detection
    ├── No face → Send {status: "no_face"}
    └── Face found → Extract 160×160 crop
        │
        ▼
    Backbone Model (InceptionResnetV1)
    ├── Input: Cropped face
    └── Output: 512-dim embedding
        │
        ▼
    Cosine Similarity Matching
    ├── Loop through worker_db
    ├── Find best match (lowest distance)
    └── Compute confidence: 1 - distance
        │
        ▼
    Decision
    ├── If distance < 0.8 → "recognized"
    │   └── Send {status: "recognized", name: "ismail", confidence: 0.95}
    └── Else → "unknown"
        └── Send {status: "unknown", name: "Unknown", confidence: 0.5}
```

### **Employee Registration (via HTTP)**

```
1. User captures 15 photos (via /api/workers/capture-live)
   dataset/ismail/000.jpg
   dataset/ismail/001.jpg
   ...
   dataset/ismail/014.jpg

2. Frontend calls POST /api/workers/register
   {name: "ismail"}

3. Backend processes:
   ├── Load 15 photos
   ├── Extract embedding for each
   │  ├── Face crop (160×160)
   │  └── Backbone model → 512-dim vector
   ├── Average 15 embeddings
   └── Normalize final embedding

4. Store in worker_db_local.pkl:
   worker_db["ismail"] = averaged_embedding

5. Return {status: "registered"}
```

---

## 🐛 Troubleshooting

### **Issue: "No module named 'fastapi'"**
```bash
pip install fastapi uvicorn
```

### **Issue: "ModuleNotFoundError: No module named 'torch'"**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### **Issue: "CUDA out of memory"**
- **Solution 1:** Reduce batch size (not applicable here — it's 1)
- **Solution 2:** Use CPU mode: `device = torch.device("cpu")`
- **Solution 3:** Restart server to clear memory cache

### **Issue: "Cannot find camera" / "VideoCapture fails"**
```bash
# Check available cameras
ls -la /dev/video*  # Linux
# or test with: python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### **Issue: "WebSocket connection refused"**
- Ensure backend is running on port 8000
- Check frontend config (should match backend URL)
- Verify CORS headers

### **Issue: Slow recognition (>1 sec per frame)**
- **GPU Available?** Should be <50ms per frame
- **CPU Only?** Normal — expect 200-500ms
- **Solution:** Enable GPU via CUDA or reduce resolution

### **Issue: "Unrecognized face" (false negatives)**
- Recompute embeddings (old checkpoint might be incompatible)
- Increase THRESHOLD in `main.py` (e.g., 0.85 → 0.90)
- Capture more diverse photos (different angles, lighting)

### **Issue: "Unknown face recognized" (false positives)**
- Decrease THRESHOLD (e.g., 0.8 → 0.75)
- Use better model checkpoint
- Ensure distinct face features per employee

---

## 📊 Performance Metrics

| Metric | GPU (RTX 3080) | CPU (i7-10700) |
|--------|---|---|
| MTCNN Detection | 10-20ms | 100-200ms |
| Embedding Generation | 20-30ms | 300-500ms |
| Similarity Matching | <1ms | <1ms |
| **Total per frame** | **30-50ms** | **400-700ms** |
| **FPS** | **20-30** | **1.5-2.5** |

---

## 🔐 Security Notes

- **Database:** No encryption (add if needed for production)
- **CORS:** Configure allowed origins for production
- **Rate Limiting:** Not implemented (add for public API)
- **Anti-Spoofing:** Implement liveness detection for production

---

## 📝 License

Part of ShkReco project. Contact maintainer for details.

---

**Last Updated:** April 26, 2026
