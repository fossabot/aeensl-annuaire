from django.shortcuts import render
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate

from django.views.generic import DetailView

from formtools.wizard.views import SessionWizardView

from users.forms import UserLoginForm, UserForm, MembershipForm
from users.models import Membership

TEMPLATES = ["form_login.html", "form_user.html", "form_membership.html"]


class RegistrationWizard(SessionWizardView):
    form_list = [UserLoginForm, UserForm, MembershipForm]

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
        step_0 = self.get_cleaned_data_for_step('0')
        step_1 = self.get_cleaned_data_for_step('1')
        step_2 = self.get_cleaned_data_for_step('2')

        u = authenticate(
            username=step_0['email'],
            password=step_0['password'])

        if u:
            # Update the user profile with the step 1
            user_form = UserForm(step_1, instance=u)
            user_form.save()
        else:
            # Create a new user from steps 0 and 1
            u = UserForm(step_1).save()
            u.username = step_0['email']
            u.is_active = False  # Not registered yet

        # Create a new Membership object
        membership = MembershipForm(step_2).save(commit=False)
        membership.user = u
        membership.start_date = membership.next_start_date()
        membership.amount = membership.compute_amount()
        membership.duration = 1
        membership.save()

        return render(self.request, 'form_done.html', {
            'user': u,
            'cotisation': membership,
        })


class MembershipDetailView(DetailView):
    slug_field = 'uid'
    queryset = Membership.objects.all()

    def get_object(self):
        object = super(MembershipDetailView, self).get_object()
        return object
