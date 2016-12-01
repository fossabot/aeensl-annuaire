from .models import Profile, Membership

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Div
from crispy_forms.bootstrap import InlineRadios, PrependedText

User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            PrependedText('password', 'Si déjà adhérent'),
            Submit('submit', 'Étape suivante')
        )

        self.fields['password'].required = False

    def clean(self):
        data = self.cleaned_data

        if data.get('email') and data.get('password'):
            user = authenticate(
                username=data['email'],
                password=data['password'])
            if user is None:
                raise forms.ValidationError({
                    'email': "L’adresse e-mail ou le mot de passe sont incorrects."
                }, code='invalid')

        elif data.get('email') and User.objects.filter(email=data['email']):
            raise forms.ValidationError({
                'email': "Cette adresse existe déjà. Veuillez entrer votre "
                         "mot de passe pour ré-adhérer."
            }, code='invalid')


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'first_name',
            'last_name',
            'birth_name',
            'phone_number',
            'first_year',
            'field',
            'professional_status',

            'address_line_1',
            'address_line_2',
            'postal_code',
            'city',
            'country',
        ]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Fieldset(
                'Informations personnelles',
                'first_name',
                'last_name',
                'birth_name',
                'phone_number'
            ),

            Fieldset(
                'Adresse postale',
                Field('address_line_1', css_class='autocomplete-address'),
                'address_line_2',
                Div(
                    Div('postal_code', css_class='col-sm-2'),
                    Div('city', css_class='col-sm-6'),
                    Div('country', css_class='col-sm-4'),
                    css_class='row'),
            ),

            Fieldset(
                'Informations professionelles',
                'first_year',
                'field',
                'professional_status'
            )
        )


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = [
            'membership_type',
            'payment_type',
            'in_couple',
            'partner_name'
        ]
        widgets = {
            'in_couple': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Fieldset(
                "Montant et réglement",
                'payment_type',
                'membership_type',

                Div(
                    Div(InlineRadios('in_couple'), css_class='col-sm-2'),
                    Div('partner_name', css_class='col-sm-10'),
                    css_class='row')
            )
        )
