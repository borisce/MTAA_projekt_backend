from django.contrib import admin
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register),
    path('login/', views.login),
    path('logout/', views.logout),
    path('create_new_ad/', views.create_new_ad),
    path('add_favourite_ads/', views.add_favourite_ads),
    path('update_profile/', views.update_profile),
    path('update_ad/', views.update_ad),
    path('delete_ad/', views.delete_ad),
    path('delete_favorite/', views.delete_favorite),
    path('my_profile/', views.my_profile),
    path('user_profile/<int:id>', views.user_profile),
    path('my_ads/', views.my_ads),
    path('ad_detail/<int:id>', views.ad_detail)
]
