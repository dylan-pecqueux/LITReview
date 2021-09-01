from django.contrib import admin
from .models import Ticket, UserFollows, Review

admin.site.register(Ticket)
admin.site.register(UserFollows)
admin.site.register(Review)

