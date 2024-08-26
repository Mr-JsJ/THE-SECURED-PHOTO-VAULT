import csv
import os
from django.conf import settings


def csv_access(id):
    csv_file_path = os.path.join(settings.META_DATA,f'SPV{id}.csv')
    Images = {'img_details': []}
    with open(csv_file_path, mode='r') as file:
            csv_reader = csv.DictReader(file)         
            # Iterate through each row in the CSV file
            for row in csv_reader:
                image_detail = {
                    'name': row.get('image_name', ''),        # Use 'image_name' as 'name'
                    'date': row.get('date', ''),              # Use 'date'
                    'tag': row.get('tags', ''),               # Use 'tags' as 'tag'
                    'public_key': row.get('public_key', ''),  # Use 'public_key'
                    'private_key': row.get('private_key', '') # Use 'private_key'
                }
                Images['img_details'].append(image_detail)
    return(Images)



def image_folder_path(id,image_details):
    Images = {'img_details': []}
    user_images_dir = os.path.join(settings.IMAGES_VAULT, f'{id}SVPimages')
    image_files = [f for f in os.listdir(user_images_dir) if os.path.isfile(os.path.join(user_images_dir, f))]
    for detail in image_details['img_details']:
        image_name = detail['name']
        if image_name in image_files:
            detail['file_path'] = os.path.join(settings.IMAGES_VAULT, f'{id}SVPimages', image_name)
            Images['img_details'].append(detail)
    return Images




