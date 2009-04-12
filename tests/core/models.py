from django.db import models

class User(models.Model):
    name = models.CharField(max_length=255)
    title = models.CharField(blank=True, max_length=255)
    email = models.EmailField()
    phone = models.CharField(blank=True, max_length=255)