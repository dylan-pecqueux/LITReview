from django import forms
from .models import Ticket, Review

RATINGS_CHOICE = [(i, i) for i in range(6)]

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('headline', 'rating', 'body')
        widgets = {'rating': forms.RadioSelect(choices=RATINGS_CHOICE)}
