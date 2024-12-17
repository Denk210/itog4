from django.contrib import admin

# Register your models here.


from django.contrib import admin
from .models import UserProfile, Application

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'birth_date', 'gender')
    search_fields = ('user__username', 'user__last_name')
    list_filter = ('gender',)

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'application_type', 'status')
    search_fields = ('user__username', 'user__last_name')
    list_filter = ('application_type', 'status')