from django.conf.urls import include, url
from django.contrib import admin

from users.views import RegistrationWizard

urlpatterns = (
    url(r'^admin/', admin.site.urls),
    # url(r'^users/', include('annuaire.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^register/$', RegistrationWizard.as_view(), name='register'),
)
