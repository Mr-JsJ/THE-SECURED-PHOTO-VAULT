from django.shortcuts import render
from django.http import HttpResponse  
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
     return render(request,'signup.html')

def login(request):
     return render(request,'login.html')

def otp_request(request):
     return render(request,'otp.html')