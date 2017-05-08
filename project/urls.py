from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from users.views import RegistrationWizard, MembershipDetailView, index, ProfileAutocomplete


renew_view = login_required(RegistrationWizard.as_view(condition_dict={
    "login": False
}))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^annuaire/', include('annuaire.urls')),

    # url(r'^register-new/$', RegistrationView.as_view(), name='register_new'),
    url(r'^register/$', RegistrationWizard.as_view(), name='register'),
    url(r'^register/renew/$', renew_view, name='register_renew'),
    url(
        r'^cotisations/(?P<slug>[0-9a-z-]+)/$',
        MembershipDetailView.as_view(),
        name='membership-detail'),

    # Autocomplete API
    url(r'^profile-autocomplete/$',
        ProfileAutocomplete.as_view(),
        name='profile-autocomplete'),

    url(
        r'^$',
        index,
        name='index')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
