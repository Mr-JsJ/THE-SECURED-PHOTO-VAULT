from django.urls import path
from . import views,otp
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
    path('delete-image/<str:image_name>/', views.delete_image, name='delete_image'),
    path('delete-multiple-images/', views.delete_multiple_images, name='delete_multiple_images'),
    path('face-gallery/',views.face_recognized_gallery, name='face_gallery'),
    path('sorted_gallary/<str:image_name>/',views.sorted_gallary,name='sorted_gallary'),
    path('request_account_deletion/',views.request_account_deletion,name='request_account_deletion'),
    path('confirm_account_deletion<str:user_id>/',views.confirm_account_deletion,name='confirm_account_deletion'),
    path('logout_d<str:user_id>/',otp.logout_d,name='logout_d'),  
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)