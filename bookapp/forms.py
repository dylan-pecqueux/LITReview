from django import forms
from .models import Ticket

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(TicketForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')