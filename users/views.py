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
        u = authenticate(
            username=step_0['email'],
            password=step_0['password'])
        if u:
            first_name = u.first_name
            last_name = u.last_name
        else:
            first_name = step_0['first_name']
            last_name = step_0['last_name']

        return render(self.request, 'form_done.html', {
            'first_name': first_name,
            'last_name': last_name,
            'form_data': [form.cleaned_data for form in form_list],
        })
