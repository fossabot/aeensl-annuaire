from django.contrib.sites.models import Site
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from django import forms

from django.utils.translation import ugettext as _

from solo.admin import SingletonModelAdmin

from dateutil.relativedelta import relativedelta

from users.models import User, Membership, FieldOfStudy, SiteConfiguration


class MembershipInline(admin.StackedInline):
    model = Membership
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
        return self.initial["password"]


class FieldOfStudyAdmin(admin.ModelAdmin):
    list_display = ('group', 'name')


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'first_year',
                    'membership', 'is_admin', 'is_active')
    list_filter = ('is_admin', )

    form = UserChangeForm
    add_form = UserCreationForm

    search_fields = ('email',)
    ordering = ('email',)

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
            'professional_status',
            'proof_school'
         ]}),
         ('Permissions', {'fields': [
            'is_admin',
            'is_active',
            'groups',
            'is_superuser'
        ]})
    ]

    add_fieldsets = fieldsets.copy()
    add_fieldsets[0] = (None, {
        'classes': ('wide',),
        'fields': ('email', 'password', 'password2')}
    )

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
admin.site.register(FieldOfStudy, FieldOfStudyAdmin)

admin.site.unregister(Site)
admin.site.site_header = "Administration de l'annuaire"
admin.site.register(SiteConfiguration, SingletonModelAdmin)
