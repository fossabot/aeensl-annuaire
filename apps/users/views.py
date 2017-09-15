from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction

from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from django.shortcuts import render, redirect, reverse
from django.contrib import auth


from formtools.wizard.views import SessionWizardView
from dal import autocomplete

# Local forms and models
from users.forms import UserLoginForm, ProfileForm, MembershipForm, ProfileAddressForm, AddressForm
from users.models import Membership, User, Profile, Address


def index(request, **kwargs):
    if request.user.is_authenticated():
        return redirect("annuaire:index")
    else:
        return redirect("register")


class ProfileAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        from django.db.models import Q

        qs = Profile.objects

        if self.q:
            Q_first_name = Q(first_name__istartswith=self.q)
            Q_last_name = Q(last_name__istartswith=self.q)
            qs = qs.filter(Q_first_name | Q_last_name)

        return qs


class RegistrationView(CreateView):
    model = User
    fields = ['first_name', 'last_name']
    template_name = "users/form.html"


class RegistrationWizard(SessionWizardView):
    form_list = [
        ("login", UserLoginForm),
        ("user_info", ProfileAddressForm),
        ("membership", MembershipForm)
    ]

    templates = {
        'login': "form_login.html",
        'user_info': "form_user.html",
        'membership': "form_membership.html"
    }

    file_storage = FileSystemStorage(location=settings.MEDIA_TMP)

    def get_template_names(self):
        return [self.templates[self.steps.current]]

    def get_form_initial(self, step):
        u = None
        if step == 'user_info':
            if not isinstance(self.request.user, auth.models.AnonymousUser):
                u = self.request.user
            else:
                step_login = self.get_cleaned_data_for_step('login')
                if step_login:
                    u = auth.authenticate(
                        username=step_login.get('email'),
                        password=step_login.get('password'))

            if u:
                return {
                    'profile': u.profile.__dict__,
                    'address': u.profile.address_set.all()[0].__dict__
                }

    @transaction.atomic
    def done(self, form_list, form_dict, **kwargs):
        """
        Gather the data from the three forms. If the user already exists,
        update the profile, if not create a new user. Then add a new membership.
        """
        login_step = self.get_cleaned_data_for_step('login')
        address_step = self.get_cleaned_data_for_step('user_info')['address']
        profile_step = self.get_cleaned_data_for_step('user_info')['profile']
        membership_step = self.get_cleaned_data_for_step('membership')

        # Renew membership for current user
        if login_step is None:
            u = self.request.user

            # Update the user profile
            profile_form = ProfileForm(profile_step, instance=u.profile)
            u.profile = profile_form.save()
            u.save()
        else:
            # Create a new user from steps 'login' & 'profile'
            u = User(email=login_step['email'])
            u.is_active = False  # Not activated yet
            p = Profile(**profile_step)
            p.save()

            u.profile = p
            u.save()

        # Create or update address info
        addresses = u.profile.address_set.all()
        if len(addresses) > 0:
            add = addresses[0]
            add = AddressForm(address_step, instance=addresses[0])
        else:
            add = Address(**address_step)
            add.profile = u.profile
        add.save()

        # Create a new Membership object
        membership = Membership(**membership_step)
        membership.profile = u.profile
        membership.start_date = membership.next_start_date()
        membership.amount = membership.compute_amount()
        membership.duration = 1  # valid for one year
        membership.save()

        # Send a confirmation email
        membership.email_user(status="submitted")

        mb_url = self.request.build_absolute_uri(
            reverse('membership-detail', args=[membership.uid]))

        return render(self.request, 'form_done.html', {
            'user': u,
            'cotisation': membership,
            'url': mb_url
        })


class MembershipDetailView(DetailView):
    slug_field = 'uid'
    queryset = Membership.objects.all()


def process_payment_view(request, **kwargs):
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    if not request.user.is_authenticated():
        return redirect("register")

    if not request.method == "POST":
        return redirect("/")

    token = request.POST.get("stripeToken")
    membership_uid = request.POST.get("membershipID")

    m = Membership.objects.get(uid=membership_uid)        

    try:
        m.accept()
        m.payment_type = 'CARD'        
        
        charge  = stripe.Charge.create(
            amount      = int(m.amount * 100),
            currency    = "eur",
            source      = token,
            description = "Cotisation annuelle à l'assocation",
            metadata    = {"membership_id": m.uid}
        )
    except stripe.error.CardError as ce:
        return False, ce
    else:
        m.save()
        return redirect("membership-detail", m.uid)
