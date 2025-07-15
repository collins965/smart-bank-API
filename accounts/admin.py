from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Profile, Wallet
from django.contrib.admin import SimpleListFilter

# ----- Custom Filters -----

class BalanceRangeFilter(SimpleListFilter):
    title = 'Balance Range'
    parameter_name = 'balance_range'

    def lookups(self, request, model_admin):
        return [
            ('<1K', 'Less than 1K'),
            ('1K-10K', '1K to 10K'),
            ('10K+', 'More than 10K'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '<1K':
            return queryset.filter(balance__lt=1000)
        elif self.value() == '1K-10K':
            return queryset.filter(balance__gte=1000, balance__lte=10000)
        elif self.value() == '10K+':
            return queryset.filter(balance__gt=10000)
        return queryset

# ----- Inline Admins -----

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = 'user'

class WalletInline(admin.StackedInline):
    model = Wallet
    can_delete = False
    verbose_name_plural = "Wallet"
    fk_name = 'user'
    readonly_fields = ('account_number', 'balance', 'created_at')

# ----- Custom User Admin -----

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, WalletInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

# Re-register User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# ----- Profile Admin -----

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'date_of_birth', 'address')
    search_fields = ('user__username', 'phone', 'address')
    list_filter = ('date_of_birth',)

# ----- Wallet Admin -----

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'formatted_balance', 'is_active', 'created_at')
    search_fields = ('user__username', 'account_number')
    list_filter = ('is_active', 'created_at', BalanceRangeFilter)
    readonly_fields = ('account_number', 'created_at')
    actions = ['freeze_selected_wallets']

    def formatted_balance(self, obj):
        return f"KSh {obj.balance:,.2f}"
    formatted_balance.short_description = 'Balance'

    def freeze_selected_wallets(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} wallet(s) successfully frozen.")
    freeze_selected_wallets.short_description = "Freeze selected wallets"
