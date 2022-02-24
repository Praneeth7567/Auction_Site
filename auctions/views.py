from asyncio.windows_events import NULL
from attr import attrs
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import fields
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Listing, User, Bid, Comment, Watch
from django import forms 
from django.contrib.auth.decorators import login_required

class create_form(forms.ModelForm):
    class Meta: 
        model = Listing
        fields = ["item_name","item_description","item_category","start_price","item_image"]

class bid_form(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["current_price"]
        labels = {"current_price":("")}

class comment_form(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["item_comments"]
        labels = {"item_comments":("Add a Comment")}


def index(request):
    return render(request, "auctions/index.html", {
        "data" : Listing.objects.filter(item_status = "OPEN")
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def product(request,name):
    try:
        data = Listing.objects.filter(item_name = name).first()
        com = Comment.objects.filter(item_name = data)
        bid = Bid.objects.filter(item_name = data).first()
        wat = Watch.objects.filter(watchlist = True, watched_by = request.user,item_name = data).exists()
        form_b = bid_form(request.POST or None)
        if form_b.is_valid():
            new_bid = request.POST["current_price"]
            price = Bid.objects.filter(item_name = data)
            start = data.start_price
            if price:
                temp = Bid.objects.get(item_name = data.id).current_price
                if float(new_bid) > float(temp):
                    Bid.objects.filter(item_name = data).update(current_price = new_bid, bid_by = request.user)
                    return HttpResponseRedirect(reverse("product",args = (name,)))
                else:
                    return render(request, "auctions/product.html",{
                    "listing_data"  : data,
                    "comment_data" : com,
                    "bid_data" : bid,
                    "is_Watchlisted" : wat,
                    "bid_form" : bid_form(),
                    "comment_form" : comment_form(),
                    "owner" : False,
                    "status" : True,
                    "message" : "Please enter a bid higher than Current price "
                    })
            else:
                if float(new_bid) > float(start):
                    Bid.objects.create(item_name = data, bid_by = request.user,current_price = new_bid)
                    return HttpResponseRedirect(reverse("product",args = (name,)))
                else:
                    return render(request, "auctions/product.html",{
                    "listing_data"  : data,
                    "comment_data" : com,
                    "bid_data" : bid,
                    "is_Watchlisted" : wat,
                    "bid_form" : bid_form(),
                    "comment_form" : comment_form(),
                    "owner" : False,
                    "status" : True,
                    "start" : True,
                    "message" : "Please enter a bid higher than Start price "
                    })
        form_c = comment_form(request.POST or None)
        if form_c.is_valid():
            new_comment = request.POST["item_comments"]
            Comment.objects.create(item_name = data, comment_by = request.user, item_comments = new_comment)
            return HttpResponseRedirect(reverse("product",args = (name,)))
        if data.item_status == "OPEN" and request.user == data.item_owner:
            return render(request, "auctions/product.html",{
            "listing_data" : data,
            "comment_data" : com,
            "bid_data" : bid,
            "is_Watchlisted" : wat,
            "owner" : True,
            "comment_form" : comment_form(), 
            })
        elif data.item_status == "OPEN":
            return render(request, "auctions/product.html",{
            "listing_data"  : data,
            "comment_data" : com,
            "bid_data" : bid,
            "is_Watchlisted" : wat,
            "bid_form" : bid_form(),
            "comment_form" : comment_form(),
            "owner" : False,
            "status" : True,
            })
        else:
            return render(request, "auctions/product.html",{
            "listing_data"  : data,
            "comment_data" : com,
            "bid_data" : bid,
            "is_Watchlisted" : None,
            "owner" : False,
            "closed" : True,
            "winner": Bid.objects.filter(item_name = data).first()
            })
    except:
        data = Listing.objects.get(item_name = name)
        com = Comment.objects.filter(item_name = data)
        bid = Bid.objects.filter(item_name = data)
        return render(request,"auctions/product.html",{
            "listing_data" : data,
            "comment_data" : com,
            "bid_data" : bid,
            "login" : True
        })

@login_required(login_url="/login")     
def watchlist(request):
    wat = Watch.objects.filter(watched_by = request.user,watchlist=True).values("item_name")
    return render(request,"auctions/watchlist.html",{
        "data" : Listing.objects.filter(id__in = wat)
        # "listing" : Listing.objects.filter()
    })

@login_required(login_url="/login") 
def watchlist_item(request,item_name):
    return(product(request,item_name))

@login_required(login_url="/login")
def categories(request):
    return render(request,"auctions/categories.html",{
        "list" : Listing.objects.values('item_category').distinct().filter(item_status = "OPEN")
    })

@login_required(login_url="/login") 
def category(request,name):
    return render(request, "auctions/category.html",{
        "list" : Listing.objects.filter(item_category = name, item_status = "OPEN"),
        "cate" : name
    })

@login_required(login_url="/login") 
def category_item(request,name,item_name):
    return(product(request,item_name))

@login_required(login_url="/login")     
def create(request):
    form = create_form(request.POST or None)
    if form.is_valid():
        name = form.cleaned_data['item_name']
        price = form.cleaned_data['start_price']
        desc = form.cleaned_data['item_description']
        cate = form.cleaned_data['item_category'].title()
        img = form.cleaned_data['item_image']
        instances = form.save(commit=False)
        instances.item_user = request.user
        Listing.objects.create(item_name = name,  item_description = desc, item_category = cate, start_price = price, item_image = img, item_owner = request.user)
        return product(request,form.cleaned_data['item_name'])
    return render(request,"auctions/create.html",{
        "form" : create_form()
    })

@login_required(login_url="/login")  
def button(request,name):
    listing = Listing.objects.get(item_name = name)
    exist = Watch.objects.filter(item_name=listing,watched_by = request.user,watchlist = True)
    if exist.count() == 0:
        add = Watch(item_name=listing,watchlist=True,watched_by=request.user)
        add.save()
    elif exist.count() == 1:
        Watch.objects.filter(item_name = listing, watched_by=request.user).update(watchlist = False)
    return HttpResponse("success")

@login_required(login_url="/login")  
def close_bid(request,name):
    listing = Listing.objects.get(item_name = name)
    if listing:
        Listing.objects.filter(item_name = listing).update(item_status = "CLOSED")
    return product(request,name)