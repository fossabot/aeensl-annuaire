from .models import Membership, Profile, Address

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.translation import ugettext as _
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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['gender', 'first_name', 'last_name', 'common_name', 'phone_number',
                  'entrance_year', 'entrance_field', 'entrance_school',
                  'professional_status', 'status_school', 'proof_school',
                  'annuaire_papier', 'bulletin_papier']

        widgets = {
            'phone_number': PhoneNumberInternationalFallbackWidget(),
            'annuaire_papier': forms.RadioSelect,
            'bulletin_papier': forms.RadioSelect
        }

    gender = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-check-inline'}),
        choices=list(Profile.GENDER_CHOICES),
        label='Civilité')

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
                Div(
                    Div('entrance_school', css_class="col-sm-6"),
                    Div('status_school', css_class='col-sm-6'),
                    css_class='row'),
                'professional_status',
                HTML(
                    """<div class='alert alert-info' role='alert'>
                    <h5 class='alert-heading'>Justificatif de passage (uniquement en cas de première adhésion)</h4>
                    <p>S’il s’agit de votre première adhésion à l’Association des élèves et anciens élèves, et afin de faciliter les opérations de vérification, nous vous remercions de bien vouloir déposer un document officiel attestant de votre passage à l’ENS (justificatif de scolarité, certificat d’inscription, carte d’étudiant, <i>etc.</i>).</p>
                    <p>En cas de difficultés, vous pouvez ignorer cette étape. Si nécessaire, le trésorier de l’Association prendra alors votre attache avant de confirmer votre adhésion. Il convient de noter que les opérations de vérification peuvent prendre plus de temps en l’absence de document.</p>
                    </div>"""),
                'proof_school',
            ),

            Fieldset(
                "Réception de l'annuaire et du bulletin",
                HTML(
                    """<p>Vous avez la possibilité de recevoir l'annuaire de
                    l'association et le bulletin par voie postale ou 
                    directement par email.</p>"""),
                'annuaire_papier',
                'bulletin_papier'
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
        fields = ['membership_type', 'payment_type', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)

        self.helper.layout = Layout(
            Fieldset(
                "Montant et réglement",
                'membership_type',
                Field('payment_type', label="Type de paiement (si applicable)"),
                'comments'
            )
        )

    def fields_required(self, fields):
        """ Used for conditionally marking fields as required. """
        for field in fields:
            if not self.cleaned_data.get(field, ''):
                msg = forms.ValidationError(_("This field is required."))
                self.add_error(field, msg)

    def clean(self):
        """
        Only accept empty payment methods if the memberhip is free.
        """
        membership_type = self.cleaned_data.get('membership_type')

        if membership_type != Membership.MEMBERSHIP_TYPE_FREE:
            self.fields_required(["payment_type"])

        return self.cleaned_data
