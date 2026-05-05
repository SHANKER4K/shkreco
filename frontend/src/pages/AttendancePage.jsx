import React, { useState, useEffect } from "react";
import CameraFeed from "../components/CameraFeed";
import StatusPanel from "../components/StatusPanel";

export default function AttendancePage({
  onCameraActive,
  addingEmployeeMode,
  onExitAddingEmployee,
  mode,
  setMode,
  addingName,
  setAddingName,
}) {
  const [totalToday, setTotalToday] = useState(0);
  const [currentFaceDetected, setCurrentFaceDetected] = useState(false);
  const [lastRecognition, setLastRecognition] = useState(null);
  const [faceBox, setFaceBox] = useState(null);
  const [message, setMessage] = useState("");

  // Adding Employee State
  const [captureStep, setCaptureStep] = useState(1); // 1: name, 2: capturing, 3: registering
  const [photoCount, setPhotoCount] = useState(0);
  const [captureError, setCaptureError] = useState("");

  useEffect(() => {
    if (addingEmployeeMode) {
      setMode("adding");
      setCaptureStep(1);
      setAddingName("");
      setPhotoCount(0);
    } else {
      setMode("recognition");
    }
  }, [addingEmployeeMode]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/recognition");

    ws.onopen = () => console.log("WebSocket connected");

    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);

      setFaceBox(data.bbox);
      setCurrentFaceDetected(data.status !== "no_face");

      if (mode === "adding") {
        // Auto capture later if needed, but manual for now
      } else {
        if (data.status === "recognized" || data.status === "unknown") {
          if (data.status === "recognized") {
            setLastRecognition((prev) => {
              if (!prev || prev.name !== data.name) {
                // Send attendance data to backend
                fetch("http://localhost:8000/api/attendance/log", {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({
                    name: data.name,
                    timestamp: new Date().toISOString(),
                  }),
                })
                  .then((res) => res.json())
                  .then((responseData) => {
                    // Only increment if backend actually logged it
                    if (responseData.status === "logged") {
                      setTotalToday((t) => t + 1);
                      setMessage("Asslama Alaikum, You can enter");
                    } else {
                      setMessage("I added you just go");
                    }
                  })
                  .catch((error) =>
                    console.error("Error logging attendance:", error),
                  );
                return { ...data, _ts: Date.now() };
              }
              return prev;
            });
          } else {
            setLastRecognition(data);
            setMessage("");
          }
        }
      }
    };

    ws.onerror = (e) => console.error("WebSocket error:", e);
    ws.onclose = () => console.log("WebSocket closed");

    return () => ws.close();
  }, [mode]);

  // Spacebar to trigger photo capture
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (mode === "adding" && captureStep === 2 && e.code === "Space") {
        e.preventDefault();
        handleCapturePhoto();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [mode, captureStep, addingName, photoCount]);

  const handleStartAddEmployee = () => {
    if (!addingName.trim()) return;
    setMode("adding");
    setCaptureStep(2);
  };

  const handleCapturePhoto = async () => {
    if (captureStep !== 2) return;
    setCaptureError("");
    const formData = new FormData();
    formData.append("name", addingName);
    formData.append("photo_index", photoCount);

    try {
      const res = await fetch(
        "http://localhost:8000/api/workers/capture-live",
        {
          method: "POST",
          body: formData,
        },
      );
      const data = await res.json();

      if (data.status === "saved") {
        const newCount = photoCount + 1;
        setPhotoCount(newCount);
        if (newCount >= 15) {
          setCaptureStep(3);
          handleRegister();
        }
      } else {
        setCaptureError("No face detected. Try again.");
      }
    } catch (err) {
      setCaptureError("Error saving photo: " + err.message);
    }
  };

  const handleRegister = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/workers/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: addingName }),
      });
      const data = await res.json();
      if (data.status === "registered") {
        setTimeout(() => {
          handleCancelAddEmployee();
        }, 1500);
      } else {
        setCaptureError("Registration failed");
        setCaptureStep(2);
      }
    } catch (err) {
      setCaptureError("Error: " + err.message);
      setCaptureStep(2);
    }
  };

  const handleCancelAddEmployee = () => {
    setMode("recognition");
    setAddingName("");
    setPhotoCount(0);
    setCaptureStep(1);
    setCaptureError("");
    if (onExitAddingEmployee) onExitAddingEmployee();
  };

  return (
    <div style={{ display: "flex", gap: 20, padding: "24px 28px" }}>
      <div style={{ flex: "0 0 60%", position: "relative" }}>
        <CameraFeed onCameraActive={onCameraActive} faceBox={faceBox} />

        {mode === "adding" && captureStep === 1 && (
          <div
            style={{
              marginTop: 16,
              padding: 16,
              background: "var(--bg-surface)",
              border: "1px solid var(--bg-border)",
              borderRadius: 8,
              display: "flex",
              gap: 12,
              alignItems: "flex-end",
            }}
          >
            <input
              className="input"
              placeholder="Employee name (use underscore)"
              value={addingName}
              onChange={(e) =>
                setAddingName(e.target.value.replace(/\s+/g, "_"))
              }
              style={{ flex: 1, margin: 0 }}
              autoFocus
            />
            <button
              className="btn"
              onClick={handleStartAddEmployee}
              disabled={!addingName.trim()}
            >
              Start Capture →
            </button>
            <button className="btn-outline" onClick={handleCancelAddEmployee}>
              Cancel
            </button>
          </div>
        )}

        {mode === "adding" && captureStep > 1 && (
          <div
            style={{
              marginTop: 16,
              padding: 16,
              background: "var(--bg-surface)",
              border: "1px solid var(--bg-border)",
              borderRadius: 8,
              textAlign: "center",
            }}
          >
            {captureStep === 2 && (
              <>
                <p
                  style={{
                    fontSize: 13,
                    marginBottom: 12,
                    color: "var(--text-2)",
                  }}
                >
                  Capturing photos... Press SPACEBAR or wait for auto-capture
                </p>
                {captureError && (
                  <p
                    style={{
                      color: "var(--red)",
                      fontSize: 12,
                      marginBottom: 12,
                    }}
                  >
                    {captureError}
                  </p>
                )}
              </>
            )}
            {captureStep === 3 && (
              <p style={{ color: "var(--green)", fontWeight: 500 }}>
                {captureError
                  ? `Error: ${captureError}`
                  : "✓ Employee registered successfully!"}
              </p>
            )}
          </div>
        )}

        {mode === "recognition" && (
          <button
            className="btn-outline"
            style={{ marginTop: 14, width: "100%" }}
            onClick={() => {
              setMode("adding");
              setCaptureStep(1);
            }}
          >
            + Add Employee
          </button>
        )}
      </div>

      <div style={{ flex: 1 }}>
        <StatusPanel
          lastRecognition={lastRecognition}
          totalToday={totalToday}
          faceDetected={currentFaceDetected}
          mode={mode}
          captureProgress={photoCount}
          message={message}
          onCapture={handleCapturePhoto}
          onCancel={handleCancelAddEmployee}
        />
      </div>
    </div>
  );
}
