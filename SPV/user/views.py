from django.shortcuts import render,redirect
from django.contrib.auth.hashers import make_password
from .models import Users
from django.contrib import messages
from .otp import otp_gen
# Create your views here.
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
       # Hash the password
        hashed_password = make_password(password)

        # Create and save the user
        new_user = Users(name=name, email=email, password=hashed_password)
        new_user.save()

        # Redirect to a success page or login
        return redirect('login')  # Assuming you have a login view

    return render(request, 'signup.html')




def login(request):
     return render(request,'login.html')

def otp_request(request):
     return render(request,'otp.html')