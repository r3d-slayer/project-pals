from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User,Profile
# Register your models here.

class UserAdminModel(BaseUserAdmin):
    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ["username", "id" ,"email", "is_admin", "credits","rating"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("Personal info", {"fields": ["username"]}),
        (None, {"fields": ["email", "password","first_name","last_name","credits","rating","otp","is_email_verified","forget_password", "last_login"]}),
        ("Permissions", {"fields": ["is_admin", "is_active"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["username", "email",  "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email"]
    filter_horizontal = []

class profileAdmin(admin.ModelAdmin):
    list_display = ["user","full_name", "verified","image", "online_status"]
    list_editable = ["verified"]


# Now register the new UserAdmin...
admin.site.register(User, UserAdminModel)
admin.site.register(Profile, profileAdmin)

