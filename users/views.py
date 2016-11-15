from django.shortcuts import render
from django.forms.models import model_to_dict
from formtools.wizard.views import SessionWizardView

from users.models import User

from users.forms import UserForm, ProfileForm, MembershipForm

TEMPLATES = ["form_user.html", "form_profile.html", "form_membership.html"]


class RegistrationWizard(SessionWizardView):
    form_list = [UserForm, ProfileForm, MembershipForm]

    def get_template_names(self):
        return [TEMPLATES[int(self.steps.current)]]

    def get_form_initial(self, step):
        if step == '1':
            step_0 = self.get_cleaned_data_for_step('0')
            print(step_0['email'])
            u = User.objects.filter(email=step_0['email']).get()
            return model_to_dict(u.profile)

    def done(self, form_list, **kwargs):
        return render(self.request, 'done.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })
