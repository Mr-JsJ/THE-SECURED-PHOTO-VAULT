import os
import numpy as np
from keras.models import load_model
from keras.preprocessing import image
from keras.applications.vgg16 import preprocess_input
from PIL import Image 

# Assuming this script is located in 'SPV/user/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'fine_tuned_vgg16.h5')

model = load_model(MODEL_PATH)

# The categories the model predicts (e.g., 'animal', 'flower', etc.)
CATEGORIES = ['animal', 'flower', 'fruit', 'human', 'landscape', 'vehicles']

def get_image_tag(file):
    # Load the image for prediction
    img = Image.open(file)
    img = img.resize((224, 224)) 
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)  # Preprocess image for VGG16

    # Make the prediction
    predictions = model.predict(img_array)

    # Get the index of the highest prediction score
    predicted_index = np.argmax(predictions[0])

    # Get the corresponding category label
    predicted_tag = CATEGORIES[predicted_index]

    return predicted_tag