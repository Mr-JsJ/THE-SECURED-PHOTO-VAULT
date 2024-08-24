import csv
import os
from django.conf import settings
# def csv_access(id):
#     with open('path_to_file.csv', mode='r') as file:
#     csv_reader = csv.reader(file)
#     for row in csv_reader:
#         print(row)

def image_folder_access(id):
    user_images_dir = os.path.join(settings.IMAGES_VAULT, f'{id}SVPimages')
    files = os.listdir(user_images_dir)
    print("Files in the folder:")
    for file in files:
         print(file)

