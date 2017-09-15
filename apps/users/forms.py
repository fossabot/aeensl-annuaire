from .models import Membership, Profile, Address

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from django.db.models.fields import BLANK_CHOICE_DASH

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Submit, Div, HTML
from crispy_forms.bootstrap import InlineRadios, PrependedText
from dal import autocomplete


from betterforms.multiform import MultiModelForm
from phonenumber_field.widgets import PhoneNumberInternationalFallbackWidget

User = get_user_model()


class UserLoginForm(forms.ModelForm):
    # password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)

    class Meta:
        # fields = ['email', 'password']
        fields = ['email']
        model = User

    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_tag = False
        self.helper.layout = Layout(
            'email',
            # PrependedText('password', 'Si déjà adhérent'),
            Submit('submit', 'Étape suivante')
        )

        # self.fields['password'].required = False

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


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['line_1', 'line_2', 'postal_code', 'city', 'country']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Fieldset(
                'Adresse postale',
                Field('line_1', css_class='autocomplete-address'),
                'line_2',
                Div(
                    Div('postal_code', css_class='col-sm-2'),
                    Div('city', css_class='col-sm-6'),
                    Div('country', css_class='col-sm-4'),
                    css_class='row'),
            )
        )


# TODO: cache the queryset
Q_fields = Profile.objects.values("entrance_field").distinct()
ENTRANCE_CHOICES = [x['entrance_field'].title() for x in Q_fields if x['entrance_field'] is not None]
ENTRANCE_CHOICES = sorted(ENTRANCE_CHOICES)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['gender', 'first_name', 'last_name', 'common_name', 'phone_number',
                  'entrance_year', 'entrance_field', 'entrance_school',
                  'professional_status', 'status_school', 'proof_school']

        widgets = {
            'phone_number': PhoneNumberInternationalFallbackWidget(),
        }

    gender = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-check-inline'}),
        choices=list(Profile.GENDER_CHOICES),
        label='Raison sociale')

    entrance_field = forms.ChoiceField(
        choices=zip(ENTRANCE_CHOICES, ENTRANCE_CHOICES),
        label="Discipline d'entrée")

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False

        self.helper.layout = Layout(
            Fieldset(
                'Informations personnelles',
                InlineRadios('gender', template="crispy/radioselect_inline.html"),
                'first_name',
                Div(
                    Div('last_name', css_class="col-sm-8"),
                    Div('common_name', css_class='col-sm-4'),
                    css_class='row'),

                'phone_number'
            ),

            Fieldset(
                'Parcours à l\'ENS',
                'entrance_year',
                'entrance_field',
                'entrance_school',
                'status_school',
                'professional_status',
                HTML(
                    """<div class='alert alert-info' role='alert'>
                    <h5 class='alert-heading'>Documents supplémentaires</h4>
                    <p>S’il s’agit de votre première adhésion à l’Association des élèves et anciens élèves, et afin de faciliter les opérations de vérification, nous vous remercions de bien vouloir déposer un document officiel attestant de votre passage à l’ENS (justificatif de scolarité, certificat d’inscription, carte d’étudiant, <i>etc.</i>).
                    En cas de difficultés, vous pouvez ignorer cette étape. Si nécessaire, le trésorier de l’Association prendra alors votre attache avant de confirmer votre adhésion. Il convient de noter que les opérations de vérification peuvent prendre plus de temps en l’absence de document.</p>
                    </div>"""),
                'proof_school',
            )
        )


class ProfileAddressForm(MultiModelForm):
    base_fields = {}

    form_classes = {
        'address': AddressForm,
        'profile': ProfileForm,
    }


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ['membership_type', 'payment_type', 'in_couple',
                  'partner_name']

        widgets = {
            'in_couple': forms.RadioSelect
        }

    partner_name = forms.ModelChoiceField(
        queryset=Profile.objects.all(), required=False,
        widget=autocomplete.ModelSelect2(url='profile-autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Fieldset(
                "Montant et réglement",
                'payment_type',
                'membership_type',

                Div(
                    Div(InlineRadios('in_couple',
                        template="crispy/radioselect_inline.html"),
                        css_class='col-sm-3'),
                    Div('partner_name', css_class='col-sm-9'),
                    css_class='row')
            )
        )
