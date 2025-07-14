from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth', 'address')
    search_fields = ('user__username', 'phone', 'address')
    list_filter = ('date_of_birth',)
