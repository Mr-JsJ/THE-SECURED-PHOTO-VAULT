from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password
from .models import Users
from django.contrib import messages
from .otp import otp_gen, send_email
import pyotp
import os
from django.conf import settings
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
        return redirect('otp_request')

    return render(request, 'signup.html')

def resend_otp(request):
    # Check if the user is in the session
    if 'email' not in request.session:
        messages.error(request, 'Session expired. Please sign up again.')
        return redirect('signup')
    
    email = request.session.get('email')
    secret = request.session.get('otp_secret')

    if not email or not secret:
        messages.error(request, 'Invalid request. Please try again.')
        return redirect('signup')
    
    # Generate a new OTP
    otp = otp_gen(secret)
    
    # Send the new OTP to the user's email
    send_email(email, otp)
    
    messages.success(request, 'A new OTP has been sent to your email.')
    
    return redirect('otp_request')


def otp_request(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        secret = request.session.get('otp_secret')

        if not secret:
            messages.error(request, 'Session expired or invalid request.')
            return redirect('signup')

        totp = pyotp.TOTP(secret)
        print("Entered OTP:", entered_otp)
        print("Secret:", secret)

        # Allow OTP to be valid for 2 minutes (120 seconds)
        if totp.verify(entered_otp, valid_window=3):  # 4 intervals of 30 seconds each = 120 seconds
            # OTP is valid, create the user
            name = request.session.get('name')
            email = request.session.get('email')
            password = request.session.get('password')

            new_user = Users(name=name, email=email, password=password)
            new_user.save()
              # Create a folder for the user with their ID
            user_id = new_user.id
            user_images_dir = os.path.join(settings.IMAGES_VAULT, f'{user_id}SVPimages')

            # Ensure the directory is created if it doesn't exist
            os.makedirs(user_images_dir, exist_ok=True)

            csv_file_path = os.path.join(settings.META_DATA,f'SPV{user_id}.csv')
            with open(csv_file_path, mode='w', newline='') as csvfile:
                fieldnames = ['image_name', 'public_key', 'private_key', 'tags', 'date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            # Clear session
            request.session.flush()

            return redirect('login')  # Redirect to login after successful registration
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('otp_request')

    return render(request, 'otp.html')


def login(request):
     return render(request,'login.html')

def gallary(request):
     Images={'img_details':[
          {'name':'img-01.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
          {'name':'img-02.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
          {'name':'img-03.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
          {'name':'img-04.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
          {'name':'img-05.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
          {'name':'img-06.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
           {'name':'img-07.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
           {'name':'img-08.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },
          {'name':'img-09.jpg',
          'date':'10-08-2002',
          'tag':'object'
          },]}
     
     return render(request,'gallary.html',Images)