from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Users

@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email')  # Adjust fields as needed
    search_fields = ('name', 'email')  # Fields to include in search functionality
    ordering = ('id',) 