from django.shortcuts import render
from django.http import HttpResponse  
from .forms import UserForm
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

from django.shortcuts import render, redirect
from .forms import UserForm

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import UserForm
from .models import User

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User

def signup(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists. Please use a different email.')
            else:
                user = form.save(commit=False)
                user.password = make_password(user.password)
                user.save()
                return redirect('login')
    else:
        form = UserForm()

    return render(request, 'signup.html', {'form': form})



def login(request):
     return render(request,'login.html')

def otp_request(request):
     return render(request,'otp.html')