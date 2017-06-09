import django_filters
from users.models import Profile

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML


class SearchFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = ['entrance_year', 'entrance_school']

    first_name = django_filters.CharFilter(name='first_name', label='Prénom (contient)', lookup_expr='icontains')
    last_name = django_filters.CharFilter(name='last_name', label='Nom (contient)', lookup_expr='icontains')
    common_name = django_filters.CharFilter(name='common_name', label='Nom d\'usage (contient)', lookup_expr='icontains')
    entrance_field = django_filters.CharFilter(name='entrance_field', label='Discipline d\'entrée (contient)', lookup_expr='icontains')


class SearchFormHelper(FormHelper):
    form_tag = False
    form_show_labels = True

    layout = Layout(
        Div(
            Div('first_name', css_class="col-sm-4"),
            Div('last_name', css_class='col-sm-4'),
            Div('common_name', css_class='col-sm-4'),
            css_class='row'
        ),
        Div(
            Div('entrance_school', css_class='col-sm-4'),
            Div('entrance_field', css_class='col-sm-4'),
            css_class="row"
        )
    )


class ProfileListFilter(django_filters.FilterSet):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name']


class ProfileListFormHelper(FormHelper):
    form_tag = False
    form_show_labels = False

    layout = Layout(
        Field('first_name', placeholder='Prénom', css_class='mr-2'),
        Field('last_name', placeholder='Nom', css_class='mr-2')
    )
