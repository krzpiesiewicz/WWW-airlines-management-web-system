from django.contrib import admin
from .models import Ticket, Flight

admin.site.register(Flight)
admin.site.register(Ticket)
