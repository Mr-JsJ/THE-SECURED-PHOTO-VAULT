from django.shortcuts import render,redirect
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

# Create your views here.
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
    
    for image in image_details['img_details']:
        if image['name'] in image_filenames:
            encrypted_image_path = os.path.join(images_dir, image['name'])
            decrypted_image_path = os.path.join(images_dir, 'decrypted', image['name'])
            
            # Ensure the decrypted directory exists
            os.makedirs(os.path.dirname(decrypted_image_path), exist_ok=True)
            
            # Decrypt the image if it hasn't been decrypted yet
            if not os.path.exists(decrypted_image_path):
                decrypt_image(user_id, image['name'], image['private_key'], image['public_key'])
            img_name=image['name'].replace('.bin', '') 
             
            # Add the image details to the list
            img_details.append({
                'name': img_name,  # Use the original name from the CSV
                'date': image['date'],  # Use the date from the CSV
                'tag': image['tag'],    # Use the tag from the CSV
                'decrypted_image_url': os.path.join(settings.MEDIA_URL, 'images_vault', f'{user_id}SVPimages', 'decrypted', img_name),
            })

    context = {
        'img_details': img_details,
        'MEDIA_URL': settings.MEDIA_URL,
        'user_id': user_id,  # Pass user_id to the template
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