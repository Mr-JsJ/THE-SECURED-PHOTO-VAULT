import cv2
import numpy as np
import face_recognition

def detect_and_crop_faces(image_data):
    # Convert image data to an array
    np_img = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if img is None:
        print("Could not load image data.")
        return []

    # Detect faces using face_recognition
    face_locations = face_recognition.face_locations(img)

    cropped_faces = []

    for (top, right, bottom, left) in face_locations:
        # Crop the face from the image
        face = img[top:bottom, left:right]

        # Encode the cropped face as a JPEG image
        _, buffer = cv2.imencode('.jpg', face)
        cropped_faces.append(buffer.tobytes())

    return cropped_faces
