from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin

from dateutil.relativedelta import relativedelta
from django_reverse_admin import ReverseModelAdmin
import import_export

from .forms import *
from .filters import *


class UserAdmin(BaseUserAdmin, ReverseModelAdmin):
    class Meta:
        exclude = ('username', )

    list_display = ('email', 'profile', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active', 'groups', UserProblemsFilter)
    ordering = ('email', )

    search_fields = ('email', )

    fieldsets = [
        (None, {'fields': [
            'email',
            'password',
        ]}),
        ('Permissions', {'fields': [
           'is_admin',
           'is_active',
           'is_superuser'
        ]})
    ]

    inline_type = 'stacked'
    inline_reverse = [
        'profile',
    ]

    form = UserChangeForm
    add_form = UserCreationForm
    add_fieldsets = fieldsets.copy()
    add_fieldsets[0] = (None, {
        'classes': ('wide',),
        'fields': ('email', 'password', 'password2')}
    )

    actions = ['activate_account']
    def activate_account(modeladmin, request, queryset):
        for u in queryset:
            from allauth.account.forms import ResetPasswordForm

            rp_form = ResetPasswordForm({'email': u.email})
            rp_form.is_valid()
            # rp_form.fields['email'] = u.email
            # rp_form.clean_email()
            rp_form.save(request)

            u.is_active = True
            u.save()

    activate_account.short_description = "Activer les utilisateurs sélectionnés"


class ProfileAdmin(admin.ModelAdmin):
    # resource_class = UserResource

    list_display = ('user', 'first_name', 'last_name', 'entrance_year',
                    'membership', )

    search_fields = ('user__email', 'first_name', 'last_name', 'entrance_year')
    ordering = ('user',)
    inlines = (AddressInline, )

    fieldsets = [
        #  (None, {'fields': ['user']}),
         ('Informations personnelles', {'fields': [
            'first_name',
            'last_name',
            'common_name',
            'gender',
            'phone_number',
         ]}),
         ('Parcours à l\'ENS et carrière', {'fields': [
            'entrance_year',
            'status_school',
            'entrance_field',
            'professional_status',
            'proof_school'
         ]}),
         ('Administratif', {'fields': [
            'transfer_data',
            'is_honorary',
            'annuaire_papier',
            'bulletin_papier'
         ]})
    ]

    def user(self, obj):
        return obj.user

    def membership(self, obj):
        last = obj.membership.first()

        if last is None:
            return None

        expire = last.start_date + relativedelta(years=last.duration)
        return expire
    membership.short_description = "Cotisation jusqu'au"


class MembershipAdmin(import_export.admin.ImportExportModelAdmin):
    resource_class = MembershipResource

    list_display = ('utilisateur', 'uid', 'status', 'created_on', 'start_date')
    list_filter = ('status', 'membership_type')
    list_editable = ('status', )
    search_fields = ('profile__user__email', 'profile__first_name', 'profile__last_name', 'uid')

    fieldsets = [
        (None, {
            'fields': ['profile', 'status', 'created_on', 'start_date',
                       'duration', 'in_couple', 'partner_name',
                       'membership_type']
        }),
        ('Paiement', {
            'fields': ['amount', 'payment_amount', 'payment_on',
                       'payment_type', 'payment_bank', 'payment_reference',
                       'payment_name']
        })
    ]
    readonly_fields = ('created_on', )

    def utilisateur(self, obj):
        return obj.profile
