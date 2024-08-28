from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('otp/',views.reg_otp,name='reg_otp'),
    path('login_otp/',views.login_otp,name='login_otp'),
    path('gallary/',views.gallary,name='gallary'),  
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('upload/', views.upload, name='upload'),
    path('logout/',views.logout,name='logout'),  
    path('details/<str:image_name>/<str:image_date>/<str:image_tag>/', views.details, name='details'), 
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)