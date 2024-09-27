import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from PIL import Image

# Assuming this script is located in 'SPV/user/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'fine_tuned_vgg16.h5')

# Load the pre-trained model
model = load_model(MODEL_PATH)

# The categories the model predicts (e.g., 'animal', 'flower', etc.)
CATEGORIES = ['animal', 'flower', 'fruit', 'human', 'landscape', 'vehicles']

def get_image_tag(file):
    try:
        # Open the image file
        img = Image.open(file)
        
        # Convert RGBA to RGB if necessary
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
        return None
