from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.register, name='register'),
    path('registration_success/', views.registration_success, name='registration_success'),
    path('profile/', views.profile, name='profile'),
    path('applications/', views.applications, name='applications'),
    path('apply/', views.submit_application, name='submit_application'),
    path('regulations/', views.regulations, name='regulations'),
    path('admin_analytics/', views.admin_analytics, name='admin_analytics'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('weather/', views.weather_view, name='weather'),
]