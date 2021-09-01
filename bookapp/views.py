from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from .models import Ticket, UserFollows
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

@login_required(login_url='/')
def subscriptions(request):
    followed_by = UserFollows.objects.filter(user=request.user)
    sub = UserFollows.objects.filter(followed_user=request.user)
    print(sub)
    print(followed_by)
    if request.method == 'POST':
        try:
            User = get_user_model()
            search_user = User.objects.get(username=request.POST['search'])
        except (KeyError, User.DoesNotExist):
            return render(request, 'bookapp/subscriptions.html', {'sub': sub, 'followed_by': followed_by, 'message': "Aucun utilisateur trouvé"})
        else:
            already_exist = [i for i in UserFollows.objects.filter(user=search_user)]
            if search_user != request.user and not already_exist:
                follow = UserFollows(user=search_user, followed_user=request.user)
                follow.save()
                return render(request, 'bookapp/subscriptions.html', {'sub': sub, 'followed_by': followed_by, 'message': "Utilisateur ajouté !"})
            else:
                return render(request, 'bookapp/subscriptions.html', {'sub': sub, 'followed_by': followed_by, 'message': "Utilisateur deja ajouté !"})
    else:
        return render(request, 'bookapp/subscriptions.html', {'sub': sub, 'followed_by': followed_by})

@login_required(login_url='/')
def delete_sub(request, pk):
    sub_to_delete = UserFollows.objects.get(pk=pk)
    if request.user == sub_to_delete.followed_user:
        sub_to_delete.delete()
    return redirect(reverse('bookapp:subscriptions'))

