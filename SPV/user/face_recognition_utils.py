import face_recognition
import numpy as np
from sklearn.cluster import KMeans
import os

def detect_faces(image_path):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    return face_locations, face_encodings

def extract_face_features(image_paths):
    face_data = {}
    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        _, encodings = detect_faces(image_path)
        if encodings:
            face_data[image_name] = encodings[0]
    return face_data

def cluster_faces(face_data):
    encodings = np.array(list(face_data.values()))
    kmeans = KMeans(n_clusters=3)  # Adjust the number of clusters as needed
    kmeans.fit(encodings)

    clustered_faces = {}
    for idx, label in enumerate(kmeans.labels_):
        image_name = list(face_data.keys())[idx]
        if label not in clustered_faces:
            clustered_faces[label] = []
        clustered_faces[label].append(image_name)
    
    return clustered_faces
