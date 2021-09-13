from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Ticket, Review

RATINGS_CHOICE = [(i, i) for i in range(6)]

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')
        labels = {
            'title': 'Titre',
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('headline', 'rating', 'body')
        widgets = {'rating': forms.RadioSelect(choices=RATINGS_CHOICE)}

class AccountCreationForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder':("Nom d'utilisateur")})
        self.fields['password1'].widget.attrs.update({'placeholder':('Mot de passe')})        
        self.fields['password2'].widget.attrs.update({'placeholder':('Confirmation de mot de passe')})
