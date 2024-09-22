from email.message import EmailMessage
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Users
import pyotp
import os
import csv
from dotenv import load_dotenv
import smtplib


def otp_gen(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()
#=============================================================================================================
def send_email(to, otp):
    msg = EmailMessage()
    subject = "Verify your email"
    body = f"Your OTP for registration is {otp}. Please do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    load_dotenv()
    user = os.getenv("EMAIL_USER")
    msg['from'] = user
    password = os.getenv("EMAIL_PASSWORD")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()
#=================================================================================================================
def reg_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        secret = request.session.get('otp_secret')

        if not secret:
            messages.error(request, 'Session expired or invalid request.')
            return redirect('signup')

        totp = pyotp.TOTP(secret)

        # Allow OTP to be valid for 2 minutes (120 seconds)
        if totp.verify(entered_otp, valid_window=3):  # 4 intervals of 30 seconds each = 120 seconds
            # OTP is valid, create the user
            name = request.session.get('name')
            email = request.session.get('email')
            password = request.session.get('password')
            print(password)
            new_user = Users(name=name, email=email, password=password)

            new_user.save()
              # Create a folder for the user with their ID
            user_id = new_user.id
            user_images_dir = os.path.join(settings.IMAGES_VAULT,f'{user_id}SVPimages')
            
            # Ensure the directory is created if it doesn't exist
            os.makedirs(user_images_dir, exist_ok=True)
            # Subdirectory path for decrypted images
            decrypted_dir_path= os.path.join(user_images_dir, 'decrypted')
            # Create the decrypted subdirectory
            os.makedirs(decrypted_dir_path, exist_ok=True)

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
            return redirect('reg_otp')

    return render(request, 'otp.html')
#===========================================================================================================================

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
    
    return redirect('reg_otp')

#============================================================================================================================
def login_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        secret = request.session.get('otp_secret')

        if not secret:
            messages.error(request, 'Session expired or invalid request.')
            return redirect('login')

        totp = pyotp.TOTP(secret)

        if totp.verify(entered_otp, valid_window=3):  # Allow OTP to be valid for 2 minutes
            # OTP is valid, log the user in
            email = request.session.get('login_email')
            user = Users.objects.get(email=email)
            request.session['user_id'] = user.id
            request.session['email'] = user.email
            request.session.pop('otp_secret', None)
            request.session.pop('login_email', None)
            return redirect('gallary')  # Redirect to the gallery or user's profile page
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('login_otp')

    return render(request, 'otp.html')
