from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.hashers import make_password,check_password
from .models import Users
from django.contrib import messages
from django.conf import settings
from .secure import upload,decrypt_image
from PIL import Image
from .otp import otp_gen,send_email,reg_otp,login_otp,resend_otp
from .csvfile import csv_access
import os
import pyotp
import shutil
from django.urls import reverse
import csv
from datetime import datetime

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        
        # Validate inputs
        if not name or not email or not password:
            messages.error(request, 'All fields are required.')
            return redirect('signup')

        # Check if the email is already registered
        if Users.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('signup')

        # Generate a secret for TOTP
        secret = pyotp.random_base32()
        otp = otp_gen(secret)
        print("Generated OTP (signup):", otp)

        # Send OTP to user's email
        send_email(email, otp)
        
        # Save user details and TOTP secret in the session for verification
        request.session['name'] = name
        request.session['email'] = email
        request.session['password'] = make_password(password)
        request.session['otp_secret'] = secret

        # Redirect to OTP verification page
        return redirect('reg_otp')

    return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, 'Email and password are required.')
            return redirect('login')

        # Check if the email exists
        try:
            user = Users.objects.get(email=email)
        except Users.DoesNotExist:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

        # Check password
        if not check_password(password, user.password):
            messages.error(request, 'Invalid email or password.')
            return redirect('login')

        # Generate and send OTP
        secret = pyotp.random_base32()
        otp = otp_gen(secret)
        send_email(email, otp)

        # Save user details and OTP secret in the session for verification
        request.session['login_email'] = email
        request.session['otp_secret'] = secret

        # Redirect to OTP verification page
        return redirect('login_otp')

    return render(request, 'login.html')


def logout(request):
    user_id = request.session.get('user_id')
    if user_id:
        # Path to the decrypted folder
        decrypted_folder = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages', 'decrypted')
        
        # Delete the contents of the decrypted folder
        if os.path.exists(decrypted_folder):
            shutil.rmtree(decrypted_folder)
    
    # Clear the user's session
    request.session.flush()
    
    # Optionally, display a success message
    messages.success(request, 'You have been logged out successfully.')
    
    # Redirect to the login page
    return redirect('login')


def gallary(request):
    user_id = request.session.get('user_id')
    images_dir = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages')
    image_filenames = os.listdir(images_dir)
    
    # Get the image details from the CSV
    image_details = csv_access(user_id)
    img_details = []

    # Get the tag and date parameters from the request
    tag_filter = request.GET.get('tag', None)
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    search_query = request.GET.get('search', '').strip()
    for image in image_details['img_details']:
        if image['name'] in image_filenames:
            encrypted_image_path = os.path.join(images_dir, image['name'])
            decrypted_image_path = os.path.join(images_dir, 'decrypted', image['name'])
            
            # Ensure the decrypted directory exists
            os.makedirs(os.path.dirname(decrypted_image_path), exist_ok=True)
            
            # Decrypt the image if it hasn't been decrypted yet
            if not os.path.exists(decrypted_image_path):
                decrypt_image(user_id, image['name'], image['private_key'], image['public_key'])
                
            img_name = image['name'].replace('.bin', '')

            # Convert image date to datetime for comparison
            img_date = datetime.strptime(image['date'], "%Y-%m-%d %H:%M:%S")
            
            # Add the image details to the list if it meets the date and tag filters
            if (not start_date or img_date >= datetime.strptime(start_date, "%Y-%m-%d")) and \
               (not end_date or img_date <= datetime.strptime(end_date, "%Y-%m-%d")):
                img_details.append({
                    'name': img_name,
                    'date': image['date'],
                    'tag': image['tag'],
                    'decrypted_image_url': os.path.join(settings.MEDIA_URL, 'images_vault', f'{user_id}SVPimages', 'decrypted', img_name),
                })

    # Filter images by tag if a tag is provided
    if tag_filter:
        img_details = [img for img in img_details if img['tag'] == tag_filter]
    # Filter images by search query if provided
    if search_query:
        img_details = [img for img in img_details if search_query.lower() in img['name'].lower()]
    # Sort images by date
    img_details.sort(key=lambda x: x['date'])

    context = {
        'img_details': img_details,
        'MEDIA_URL': settings.MEDIA_URL,
        'user_id': user_id,
        'selected_tag': tag_filter,
        'start_date': start_date,
        'end_date': end_date,
        'search_query': search_query,
    }

    return render(request, 'gallary.html', context)




def details(request,image_name,image_date,image_tag):
    # Use the image_name parameter in your logic
    user_id = request.session.get('user_id')
    image_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages','decrypted',image_name)
    with Image.open(image_path) as img:
        img_dimension = f"{img.width}x{img.height}"
        img_format = img.format

    context = {'img': image_name,
               'date':image_date,
               'tag':image_tag,
               'user_id': user_id,
               'dimension': img_dimension,
               'format': img_format,
               }
    return render(request,'details.html',context)




def delete_image(request, image_name):
    if request.method == "POST":
        user_id = request.session.get('user_id')

        image_path = os.path.join(settings.MEDIA_ROOT, f'images_vault/{user_id}SVPimages/decrypted/{image_name}')
        encrypted_image_name = f"{image_name}.bin"
        encrypted_image_path = os.path.join(settings.MEDIA_ROOT, f'images_vault/{user_id}SVPimages/{encrypted_image_name}')

        # Delete decrypted image
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete encrypted image
        if os.path.exists(encrypted_image_path):
            os.remove(encrypted_image_path)

        # Delete face images related to the image
        face_images_dir = os.path.join(settings.MEDIA_ROOT, f'images_vault/{user_id}SVPimages/faces')
        for face_image in os.listdir(face_images_dir):
            if face_image.startswith(image_name):
                os.remove(os.path.join(face_images_dir, face_image))

        # Update CSV file
        csv_file_path = os.path.join(settings.MEDIA_ROOT, f'meta_data/SPV{user_id}.csv')
        if os.path.exists(csv_file_path):
            updated_rows = []
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['image_name'] != encrypted_image_name and not row['image_name'].startswith(f"{image_name}_face"):
                        updated_rows.append(row)
            with open(csv_file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

        return redirect('gallary')

    return redirect('gallary')


def delete_multiple_images(request):
    if request.method == "POST":
        selected_images = request.POST.getlist('image_names')
        user_id = request.session.get('user_id')
        images_dir = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages')

        if not selected_images:
            messages.error(request, "No images were selected for deletion.")
            return redirect(reverse('gallary'))

        csv_file_path = os.path.join(settings.MEDIA_ROOT, f'meta_data/SPV{user_id}.csv')

        for image_name in selected_images:
            decrypted_image_path = os.path.join(images_dir, 'decrypted', image_name)
            encrypted_image_name = f"{image_name}.bin"
            encrypted_image_path = os.path.join(images_dir, encrypted_image_name)

            if os.path.exists(decrypted_image_path):
                os.remove(decrypted_image_path)

            if os.path.exists(encrypted_image_path):
                os.remove(encrypted_image_path)

            face_images_dir = os.path.join(images_dir, 'faces')
            for face_image in os.listdir(face_images_dir):
                if face_image.startswith(image_name):
                    os.remove(os.path.join(face_images_dir, face_image))

        if os.path.exists(csv_file_path):
            updated_rows = []
            with open(csv_file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['image_name'] not in [f"{img}.bin" for img in selected_images] and \
                       not any(row['image_name'].startswith(f"{img}_face") for img in selected_images):
                        updated_rows.append(row)
            with open(csv_file_path, 'w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerows(updated_rows)

        messages.success(request, "Selected images and associated faces have been deleted successfully.")
        return redirect(reverse('gallary'))

    return redirect(reverse('gallary'))
