from django.conf.urls import url
from annuaire_app import views

app_name = 'annuaire_app'
urlpatterns = [
    url(r'^$', views.AnnuaireView.as_view(), name='index'),
    url(r'^profile/me/',
        views.CurrentProfileDetailView.as_view(), name="current_profile"),
    url(r'^promo/(?P<year>\d+)/$',
        views.ProfilePromotionListView.as_view(), name="promo_list"),
    url(r'^profile/(?P<pk>\d+)/$',
        views.ProfileDetailView.as_view(), name="user_profile"),
]
