from django.shortcuts import render
from django.contrib.auth import authenticate

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import set_script_prefix
from django.urls import reverse

from django.views.generic import DetailView, ListView

from formtools.wizard.views import SessionWizardView
from post_office import mail

from users.forms import UserLoginForm, UserForm, MembershipForm
from users.models import Membership, User


TEMPLATES = ["form_login.html", "form_user.html", "form_membership.html"]


class RegistrationWizard(SessionWizardView):
    form_list = [UserLoginForm, UserForm, MembershipForm]
    file_storage = FileSystemStorage(location=settings.MEDIA_TMP)

    def get_template_names(self):
        return [TEMPLATES[int(self.steps.current)]]

    def get_form_initial(self, step):
        if step == '1':
            step_0 = self.get_cleaned_data_for_step('0')
            u = authenticate(
                username=step_0['email'],
                password=step_0['password'])

            if u:
                return u.__dict__

    def done(self, form_list, **kwargs):
        """
        Gather the data from the three forms. If the user already exists,
        update the profile, if not create a new user. Then add a new membership.
        """
        form_list = list(form_list)  # Convert view to list

        step_0 = self.get_cleaned_data_for_step('0')
        step_1 = self.get_cleaned_data_for_step('1')

        u = authenticate(
            username=step_0['email'],
            password=step_0['password'])

        if u:
            # Update the user profile with the step 1
            user_form = UserForm(step_1, instance=u)
            user_form.save()
        else:
            # Create a new user from steps 0 and 1
            u = form_list[1].save(commit=False)
            u.email = step_0['email']
            u.is_active = False  # Not registered yet
            u.save()

        # Create a new Membership object
        membership = form_list[2].save(commit=False)
        membership.user = u
        membership.start_date = membership.next_start_date()
        membership.amount = membership.compute_amount()
        membership.duration = 1  # valid for one year
        membership.save()

        mail.send(
            u.email,
            'luc@lyon-normalesup.org',  # For development purposes
            template='membership_submitted',
            context={
                'membership': membership
            },
        )

        return render(self.request, 'form_done.html', {
            'user': u,
            'cotisation': membership,
        })


class MembershipDetailView(DetailView):
    slug_field = 'uid'
    queryset = Membership.objects.all()


class UserDetailView(DetailView):
    queryset = User.objects.all()


class CurrentUserDetailView(UserDetailView):
    def get_object(self):
        return self.request.user


class UserListView(ListView):
    model = User
