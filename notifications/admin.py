from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notif_type', 'is_read', 'timestamp')
    list_filter = ('notif_type', 'is_read', 'timestamp')
    search_fields = ('user__username', 'message')
