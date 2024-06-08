from django.contrib import admin
from django.contrib.sessions.models import Session
from .models import AddMoneyInfo

# Register your models here.


class AddMoneyInfoAdmin(admin.ModelAdmin):
    list_display = ['user', 'add_money', 'quantity', 'Date', 'Category']
    list_filter = ['add_money', 'Category']
    search_fields = ['user__username', 'add_money', 'Category']


admin.site.register(AddMoneyInfo, AddMoneyInfoAdmin)
admin.site.register(Session)
