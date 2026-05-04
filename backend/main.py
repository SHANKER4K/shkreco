import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
import cv2
import torch
import pickle
import numpy as np
import datetime
import asyncio
import threading
from PIL import Image

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from contextlib import asynccontextmanager

from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from torchvision import transforms
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch.nn.functional as F
from scipy.spatial.distance import cosine

# Load model — same pattern as existing main.py
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

mtcnn = MTCNN(image_size=160, margin=20, keep_all=False, device=device)

backbone = InceptionResnetV1(pretrained="vggface2").to(device)
ckpt = torch.load(
    "backend/checkpoints/arcface_best.pth", map_location=device, weights_only=False
)
if "backbone" in ckpt:
    backbone.load_state_dict(ckpt["backbone"])
else:
    backbone.load_state_dict(ckpt)
backbone.eval()

# Load the real database
DB_PATH = "worker_db_local.pkl"
if os.path.exists(DB_PATH):
    with open(DB_PATH, "rb") as f:
        worker_db = pickle.load(f)
else:
    worker_db = {}

# Transform — must match training
transform = transforms.Compose(
    [
        transforms.Resize((160, 160)),
        transforms.ToTensor(),
        transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
    ]
)

THRESHOLD = 0.8


def run_recognition(frame_bgr):
    """
    Takes a BGR OpenCV frame.
    Returns a dict with name, confidence, time, status, bbox.
    """
    # print(f"Frame shape: {frame_bgr.shape}")
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)

    faces = mtcnn.detect(pil_img)
    bbox = None
    face_tensor = None

    if faces is not None and len(faces) > 0 and faces[0] is not None:
        boxes, probs = faces
        if len(boxes) > 0:
            box = boxes[0]
            x0, y0, x1, y1 = box
            x = int(x0)
            y = int(y0)
            w = int(x1 - x0)
            h = int(y1 - y0)
            bbox = [x, y, w, h]
            face_tensor = mtcnn(pil_img)

    # print(f"Face detected: {face_tensor is not None}")
    if face_tensor is None:
        return {
            "name": None,
            "confidence": 0,
            "time": datetime.datetime.now().strftime("%H:%M:%S"),
            "status": "no_face",
            "bbox": None,
        }

    face_input = face_tensor.unsqueeze(0).to(device)
    with torch.no_grad():
        emb = backbone(face_input)
    emb = F.normalize(emb, p=2, dim=1).cpu().numpy().flatten()

    best_name = "Unknown"
    best_dist = THRESHOLD

    for name, known_emb in worker_db.items():
        if known_emb is None:
            continue
        dist = 1 - cosine(emb, known_emb)
        # print(dist)
        if dist > best_dist:
            best_dist = dist
            best_name = name

    status = "recognized" if best_name != "Unknown" else "unknown"
    confidence = float(round(best_dist, 2)) if best_name != "Unknown" else float(round(dist, 2))

    return {
        "name": best_name,
        "confidence": confidence,
        "time": datetime.datetime.now().strftime("%H:%M:%S"),
        "status": status,
        "bbox": bbox,
    }


# ── Dedicated background capture thread ──────────────────────────────────────
class CameraManager:
    def __init__(self, fps: int = 15):
        self._frame: np.ndarray | None = None
        self._lock = threading.Lock()
        self._fps = fps
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        interval = 1.0 / self._fps
        while not self._stop.is_set():
            ret, frame = cap.read()
            if ret:
                with self._lock:
                    self._frame = frame
            time.sleep(interval)          # ← rate-limit the capture loop
        cap.release()

    def read(self) -> np.ndarray | None:
        with self._lock:
            return self._frame.copy() if self._frame is not None else None

    def stop(self):
        self._stop.set()


camera = CameraManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    camera.stop()
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/workers")
def get_workers():
    workers = []
    index = 1
    for name in worker_db.keys():
        photo_dir = f"dataset/{name}"
        if not os.path.exists(photo_dir):
            continue
        photos = [f for f in os.listdir(photo_dir) if f.endswith(".jpg")]
        if not photos:
            continue
        workers.append(
            {"id": f"EMP-{index:03d}", "name": name, "photo_count": len(photos)}
        )
        index += 1
    return workers


@app.get("/api/workers/{name}/photo")
def worker_photo(name: str):
    photo_dir = f"dataset/{name}"
    if not os.path.exists(photo_dir):
        raise HTTPException(status_code=404)
    photos = sorted([f for f in os.listdir(photo_dir) if f.endswith(".jpg")])
    if not photos:
        raise HTTPException(status_code=404)
    return FileResponse(f"{photo_dir}/{photos[0]}", media_type="image/jpeg")


@app.delete("/api/workers/{name}")
def delete_worker(name: str):
    global worker_db
    if name in worker_db:
        del worker_db[name]
        with open(DB_PATH, "wb") as f:
            pickle.dump(worker_db, f)
    return {"status": "deleted"}


@app.post("/api/workers/capture-live")
async def capture_live_photo(name: str = Form(...), photo_index: int = Form(...)):
    frame = camera.read()
    if frame is None:
        return {"status": "no_frame"}

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    face_tensor = mtcnn(pil_img)

    if face_tensor is None:
        return {"status": "no_face"}

    save_dir = f"dataset/{name}"
    os.makedirs(save_dir, exist_ok=True)

    from torchvision.transforms.functional import to_pil_image

    face_pil = to_pil_image(((face_tensor + 1) / 2).clamp(0, 1))
    face_pil.save(f"{save_dir}/{photo_index:03d}.jpg")

    count = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
    return {"status": "saved", "count": count}


@app.post("/api/workers/capture")
async def capture_photo(
    name: str = Form(...), photo_index: int = Form(...), frame: UploadFile = File(...)
):
    contents = await frame.read()
    nparr = np.frombuffer(contents, np.uint8)
    img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb)
    face_tensor = mtcnn(pil_img)

    if face_tensor is None:
        return {"status": "no_face"}

    save_dir = f"dataset/{name}"
    os.makedirs(save_dir, exist_ok=True)

    from torchvision.transforms.functional import to_pil_image

    face_pil = to_pil_image(((face_tensor + 1) / 2).clamp(0, 1))
    face_pil.save(f"{save_dir}/{photo_index:03d}.jpg")

    count = len([f for f in os.listdir(save_dir) if f.endswith(".jpg")])
    return {"status": "saved", "count": count}


@app.post("/api/workers/register")
def register_worker(body: dict):
    global worker_db
    name = body["name"]
    photo_dir = f"dataset/{name}"
    if not os.path.exists(photo_dir):
        raise HTTPException(status_code=400, detail="No photos found")
    photos = [f for f in os.listdir(photo_dir) if f.endswith(".jpg")]

    embeddings = []
    for photo in photos:
        img = Image.open(f"{photo_dir}/{photo}").convert("RGB")
        face_tensor = mtcnn(img)
        if face_tensor is None:
            continue
        face_input = face_tensor.unsqueeze(0).to(device)
        with torch.no_grad():
            emb = backbone(face_input)
        embeddings.append(F.normalize(emb, p=2, dim=1).cpu().numpy().flatten())

    if not embeddings:
        raise HTTPException(status_code=400, detail="No valid faces found")

    mean_emb = np.mean(embeddings, axis=0)
    mean_emb = mean_emb / np.linalg.norm(mean_emb)
    worker_db[name] = mean_emb

    with open(DB_PATH, "wb") as f:
        pickle.dump(worker_db, f)

    return {"status": "registered", "name": name}


# ── Stream: cap frame rate at 15 fps ─────────────────────────────────────────
def generate_frames():
    interval = 1.0 / 15          # 15 fps max
    while True:
        frame = camera.read()
        if frame is None:
            time.sleep(0.05)
            continue
        _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        time.sleep(interval)     # ← was missing entirely


@app.get("/api/stream")
def stream():
    return StreamingResponse(
        generate_frames(), media_type="multipart/x-mixed-replace;boundary=frame"
    )


# ── WebSocket: skip recognition if frame unchanged ───────────────────────────
@app.websocket("/ws/recognition")
async def recognition_ws(websocket: WebSocket):
    await websocket.accept()
    last_hash = None
    try:
        while True:
            frame = camera.read()
            if frame is not None:
                # Cheap fingerprint — skip expensive inference if frame is the same
                small = cv2.resize(frame, (16, 16))
                frame_hash = small.tobytes()

                if frame_hash != last_hash:
                    last_hash = frame_hash
                    result = await asyncio.get_event_loop().run_in_executor(
                        None, run_recognition, frame   # ← run blocking work off the event loop
                    )
                    await websocket.send_json(result)

            await asyncio.sleep(0.1)   # 10 fps is plenty for recognition
    except WebSocketDisconnect:
        pass
        
