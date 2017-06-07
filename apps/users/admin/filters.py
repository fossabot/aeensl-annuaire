from django.contrib.admin.filters import SimpleListFilter
from users.models import User, Membership

class UserProblemsFilter(SimpleListFilter):
    title = u'problèmes'
    parameter_name = ''

    def lookups(self, request, model_admin):
        return (
            ('profile_missing', ('Compte utilisateur sans profil'), ),
            ('need_activation', ('Adhérent mais compte inactif'), ),
        )

    def queryset(self, request, queryset):
        if self.value() == 'profile_missing':
            return queryset.filter(profile=None)

        if self.value() == 'need_activation':
            qs = queryset.filter(is_active=False).select_related('profile')
            # Inactive users: small qs, querying all directly
            profile_ids = [p.profile.id for p in qs if p.profile]

            qs_membership = Membership.objects.filter(profile__in=profile_ids)
            qs_membership = qs_membership.order_by('profile__id', '-created_on').distinct('profile__id')

            return User.objects.filter(profile__in=[q.profile.id for q in qs_membership if q.status == 'accepted'])

        return queryset
