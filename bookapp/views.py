from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.urls import reverse
from .models import Ticket
from .forms import TicketForm
from django.conf import settings


def index(request):
    return render(request, 'bookapp/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(reverse('bookapp:feed'))
    else:
        form = UserCreationForm()
        
    context = {'form': form}
    return render(request, 'registration/register.html', context)

@login_required(login_url='/')
def new_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.save()
            return redirect(reverse('bookapp:feed'))
    else:
        form = TicketForm()
    return render(request, 'bookapp/new_ticket.html', {'form': form})

@login_required(login_url='/')
def feed(request):
    ticket_list = Ticket.objects.order_by('-time_created')
    return render(request, 'bookapp/feed.html', {'tickets': ticket_list, 'media_url':settings.MEDIA_URL})
