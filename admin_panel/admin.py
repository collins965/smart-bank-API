from django.contrib import admin
from .models import AdminActionLog

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action', 'target_user', 'loan', 'transaction', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('admin_user__username', 'target_user__username', 'notes')
    readonly_fields = ('timestamp',)

    fieldsets = (
        (None, {
            'fields': ('admin_user', 'action', 'target_user', 'loan', 'transaction', 'notes')
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
        }),
    )
