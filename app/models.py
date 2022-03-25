from django.db import models
from django.contrib.auth.models import AbstractUser

class Items_categories(models.Model):
    name = models.CharField(max_length=60, unique=True)

class Statuses(models.Model):
    name = models.CharField(max_length=60, unique=True)

class Districts(models.Model):
    name = models.CharField(max_length=60, unique=True)

class User(AbstractUser):
    city = models.CharField(max_length=60, null=True)
    street = models.CharField(max_length=60, null=True)
    zip_code = models.CharField(max_length=10, null=True)
    phone = models.CharField(max_length=20, null=True)
    deleted_at = models.DateTimeField(auto_now_add=False, null=True)
    district = models.ForeignKey(Districts, on_delete=models.CASCADE, null=True)

class Advertisments(models.Model):
    name = models.CharField(max_length=60)
    description = models.CharField(max_length=1000)
    prize = models.IntegerField()
    picture = models.CharField(max_length=1000, null=True)
    city = models.CharField(max_length=60)
    street = models.CharField(max_length=60, null=True)
    zip_code = models.CharField(max_length=10, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(auto_now_add=False, null=True)
    category = models.ForeignKey(Items_categories, on_delete=models.CASCADE)
    status = models.ForeignKey(Statuses, on_delete=models.CASCADE)
    district = models.ForeignKey(Districts, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class Favorite_advertisments(models.Model):
    ad = models.ForeignKey(Advertisments, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)