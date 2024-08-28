from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password,check_password
from .models import Users
from django.contrib import messages
from .otp import otp_gen,send_email,reg_otp,login_otp,resend_otp
from .csvfile import csv_access
from PIL import Image
from django.conf import settings
import pyotp
import os
from .secure import upload
from datetime import datetime
import csv

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
    # Clear the user's session
    request.session.flush()
    # Optionally, display a success message
    messages.success(request, 'You have been logged out successfully.')    
    # Redirect to the login page
    return redirect('login')



# def upload(request):
#     user_id = request.session.get('user_id')

#     if request.method == 'POST':
#         images = request.FILES.getlist('images')

#         # Directory where user's images will be stored
#         user_images_dir = os.path.join(settings.IMAGES_VAULT, f'{user_id}SVPimages')
#         os.makedirs(user_images_dir, exist_ok=True)

#         # Path to the user's CSV file for metadata storage
#         csv_file_path = os.path.join(settings.META_DATA, f'SPV{user_id}.csv')

#         # Open the CSV file in append mode
#         with open(csv_file_path, mode='a', newline='') as csvfile:
#             fieldnames = ['image_name', 'public_key', 'private_key', 'tags', 'date']
#             writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

#             # Iterate over the uploaded images
#             for image in images:
#                 # Save the image to the user's directory
#                 image_path = os.path.join(user_images_dir, image.name)
#                 with open(image_path, 'wb+') as destination:
#                     for chunk in image.chunks():
#                         destination.write(chunk)

                

#                 # Collect image metadata
#                 image_metadata = {
#                     'image_name': image.name,
#                     'public_key':'',
#                     'private_key':'' ,
#                     'tags': request.POST.get('tags', 'on tag'),  # Assuming you have a form field for tags
#                     'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 }

#                 # Write metadata to the CSV file
#                 writer.writerow(image_metadata)

#         # Optionally, add a success message
#         messages.success(request, 'Images uploaded successfully!')

#     return render(request, 'upload.html')


def gallary(request):
    user_id = request.session.get('user_id')
    images_dir = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages')
    image_filenames = os.listdir(images_dir)
    
    # Get the image details from the CSV
    image_details = csv_access(user_id)
    img_details = []
    for image in image_details['img_details']:
        if image['name'] in image_filenames:
            img_details.append({
                'name': image['name'],
                'date': image['date'],  # Use the date from the CSV
                'tag': image['tag'],    # Use the tag from the CSV
                'public_key': image.get('public_key'),  # Include other data if necessary
                'private_key': image.get('private_key'),
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
    image_path = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages',image_name)
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