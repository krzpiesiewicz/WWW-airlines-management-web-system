from django import forms
from django.db import transaction

from linie_lotnicze.models import Ticket, Flight

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['number_of_seats', 'passenger']

        @transaction.atomic
        def clean(self):
            super().clean()