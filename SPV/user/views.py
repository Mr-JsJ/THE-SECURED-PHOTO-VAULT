from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password,check_password
from .models import Users
from django.contrib import messages
from .otp import otp_gen,send_email,otp_request,login_otp
import pyotp



# Create your views here.
def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        password = request.POST['password']
        print(password)
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

# def gallary(request):
#      Images={'img_details':[
#           {'name':'img-01.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#           {'name':'img-02.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#           {'name':'img-03.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#           {'name':'img-04.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#           {'name':'img-05.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#           {'name':'img-06.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#            {'name':'img-07.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#            {'name':'img-08.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },
#           {'name':'img-09.jpg',
#           'date':'10-08-2002',
#           'tag':'object'
#           },]}
     
#      return render(request,'gallary.html',Images)

def gallary(request):

    Images={'img_details':[{}]}

    return render(request,'gallary.html',Images)