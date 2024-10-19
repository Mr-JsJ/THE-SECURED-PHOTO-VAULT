import cv2
import numpy as np
from io import BytesIO

# Load Haar Cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def detect_and_crop_faces(image_data):
    # Convert image data to an array
    np_img = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        print("Could not load image data.")
        return []

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    cropped_faces = []

    for (x, y, w, h) in faces:
        face = img[y:y+h, x:x+w]
        _, buffer = cv2.imencode('.jpg', face)
        cropped_faces.append(buffer.tobytes())

    return cropped_faces
