from .models import Profile, Membership

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(Fieldset(
                    "Nouvelle adhésion",
                    'first_name',
                    'last_name',
                ), css_class="card card-block"),
                css_class="col-sm-6"
            ),
            Div(
                Div(Fieldset(
                    "Déjà adhérent",
                    'email',
                    'password',
                ), css_class="card card-block"),
                css_class="col-sm-6"
            ),
            Submit('submit', 'Continuer')
        )

        for key in self.fields:
            self.fields[key].required = False

    def clean(self):
        data = self.cleaned_data

        if data.get('email') and data.get('password'):
            user = authenticate(
                username=data['email'],
                password=data['password'])
            if user is None:
                raise forms.ValidationError(message="Invalid user account")

        else:
            if data.get('first_name') and data.get('last_name'):
                pass
            else:
                raise forms.ValidationError(message="blabla")


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'married_name',
            'phone_number',
            'address',
            'first_year',
            'field',
            'notes',
        ]


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = [
            'reference_type',
            'in_couple',
            'partner_name',
            'membership_type'
        ]
