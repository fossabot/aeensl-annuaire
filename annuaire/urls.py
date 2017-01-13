from django.conf.urls import include, url
from django.contrib import admin

from django.views.generic.base import RedirectView
from users.views import RegistrationWizard, MembershipDetailView, UserListView, UserDetailView, CurrentUserDetailView

urlpatterns = (
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^users/me/', CurrentUserDetailView.as_view(), name="current_user_profile"),
    url(r'^users/(?P<pk>\d+)/$', UserDetailView.as_view(), name="user_profile"),
    url(r'^users/$', UserListView.as_view(), name="user_list"),

    url(r'^register/$', RegistrationWizard.as_view(), name='register'),
    url(
        r'^cotisations/(?P<slug>[0-9a-z-]+)/$',
        MembershipDetailView.as_view(),
        name='membership-detail'),

    url(
        r'^$',
        RedirectView.as_view(url='register/', permanent=False),
        name='index'),
)
