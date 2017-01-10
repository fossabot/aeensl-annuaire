from django.contrib.sites.models import Site
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from dateutil.relativedelta import relativedelta

from users.models import User, Membership, SiteConfiguration


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 0


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'first_year', 'membership', 'is_admin', 'is_active')
    list_filter = ('is_admin', )

    fieldsets = [
         (None, {'fields': ['email', 'password']}),
         ('Informations personnelles', {'fields': [
            'first_name',
            'last_name',
            'birth_name',
            'phone_number',
            'address_line_1',
            'address_line_2',
            'postal_code',
            'city',
            'state_province',
            'country'
         ]}),
         ('Informations professionnelles', {'fields': [
            'first_year',
            'status_school',
            'field',
            'professional_status'
         ]}),
         ('Permissions', {'fields': ['is_admin', 'is_active', 'groups', 'is_superuser']})
    ]

    def membership(self, obj):
        last = obj.membership.last()

        if last is None:
            return None

        expire = last.start_date + relativedelta(years=last.duration)
        return expire
    membership.short_description = "Cotisation jusqu'au"


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'uid', 'status', 'created_on', 'start_date')
    list_filter = ('status', 'membership_type')
    list_editable = ('status', )
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'uid')

    fieldsets = [
        (None, {
            'fields': ['user', 'status', 'created_on', 'start_date',
                       'duration', 'in_couple', 'partner_name',
                       'membership_type']
        }),
        ('Paiement', {
            'fields': ['amount', 'payment_amount', 'payment_date',
                       'payment_type', 'payment_bank', 'payment_reference',
                       'payment_first_name', 'payment_last_name']
        })
    ]
    readonly_fields = ('created_on', )

    def utilisateur(self, obj):
        return obj.user

# Update visible models and admin interface parameters
admin.site.register(User, UserAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.unregister(Site)
admin.site.site_header = "Administration de l'annuaire"
admin.site.register(SiteConfiguration, SingletonModelAdmin)
