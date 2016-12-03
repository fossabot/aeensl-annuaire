from django.conf.urls import include, url
from django.contrib import admin

from users.views import RegistrationWizard, MembershipDetailView

urlpatterns = (
    url(r'^admin/', admin.site.urls),
    # url(r'^users/', include('annuaire.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^register/$', RegistrationWizard.as_view(), name='register'),
    url(
        r'^cotisations/(?P<slug>[0-9a-z-]+)/$',
        MembershipDetailView.as_view(),
        name='membership-detail'),
)
