
from django.urls import path

from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('otp/',views.otp_request,name='otp_request'),
    path('otp2/',views.login_otp,name='login_otp'),
    path('gallery/',views.gallary,name='gallery'),  
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('logout/',views.logout,name='logout'),  
]
