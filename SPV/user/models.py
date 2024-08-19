from django.db import models

class Users(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=128)  # Increased for better security

    def __str__(self):
        return self.email