import cv2
import os
import argparse
import torch
from PIL import Image
from facenet_pytorch import MTCNN
from torchvision.transforms.functional import to_pil_image

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

mtcnn = MTCNN(
    image_size=160,
    margin=20,
    keep_all=False,
    device=device
)

def capture_worker(name, n_photos=15, save_dir='dataset'):
    worker_dir = os.path.join(save_dir, name)
    os.makedirs(worker_dir, exist_ok=True)

    existing = len([f for f in os.listdir(worker_dir)
                    if f.endswith('.jpg')])
    count = existing

    if existing > 0:
        print(f"Found {existing} photos already — resuming from {existing}")

    cap = cv2.VideoCapture(0,cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print("Error: Cannot open camera")
        return

    instructions = {
        0:  "Shoot straight — face forward",
        3:  "Tilt head slightly right",
        6:  "Tilt head slightly left",
        9:  "Step back from camera",
        12: "Smile naturally",
    }

    print(f"\nStarting capture: {name}")
    print("Press SPACE to capture · Press Q to exit\n")

    # Warm up camera by reading several frames first
    for _ in range(5):
        cap.read()

    while count < n_photos:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("تحذير: إطار فارغ")
            continue

        # Keep clean frame for processing
        # Draw on separate frame for display only
        clean_frame = frame.copy()   # Clean frame without annotations
        display = frame.copy()       # Display frame only

        instruction = ""
        for threshold, text in instructions.items():
            if count >= threshold:
                instruction = text

        h, w = display.shape[:2]

        # Overlay on display only — do not touch clean_frame
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (w, 70), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.5, display, 0.5, 0, display)

        cv2.putText(display, f"{name}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 255, 255), 2)
        cv2.putText(display, f"Photo {count}/{n_photos} — {instruction}",
                    (10, 52), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, (180, 220, 255), 1)

        # Detect face from clean frame
        rgb = cv2.cvtColor(clean_frame, cv2.COLOR_BGR2RGB)
        boxes, _ = mtcnn.detect(Image.fromarray(rgb))

        face_found = False
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = [int(b) for b in box]
                # Draw rectangle on display only
                cv2.rectangle(display, (x1, y1), (x2, y2),
                              (0, 220, 100), 2)
                face_found = True

        status_color = (0, 220, 100) if face_found else (0, 80, 220)
        status_text  = "Face detected" if face_found else "No face"
        cv2.putText(display, status_text,
                    (w - 160, 25), cv2.FONT_HERSHEY_SIMPLEX,
                    0.55, status_color, 2)

        # Display only the display frame — not the original
        cv2.imshow('Worker Registration ENIE', display)
        cv2.resizeWindow('Worker Registration ENIE', 800, 600)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            # Save from clean frame
            pil_img = Image.fromarray(rgb)
            face_tensor = mtcnn(pil_img)

            if face_tensor is not None:
                face_pil = to_pil_image(
                    ((face_tensor + 1) / 2).clamp(0, 1)
                )
                path = os.path.join(worker_dir, f"{count:03d}.jpg")
                face_pil.save(path)
                count += 1
                print(f"  Saved {count}/{n_photos} — {instruction}")
            else:
                print("  No face detected — try again")

        elif key == ord('q'):
            print("Stopped manually")
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\nCapture complete for {name}: {count} photos saved to {worker_dir}/")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--n',    type=int, default=15)
    parser.add_argument('--dir',  default='dataset')
    args = parser.parse_args()

    capture_worker(args.name, args.n, args.dir)