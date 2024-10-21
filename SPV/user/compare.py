import face_recognition
import os
import shutil
import numpy as np

def similar_faces(input_image_path,folder_path,tolerance=0.4):
    image_names=[]
    print(f"Processing input image {os.path.basename(input_image_path)}...")
    input_image = face_recognition.load_image_file(input_image_path)
    input_face_encodings = face_recognition.face_encodings(input_image)

    if not input_face_encodings:
        print("No faces found in the input image.")
        return

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(folder_path, filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)

            for encoding in face_encodings:
                matches = face_recognition.compare_faces(input_face_encodings, encoding, tolerance=tolerance)
                face_distances = face_recognition.face_distance(input_face_encodings, encoding)

                if any(matches) and np.min(face_distances) <= tolerance:
                    print(f"Found a similar face in {filename}.")
                    image_names.append(filename)
                    break

    print("Completed searching for similar faces.")
    return image_names

