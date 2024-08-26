
from django.urls import path

from . import views

urlpatterns = [
    path('',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('otp/',views.reg_otp,name='reg_otp'),
    path('otp2/',views.login_otp,name='login_otp'),
    path('gallary/',views.gallary,name='gallary'),  
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('upload/', views.upload, name='upload'),
    path('logout/',views.logout,name='logout'),  
    # path('gallery/<int:user_id>/', views.gallery, name='gallery')
]
