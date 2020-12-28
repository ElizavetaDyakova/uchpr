from django.contrib import admin
from .models import Profile, Chat, Message


admin.site.register(Profile)
admin.site.register(Chat)
admin.site.register(Message)



from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# admin.site.unregister(User)

