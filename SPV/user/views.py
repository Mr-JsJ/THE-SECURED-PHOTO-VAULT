from django.shortcuts import render
from django.http import HttpResponse  
# Create your views here.

def gallary(request):
     Images_details={
          'name':'img-01.jpg',
          'date':'10-08-2002',
          'tag':'object'
     }
     return render(request,'gallary.html',Images_details)

def signup(request):
     return render(request,'signup.html')

def login(request):
     return render(request,'login.html')