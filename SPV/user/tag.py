import os
import numpy as np
import tensorflow as tf
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from PIL import Image


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'fine_tuned_vgg16.h5')


model = load_model(MODEL_PATH)

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

CATEGORIES = ['animal', 'flower', 'fruit', 'human', 'landscape', 'vehicles']

def get_image_tag(file):
    try:
       
        img = Image.open(file)
        
        
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Resize the image to 224x224 (required input size for VGG16)
        img = img.resize((224, 224))
        
        # Convert the image to a numpy array
        img_array = image.img_to_array(img)
        
        # Expand dimensions to match the input shape (1, 224, 224, 3)
        img_array = np.expand_dims(img_array, axis=0)
        
        # Preprocess the image (scale pixel values, apply VGG-specific transformations)
        img_array = preprocess_input(img_array)
        
        # Make the prediction
        predictions = model.predict(img_array)
        
        # Get the index of the highest prediction score
        predicted_index = np.argmax(predictions[0])
        
        # Get the corresponding category label
        predicted_tag = CATEGORIES[predicted_index]
        
       
        
        return predicted_tag
    
    except Exception as e:
        print(f"Error processing the image: {str(e)}")
        return None, None

# Example usage
if __name__ == '__main__':
    image_path = os.path.join(BASE_DIR, 'example_image.jpg')  # Example image path
    predicted_tag, confidence = get_image_tag(image_path)
    
    if predicted_tag:
        print(f"Predicted Tag: {predicted_tag} with confidence {confidence:.2f}")
    else:
        print("Failed to process the image.")

