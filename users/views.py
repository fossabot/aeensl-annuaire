from django.shortcuts import render
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate

from formtools.wizard.views import SessionWizardView

from users.forms import UserForm, ProfileForm, MembershipForm

TEMPLATES = ["form_user.html", "form_profile.html", "form_membership.html"]


class RegistrationWizard(SessionWizardView):
    form_list = [UserForm, ProfileForm, MembershipForm]

    def get_template_names(self):
        return [TEMPLATES[int(self.steps.current)]]

    def get_form_initial(self, step):
        if step == '1':
            step_0 = self.get_cleaned_data_for_step('0')
            u = authenticate(
                username=step_0['email'],
                password=step_0['password'])

            if u:
                return model_to_dict(u.profile)

    def done(self, form_list, **kwargs):
        step_0 = self.get_cleaned_data_for_step('0')
        step_1 = self.get_cleaned_data_for_step('1')
        step_2 = self.get_cleaned_data_for_step('2')

        u = authenticate(
            username=step_0['email'],
            password=step_0['password'])

        if u:
            # Update the user profile
            profile = u.profile
            profile_form = ProfileForm(step_1, instance=profile)
            profile_form.save()
        else:
            # Create a new user and a new profile
            u = UserForm(step_0).save()

            profile = ProfileForm(step_1).save(commit=False)
            profile.user = u
            profile.save()

        # Create a new Membership object
        membership = MembershipForm(step_2).save(commit=False)
        membership.user = u
        membership.amount = membership.compute_amount()
        membership.start_date = membership.next_start_date()
        membership.duration = 1

        membership.save()

        return render(self.request, 'form_done.html', {
            'first_name': u.first_name,
            'last_name': u.last_name,
            'form_data': [form.cleaned_data for form in form_list],
        })
