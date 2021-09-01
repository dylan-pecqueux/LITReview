from django import forms
from .models import Ticket, Review

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user',None)
        super(TicketForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')

class ReviewForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.ticket = kwargs.pop('ticket',None)
        self.user = kwargs.pop('user',None)
        super(ReviewForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Review
        fields = ('rating', 'headline', 'body')