from django.contrib import admin
from .models import Investment

@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'asset_type', 'symbol', 'units', 'total_value', 'last_updated')
    list_filter = ('asset_type', 'last_updated')
    search_fields = ('user__username', 'symbol')
    readonly_fields = ('initial_value', 'current_price', 'total_value', 'last_updated')
    ordering = ('-last_updated',)

    fieldsets = (
        (None, {
            'fields': ('user', 'asset_type', 'symbol', 'units')
        }),
        ('Price Info', {
            'fields': ('initial_value', 'current_price', 'total_value', 'last_updated')
        }),
    )
