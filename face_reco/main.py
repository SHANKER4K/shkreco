
import pickle
from time import sleep
import face_recognition as fr
import cv2
import numpy as np
import matplotlib.pyplot as plt

with open("faces.p", "rb") as f:
	faces_info = pickle.load(f)

camera_index = 0

cap = cv2.VideoCapture(camera_index)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

if not cap.isOpened():
    print(f"Error: Could not open video device at index {camera_index}")
    exit()

while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (600, 400), interpolation=cv2.INTER_AREA)
    if not ret:
        print("Error: Failed to capture image")
        break

    # Rotate to landscape, then flip horizontally
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    # frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    frame = cv2.flip(frame, 1)

    face_locations = fr.face_locations(frame, model="hog")
    if face_locations:
        print(f"Found {len(face_locations)} face(s) in the current frame.")
        user_img = frame.copy()
        
        # Get face encodings for all detected faces
        user_face_loc = fr.face_locations(user_img, model="hog")
        user_face_en = fr.face_encodings(user_img, user_face_loc, model="large")
        votes = [0] * len(faces_info)  # Initialize votes for each known face
        # Process each detected face
        for face_idx, face_enc in enumerate(user_face_en):
            # Compare this face against all known faces
            matches = fr.compare_faces([face_info[1] for face_info in faces_info], face_enc)
            face_distances = fr.face_distance([face_info[1] for face_info in faces_info], face_enc)
            min_dist = np.argmin(face_distances)
            if face_distances[min_dist] < 0.6:  # Threshold for a good match
                votes[min_dist] += 1
        # Determine the most likely identity based on votes
        if max(votes) > 0:
            best_match_idx = np.argmax(votes)
            found = faces_info[best_match_idx][0]
        else:
            found = None
        if found:
            print(f"Face {face_idx + 1}: Closest match: {found} with distance {face_distances[min_dist]:.4f}")
            
            # Draw text on frame if match found
        if found and face_idx < len(user_face_loc):
            top, right, bottom, left = user_face_loc[face_idx]
            cv2.rectangle(frame, (left, top), (right, bottom), (250, 5, 5), 1)
            cv2.putText(frame, found, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 5, 5), 1)

    cv2.imshow("Phone Camera Stream", frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()