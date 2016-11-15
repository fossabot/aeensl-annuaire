from django.contrib import admin
from users.models import User, Profile, Membership


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('is_admin', )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_year', 'field')
    search_fields = ('user__first_name', 'user__last_name')


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'uid', 'status', 'created_on', 'start_date')
    list_filter = ('status', 'reference_type', 'membership_type')
    list_editable = ('status', )
    search_fields = ('user__first_name', 'user__last_name', 'uid')


admin.site.register(User, UserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Membership, MembershipAdmin)
