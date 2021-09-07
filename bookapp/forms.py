from django import forms
from .models import Ticket, Review

RATINGS_CHOICE = [(i, i) for i in range(6)]

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')

class ReviewForm(forms.Form):
    headline = forms.CharField(max_length=128)
    rating = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=RATINGS_CHOICE,
    ) 
    body = forms.CharField(max_length=8192, required=False, widget=forms.Textarea)
