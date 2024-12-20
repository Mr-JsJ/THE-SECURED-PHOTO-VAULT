from email.message import EmailMessage
from django.conf import settings
from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Users
import pyotp
import os
import csv
import smtplib

#OTP GENERATOR#
def otp_gen(secret):
    totp = pyotp.TOTP(secret)
    return totp.now()


#EMAIL SENDING#
def send_email(to, otp):
    msg = EmailMessage()
    subject = "Verify your email"
    body = f"Your OTP for registration is {otp}. Please do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user = "EMAIL____ID"
    msg['from'] = user
    password = "PASSWORD"
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()


#OTP VALIDATION AT REGESTRATION TIME#
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


#RESENT OTP AT REGSTRATION TIME#
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

#OTP VALIDATION AT LOGIN TIME#
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

def send_email_d(to, otp):
    msg = EmailMessage()
    subject = "Verify your email"
    body = f"Your OTP for deletion of your account is {otp}. Please do not share it with anyone."
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to
    user = "EMAIL___ID"
    msg['from'] = user
    password = "PASSWORD"
    
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

import pyotp
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Users

def confirm_account_deletion(request, user_id):
    user = get_object_or_404(Users, id=user_id)

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        secret = request.session.get('otp_secret')  # OTP secret stored in the session
        
        if not secret:
            messages.error(request, 'Session expired or invalid request.')
            return redirect('gallary')  # Redirect to gallery or other page

        # Verify the OTP using the same logic as login
        totp = pyotp.TOTP(secret)

        if totp.verify(entered_otp, valid_window=3):  # OTP valid for a time window
            # OTP is valid, delete the user account
            user.delete()
            messages.success(request, 'Your account has been deleted.')
            return redirect('logout_d',user_id)  # Redirect to homepage or login page
        else:
            messages.error(request, 'Invalid or expired OTP.')
            return render(request, 'confirm_account_deletion.html', {'user': user})

    return render(request, 'confirm_account_deletion.html', {'user': user})


import shutil

def logout_d(request,user_id):
    if user_id:
        print("qwertyhgfds",user_id)
        # Path to the decrypted folder
        folder = os.path.join(settings.MEDIA_ROOT, 'images_vault', f'{user_id}SVPimages')
        csv_file_path = os.path.join(settings.META_DATA, f'SPV{user_id}.csv')
        # Delete the contents of the decrypted folder
        if os.path.exists(folder):
            shutil.rmtree(folder)
        if os.path.exists(csv_file_path):
            os.remove(csv_file_path)
    # Clear the user's session
    request.session.flush()
    
    # Optionally, display a success message
    messages.success(request, 'You have been logged out successfully.')
    
    # Redirect to the login page
    return redirect('login')