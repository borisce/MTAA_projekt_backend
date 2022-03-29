from django.conf import settings
from django.conf.urls.static import static
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
    path('delete_favourite/', views.delete_favourite),
    path('my_profile/', views.my_profile),
    path('user_profile/<int:id>', views.user_profile),
    path('my_ads/', views.my_ads),
    path('ad_detail/<int:id>', views.ad_detail),
    path('get_image/<name>', views.get_image),
    path('ads/', views.ads),
    path('favourite_ads/', views.favourite_ads)
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
