import face_recognition
from PIL import Image
import os

def crop_faces_from_folder(input_folder, output_folder):
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    
    for filename in os.listdir(input_folder):
        
        image_path = os.path.join(input_folder, filename)

        
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"{filename}")

            
            image = face_recognition.load_image_file(image_path)

            face_locations = face_recognition.face_locations(image)

            if not face_locations:
                print(f"No faces {filename}.")
                continue

            
            pil_image = Image.open(image_path)

            
            for i, (top, right, bottom, left) in enumerate(face_locations):
                
                face_image = pil_image.crop((left, top, right, bottom))

                
                cropped_face_name = f"{os.path.splitext(filename)[0]}_face_{i + 1}.jpg"
                output_path = os.path.join(output_folder, cropped_face_name)

               
                face_image.save(output_path)
                print(f"Cropped face {i + 1} from {filename} saved to {output_path}")

    print("Face cropping from all images completed.")

if __name__ == "__main__":
   
    input_folder = input("Enter the folder path containing images: ")

    
    output_folder = input("Enter the folder path to save cropped faces: ")

    crop_faces_from_folder(input_folder, output_folder)
