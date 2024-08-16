
from django.urls import path

from . import views

urlpatterns = [
    path('gallery/',views.gallary,name='gallery'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.login,name='login'),
    path('otp/',views.otp_request),
]
