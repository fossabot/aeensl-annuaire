from django.contrib.sites.models import Site
from django.contrib import admin

from users.models import User, Membership, Profile, Address
from .views import *

# Update visible models and admin interface parameters

admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Membership, MembershipAdmin)
# admin.site.register(FieldOfStudy, FieldOfStudyAdmin)

admin.site.unregister(Site)
