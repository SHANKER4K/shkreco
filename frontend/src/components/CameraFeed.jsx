import { useEffect, useRef } from 'react'

export default function CameraFeed({ onCameraActive, faceBox }) {
  const canvasRef = useRef(null)
  const imgRef = useRef(null)

  useEffect(() => {
    if (!canvasRef.current || !imgRef.current) return
    const canvas = canvasRef.current
    const img = imgRef.current
    const ctx = canvas.getContext('2d')

    // Ensure canvas dimensions match the image exactly
    const updateCanvasSize = () => {
      if (img.clientWidth && img.clientHeight) {
        canvas.width = img.clientWidth
        canvas.height = img.clientHeight
      }
    }
    
    // Call once and also if window resizes
    updateCanvasSize()

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (!faceBox) return

    // Scale coordinates since the image might be scaled down by CSS
    const scaleX = canvas.width / (img.naturalWidth || 640)
    const scaleY = canvas.height / (img.naturalHeight || 480)

    const [x, y, w, h] = faceBox
    const scaledX = x * scaleX
    const scaledY = y * scaleY
    const scaledW = w * scaleX
    const scaledH = h * scaleY

    // Draw rectangle
    ctx.strokeStyle = '#14B8A6'  // --teal
    ctx.lineWidth = 3
    ctx.strokeRect(scaledX, scaledY, scaledW, scaledH)

    // Optional: add label
    ctx.fillStyle = '#14B8A6'
    ctx.font = 'bold 14px Sora'
    ctx.fillText('Face Detected', scaledX, scaledY - 8)
  }, [faceBox])

  return (
    <div style={{ position: 'relative', display: 'inline-block', width: '100%', aspectRatio: '4/3' }}>
      <img
        ref={imgRef}
        src="http://localhost:8000/api/stream"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          display: 'block',
          borderRadius: '8px',
        }}
        onLoad={(e) => {
          onCameraActive(true);
          // Trigger a re-render of canvas by slightly delaying the size update
          if (canvasRef.current) {
            canvasRef.current.width = e.target.clientWidth;
            canvasRef.current.height = e.target.clientHeight;
          }
        }}
        onError={() => onCameraActive(false)}
        alt="Camera feed"
      />
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          borderRadius: '8px',
          pointerEvents: 'none'
        }}
      />
    </div>
  )
}
