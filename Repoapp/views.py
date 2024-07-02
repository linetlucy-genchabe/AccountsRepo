from django.shortcuts import render,redirect
from django.conf import settings
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.templatetags.static import static
# from django.shortcuts import render, redirect, render_to_response, HttpResponseRedirect
from django.http import HttpResponse, Http404,HttpResponseRedirect
import datetime as dt
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
import json
# Create your views here.




# Create your views here.

def index(request):
    accounts = Accounts.objects.all()
    counties = County.objects.all()

    return render(request, 'index.html', {"accounts":accounts, 'counties':counties})

def user_login(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']  
        
        user = authenticate (request,username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request,"Welcome , you are now logged in")
            return redirect ("index")
        else:
            messages.error(request,'Username or password not correct')
            return redirect('login')
        
    return render(request, 'login.html' )


@login_required(login_url='/login/')
def new_account(request):
    current_user = request.user
    profile = request.user.profile
   

    if request.method == 'POST':
        form = NewAccountForm(request.POST, request.FILES)
        if form.is_valid():
            account = form.save(commit=False)
            account.Author = current_user
            account.author_profile = profile

            account.save()
        return redirect('index')

    else:
        form = NewAccountForm()
    return render(request, 'new_account.html', {"form": form})

@login_required(login_url='/login/')
def update_account(request,id):
    
    update = Accounts.objects.get(id=id)
    if request.method == 'POST':
        form2= AccountUpdateForm(
            request.POST, request.FILES, instance=update)
        if form2.is_valid():
            form2.save()
            return redirect(index)
    else:
        form2 = AccountUpdateForm(instance=update)
    return render(request, 'edit_account.html', {'form2': form2})


@login_required(login_url='/login/')
def search_accounts(request):
    if 'keyword' in request.GET and request.GET["keyword"]:
        search_term = request.GET.get("keyword")
        searched_projects = Accounts.search_accounts(search_term)
        message = f"{search_term}"

        return render(request, 'search.html', {"message":message,"accounts": searched_projects})

    else:
        message = "You haven't searched for any term"
        return render(request, 'search.html', {"message": message})

@login_required(login_url='/login/')
def user_profiles(request):
    current_user = request.user
    
    profile = Profile.objects.get(user=request.user)
    # profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES,instance=profile)   
        if form.is_valid():
            current_user=current_user
            profile = form.save(commit=False)
            profile.save()
            form.save()
            return redirect('profile')
            
    else:
        form = ProfileUpdateForm()


    return render(request, 'profile.html', {"form":form})
@login_required(login_url='/login/')
def kisumu(request):
    accounts = Accounts.objects.all()
    

    return render(request, 'kisumu.html', {"accounts":accounts})

@login_required(login_url='/login/')
def busia(request):
    accounts = Accounts.objects.all()
    

    return render(request, 'busia.html', {"accounts":accounts})


 
def signout(request):
    logout(request)
    messages.success(request,"You have logged out")
           
    return redirect("/")
