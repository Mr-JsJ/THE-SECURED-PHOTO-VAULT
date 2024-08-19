
from django.urls import path

from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('otp/',views.otp_request),
    path('gallery/',views.gallary,name='gallery'),  
]
