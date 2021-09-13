from itertools import chain
from django.db.models import CharField, Value, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, get_user_model
from django.urls import reverse
from django.conf import settings
from .models import Ticket, UserFollows, Review
from .forms import TicketForm, ReviewForm, AccountCreationForm


def index(request):
    return render(request, 'bookapp/index.html')

def register(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(reverse('bookapp:feed'))
    else:
        form = AccountCreationForm()

    context = {'form': form}
    return render(request, 'registration/register.html', context)

@login_required(login_url='/')
def new_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            save = form.save(commit=False)
            save.user = request.user
            save.save()
            return redirect(reverse('bookapp:feed'))
    else:
        form = TicketForm()
    return render(request, 'bookapp/new_ticket.html', {'form': form})

@login_required(login_url='/')
def feed(request):
    my_tickets = Ticket.objects.filter(user=request.user)
    response_to_my_reviews = Review.objects.filter(ticket__in=my_tickets)
    response_to_my_reviews = response_to_my_reviews.annotate(
        content_type=Value('REVIEW', CharField()))
    user_followed = UserFollows.objects.filter(followed_user=request.user)
    my_filter_qs = Q()
    for user in user_followed:
        my_filter_qs = my_filter_qs | Q(user=user.user)
    my_filter_qs |= my_filter_qs | Q(user=request.user)
    reviews = Review.objects.filter(my_filter_qs).exclude(ticket__in=my_tickets)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    tickets = Ticket.objects.filter(my_filter_qs)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    ticket_response = [i.ticket for i in Review.objects.filter(user=request.user)]
    posts = sorted(
        chain(reviews, tickets, response_to_my_reviews), 
        key=lambda post: post.time_created, 
        reverse=True
    )
    context = {'posts': posts, 'media_url':settings.MEDIA_URL, 'ticket_response':ticket_response}
    return render(request, 'bookapp/feed.html', context)

@login_required(login_url='/')
def subscriptions(request):
    followed_by = UserFollows.objects.filter(user=request.user)
    sub = UserFollows.objects.filter(followed_user=request.user)
    if request.method == 'POST':
        try:
            User = get_user_model()
            search_user = User.objects.get(username=request.POST['search'])
        except (KeyError, User.DoesNotExist):
            message = "Aucun utilisateur trouvé"
        else:
            already_exist = [i.user for i in UserFollows.objects.filter(followed_user=request.user)]
            print(already_exist)
            if search_user != request.user and search_user not in already_exist:
                follow = UserFollows(user=search_user, followed_user=request.user)
                follow.save()
                message = "ajouté"
            if search_user == request.user:
                message = "Vous ne pouvez pas vous ajouter vous-même !"
            if search_user in already_exist:
                message = "Utilisateur deja ajouté !"
    else:
        message = None

    context = {'sub': sub, 'followed_by': followed_by, 'message': message}
    return render(request, 'bookapp/subscriptions.html', context)

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
            save_form = form.save(commit=False)
            save_form.user = request.user
            save_form.ticket = ticket
            save_form.save()
            return redirect(reverse('bookapp:feed'))
    else:
        form = ReviewForm()
    
    context = {'form': form, 'ticket': ticket, 'media_url':settings.MEDIA_URL}
    return render(request, 'bookapp/new_review.html', context)

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
                save_review = review_form.save(commit=False)
                save_review.user = request.user
                save_review.ticket = save_ticket
                save_review.save()
                return redirect(reverse('bookapp:feed'))
    else:
        ticket_form = TicketForm()
        review_form = ReviewForm()

    context = {'ticket_form': ticket_form, 'review_form': review_form}
    return render(request, 'bookapp/new_ticket_and_review.html', context)

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

@login_required(login_url='/')
def update_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    context = {'review': review}
    form = ReviewForm(request.POST or None, instance=review)
    if form.is_valid():
        form.save()
        return redirect(reverse('bookapp:posts'))
    context["form"] = form
    return render(request, 'bookapp/update_review.html', context)

@login_required(login_url='/')
def delete_review(request, pk):
    review_to_delete = get_object_or_404(Review, pk=pk)
    if request.user == review_to_delete.user:
        review_to_delete.delete()
    return redirect(reverse('bookapp:posts'))

@login_required(login_url='/')
def update_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    context = {'ticket': ticket}
    form = TicketForm(request.POST or None, request.FILES or None, instance=ticket)
    if form.is_valid():
        form.save()
        return redirect(reverse('bookapp:posts'))
    context["form"] = form
    return render(request, 'bookapp/update_ticket.html', context)

@login_required(login_url='/')
def delete_ticket(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    if request.user == ticket.user:
        ticket.delete()
    return redirect(reverse('bookapp:posts'))
