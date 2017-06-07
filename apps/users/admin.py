from django.contrib.sites.models import Site
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django import forms
from django.utils.translation import ugettext as _

from django_reverse_admin import ReverseModelAdmin
import import_export
from dateutil.relativedelta import relativedelta

from users.models import User, Membership, Profile, Address


from django.utils.encoding import force_text

import logging
log = logging.getLogger(__name__)


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 0


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password confirmation'), widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', )
        exclude = ('username', )

    def is_valid(self):
        log.info(force_text(self.errors))
        return super(UserCreationForm, self).is_valid()

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=_("Password"))

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password")


# class FieldOfStudyAdmin(admin.ModelAdmin):
#     list_display = ('group', 'name')


class UserResource(import_export.resources.ModelResource):
    class Meta:
        model = User


class UserAdmin(BaseUserAdmin, ReverseModelAdmin):
    class Meta:
        exclude = ('username', )

    list_display = ('email', 'profile', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active', )
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


class MembershipResource(import_export.resources.ModelResource):
    class Meta:
        model = Membership


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


# Update visible models and admin interface parameters

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Membership, MembershipAdmin)
# admin.site.register(FieldOfStudy, FieldOfStudyAdmin)

admin.site.unregister(Site)
