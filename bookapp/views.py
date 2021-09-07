from itertools import chain
from django.db.models import CharField, Value, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from .models import Ticket, UserFollows, Review
from .forms import TicketForm, ReviewForm
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
        form = TicketForm(request.POST, request.FILES)
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
    user_followed = UserFollows.objects.filter(followed_user=request.user)
    my_filter_qs = Q()
    for user in user_followed:
        my_filter_qs = my_filter_qs | Q(user=user.user)
    my_filter_qs |= my_filter_qs | Q(user=request.user)
    reviews = Review.objects.filter(my_filter_qs)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = Ticket.objects.filter(my_filter_qs)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    posts = sorted(
        chain(reviews, tickets), 
        key=lambda post: post.time_created, 
        reverse=True
    )
    return render(request, 'bookapp/feed.html', {'posts': posts, 'media_url':settings.MEDIA_URL})

@login_required(login_url='/')
def subscriptions(request):
    followed_by = UserFollows.objects.filter(user=request.user)
    sub = UserFollows.objects.filter(followed_user=request.user)
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

@login_required(login_url='/')
def new_review(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.user = request.user
            m.ticket = ticket
            m.save()
            return redirect(reverse('bookapp:feed'))
    else:
        form = ReviewForm()
    return render(request, 'bookapp/new_review.html', {'form': form, 'ticket': ticket})

@login_required(login_url='/')
def new_ticket_and_review(request):
    if request.method == 'POST':
        ticket_form = TicketForm(request.POST, request.FILES)
        if ticket_form.is_valid():
            save_ticket = ticket_form.save(commit=False)
            save_ticket.user = request.user
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                save_ticket.save()
                rating = review_form.cleaned_data['rating']
                headline = review_form.cleaned_data['headline']
                body = review_form.cleaned_data['body']
                new_review = Review(ticket=save_ticket, rating=rating, headline=headline, body=body, user=request.user)
                new_review.save()
                return redirect(reverse('bookapp:feed'))
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()
    return render(request, 'bookapp/new_ticket_and_review.html', {'ticket_form': ticket_form, 'review_form': review_form})

@login_required(login_url='/')
def posts(request):
    reviews = Review.objects.filter(user=request.user)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = Ticket.objects.filter(user=request.user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    posts = sorted(
        chain(reviews, tickets), 
        key=lambda post: post.time_created, 
        reverse=True
    )
    return render(request, 'bookapp/posts.html', {'posts': posts, 'media_url':settings.MEDIA_URL})

