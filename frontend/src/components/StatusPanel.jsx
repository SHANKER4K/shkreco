import React from "react";

export default function StatusPanel({
  lastRecognition,
  totalToday,
  faceDetected,
  mode,
  captureProgress,
  onCapture,
  onCancel,
}) {
  if (mode === "adding") {
    return (
      <div
        style={{
          background: "var(--bg-surface)",
          border: "1px solid var(--bg-border)",
          borderRadius: 8,
          padding: 20,
          height: "100%",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Mode Badge */}
        <div
          style={{
            display: "inline-block",
            padding: "6px 12px",
            background: "var(--teal-dim)",
            color: "var(--teal)",
            borderRadius: 6,
            fontSize: 12,
            fontWeight: 600,
            marginBottom: 20,
            width: "fit-content",
          }}
        >
          📸 Capturing Mode
        </div>

        {/* Progress Bar */}
        <div style={{ marginBottom: 20 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginBottom: 8,
              fontSize: 12,
              fontWeight: 500,
            }}
          >
            <span>Progress</span>
            <span style={{ color: "var(--teal)" }}>{captureProgress} / 15</span>
          </div>
          <div
            style={{
              background: "var(--bg-border)",
              height: 8,
              borderRadius: 4,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                background: "var(--teal)",
                height: "100%",
                width: `${(captureProgress / 15) * 100}%`,
                transition: "width 300ms ease-out",
              }}
            />
          </div>
        </div>

        {/* Instructions */}
        <div style={{ marginBottom: 24 }}>
          <h3
            style={{
              fontSize: 13,
              fontWeight: 600,
              marginBottom: 12,
              color: "var(--teal)",
            }}
          >
            📋 Capture Instructions
          </h3>
          <ul
            style={{
              fontSize: 12,
              color: "var(--text-2)",
              lineHeight: 1.8,
              listStyle: "none",
              paddingLeft: 0,
            }}
          >
            <li>✓ Face in center of frame</li>
            <li>✓ Good lighting (avoid backlight)</li>
            <li>✓ Natural expression</li>
            <li>✓ Vary angle (15+ photos)</li>
          </ul>
        </div>

        {/* Current Status */}
        <div
          style={{
            padding: 12,
            background: "var(--bg-elevated)",
            borderRadius: 6,
            marginBottom: 20,
            fontSize: 12,
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              marginBottom: 4,
            }}
          >
            <div
              style={{
                width: 8,
                height: 8,
                borderRadius: "50%",
                background: faceDetected ? "var(--green)" : "var(--red)",
              }}
            />
            <span
              style={{
                color: faceDetected ? "var(--green)" : "var(--red)",
                fontWeight: 500,
              }}
            >
              {faceDetected ? "Face Detected" : "No Face Detected"}
            </span>
          </div>
          <div style={{ color: "var(--text-2)", fontSize: 11 }}>
            Position face in rectangle and capture
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ marginTop: "auto", display: "flex", gap: 8 }}>
          <button className="btn" style={{ flex: 1 }} onClick={onCapture}>
            Capture
          </button>
          <button
            className="btn-outline"
            style={{ flex: 1 }}
            onClick={onCancel}
          >
            Cancel
          </button>
        </div>
      </div>
    );
  }

  // Original recognition mode
  return (
    <div
      style={{
        background: "var(--bg-surface)",
        border: "1px solid var(--bg-border)",
        borderRadius: 8,
        padding: 20,
        height: "100%",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Status Indicator */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 12,
          marginBottom: 24,
        }}
      >
        <div
          style={{
            width: 16,
            height: 16,
            borderRadius: "50%",
            background: faceDetected ? "var(--green)" : "var(--red)",
            animation: faceDetected ? "pulse 2s ease-in-out infinite" : "none",
          }}
        />
        <span style={{ fontSize: 14, fontWeight: 500 }}>
          {faceDetected ? "Face Detected" : "Waiting for Face"}
        </span>
      </div>

      {/* Instructions */}
      <div style={{ marginBottom: 24 }}>
        <h3
          style={{
            fontSize: 13,
            fontWeight: 600,
            marginBottom: 12,
            color: "var(--teal)",
          }}
        >
          📋 Instructions
        </h3>
        <ul
          style={{
            fontSize: 12,
            color: "var(--text-2)",
            lineHeight: 1.8,
            listStyle: "none",
            paddingLeft: 0,
          }}
        >
          <li>✓ Stand in front of camera</li>
          <li>✓ Wait for face detection</li>
          <li>✓ System will recognize you</li>
          <li>✓ Entry logged automatically</li>
        </ul>
      </div>

      {/* Last Recognition */}
      <div
        style={{
          marginBottom: 20,
          paddingBottom: 20,
          borderBottom: "1px solid var(--bg-border)",
        }}
      >
        <h3
          style={{
            fontSize: 13,
            fontWeight: 600,
            marginBottom: 12,
            color: "var(--text-1)",
          }}
        >
          Last Recognition
        </h3>
        {lastRecognition ? (
          <div>
            <div
              style={{
                fontSize: 14,
                fontWeight: 500,
                color: "var(--text-1)",
                marginBottom: 4,
              }}
            >
              {lastRecognition.name.replace(/_/g, " ")}
            </div>
            <div
              style={{
                fontSize: 11,
                color: "var(--text-2)",
                fontFamily: "var(--font-mono)",
                marginBottom: 8,
              }}
            >
              {lastRecognition.time} •{" "}
              {Math.floor(lastRecognition.confidence.toFixed(2)*100)}%
            </div>
            <div
              style={{
                display: "inline-block",
                padding: "4px 10px",
                borderRadius: 12,
                fontSize: 11,
                fontWeight: 500,
                background:
                  lastRecognition.status === "recognized"
                    ? "var(--green-dim)"
                    : "var(--red-dim)",
                color:
                  lastRecognition.status === "recognized"
                    ? "var(--green)"
                    : "var(--red)",
              }}
            >
              {lastRecognition.status}
            </div>
          </div>
        ) : (
          <div style={{ fontSize: 12, color: "var(--text-2)" }}>
            No recognitions yet
          </div>
        )}
      </div>

      {/* Total Count */}
      <div
        style={{
          marginTop: "auto",
          paddingTop: 16,
          borderTop: "1px solid var(--bg-border)",
        }}
      >
        <div
          style={{
            fontSize: 12,
            fontFamily: "var(--font-mono)",
            color: "var(--teal)",
            fontWeight: 500,
          }}
        >
          Total Today: <span style={{ fontSize: 16 }}>{totalToday}</span>
        </div>
      </div>
    </div>
  );
}
