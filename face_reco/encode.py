# Load the images from images folder, get the ids and encode them
import os
import face_recognition as fr
import cv2
import pickle

images = os.listdir("images")
ids = [os.path.splitext(image)[0] for image in images]
images = [cv2.imread(f"images/{image}") for image in images]

def face_encoding(face):
    face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
    face_loc = fr.face_locations(face, model='large')
    return fr.face_encodings(face, face_loc, model='large')[0]

print("Encoding")
face_encodings = [face_encoding(face) for face in images]
print("Finished encoding")

faces_info = list(zip(ids, face_encodings))
print('Saving faces info')
open("faces.p", "wb").write(pickle.dumps(faces_info))
print('Saving faces Done')