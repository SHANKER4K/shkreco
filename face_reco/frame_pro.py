import cv2
import face_recognition as fr
import numpy as np
def preprocess_frame(frame):
    # تحسين الإضاءة
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    frame = cv2.merge((l, a, b))
    frame = cv2.cvtColor(frame, cv2.COLOR_LAB2BGR)
    return frame

def show_frames(original, preprocessed):
    cv2.imshow("Original Frame", original)
    cv2.imshow("Preprocessed Frame", preprocessed)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

frame = cv2.imread("image.jpg")
frame_ = preprocess_frame(frame)
# show_frames(frame, frame_)

face_locations = fr.face_locations(frame,model="hog")
face_locations_ = fr.face_locations(frame_,model="hog")

face_em = fr.face_encodings(frame, face_locations, model="hog")
face_em_ = fr.face_encodings(frame_, face_locations_, model="hog")

# print("Original Frame:")
# print("Face Locations:", face_locations)
# print("Face Encodings:", face_em)

# print("\nPreprocessed Frame:")
# print("Face Locations:", face_locations_)
# print("Face Encodings:", face_em_)

if face_em and face_em_:
    print(fr.compare_faces(face_em, face_em_[0]))
    print(fr.face_distance(face_em, face_em_[0]))
else:
    print("No face encodings found in one of the frames.")