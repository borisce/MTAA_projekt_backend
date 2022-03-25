from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('create_new_ad/', views.create_new_ad)
]
