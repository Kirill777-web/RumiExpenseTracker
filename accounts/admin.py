from django.contrib import admin
from .models import UserProfile

# Register your models here.


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profession', 'savings', 'income']
    search_fields = ['user__username', 'profession']


admin.site.register(UserProfile, UserProfileAdmin)
