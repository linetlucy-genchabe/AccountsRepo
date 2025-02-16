from django.shortcuts import get_object_or_404, render,redirect
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
import csv
from django.http import JsonResponse
import json


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

def county(request):
    counties=County.objects.all()
    

    return render(request, 'index.html', {"counties":counties})

def county_detail(request, county_id):
    county = get_object_or_404(County, id=county_id)
    subcounty = county.subcounty.all()  # Fetch subcounties for this county
    return render(request, 'county.html', {'county': county, 'subcounty': subcounty})

def subcounty_detail(request, subcounty_id):
    subcounty = get_object_or_404(Subcounty, id=subcounty_id)
    accounts = subcounty.accountnames.all()  # Fetch accounts for this subcounty
    return render(request, 'subcounty.html', {'subcounty': subcounty, 'accounts': accounts})

# def export_accounts_csv(request):
#     # Define response as a CSV file
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="accounts.csv"'

#     # Create a CSV writer
#     writer = csv.writer(response)
    
#     # Write the header row
#     writer.writerow(['Name', 'Contact UUID', 'Community Health Unit', 'Username', 'Password',
#                      'Account Category', 'Subcounty', 'County'])

#     # Fetch all accounts and write to CSV
#     accounts = Accounts.objects.all()
#     for account in accounts:
#         writer.writerow([
#             account.Name, 
#             account.Contact_UUID, 
#             account.Community_Health_Unit, 
#             account.Username,
#             account.Password,
#             account.account_category.name, 
#             account.account_subcounty.name, 
#             account.account_county.name, 
#             # account.Admin.username if account.Admin else "N/A",
#             # account.pub_date.strftime('%Y-%m-%d %H:%M:%S')  # Format the date
#         ])

#     return response

def export_accounts_csv(request):
    # Get filter parameters
    county_id = request.GET.get('county')
    subcounty_id = request.GET.get('subcounty')

    # Define response as a CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts.csv"'

    # Create a CSV writer
    writer = csv.writer(response)
    
    # Write the header row
    writer.writerow(['Name', 'Contact UUID', 'Community Health Unit', 'Username', 'Password',
                     'Account Category', 'Subcounty', 'County'])

    # Fetch accounts based on filters
    accounts = Accounts.objects.all()
    if county_id:
        county = get_object_or_404(County, id=county_id)
        accounts = accounts.filter(account_county=county)
    if subcounty_id:
        subcounty = get_object_or_404(Subcounty, id=subcounty_id)
        accounts = accounts.filter(account_subcounty=subcounty)

    # Write account data to CSV
    for account in accounts:
        writer.writerow([
            account.Name, 
            account.Contact_UUID, 
            account.Community_Health_Unit, 
            account.Username,
            account.Password,
            account.account_category.name, 
            account.account_subcounty.name, 
            account.account_county.name, 
        ])

    return response

def bulk_upload_accounts(request):
    if request.method == "POST":
        form = AccountUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'Invalid file format. Please upload a CSV file.')
                return redirect('bulk_upload_accounts')

            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.reader(decoded_file)
            next(reader)  # Skip header row

            success_count = 0
            error_count = 0

            for row in reader:
                try:
                    name, contact_uuid, community_health_unit, username, password, category_name, subcounty_name, county_name = row
                    
                    category, _ = Category.objects.get_or_create(name=category_name)
                    county, _ = County.objects.get_or_create(name=county_name)
                    subcounty, _ = Subcounty.objects.get_or_create(name=subcounty_name, account_county=county)

                    Accounts.objects.create(
                        Name=name,
                        Contact_UUID=contact_uuid,
                        Community_Health_Unit=community_health_unit,
                        Username=username,
                        Password=password,
                        account_category=category,
                        account_subcounty=subcounty,
                        account_county=county
                    )
                    success_count += 1
                except Exception as e:
                    print(f"Error importing row: {row} - {str(e)}")
                    error_count += 1

            messages.success(request, f'Successfully imported {success_count} accounts. Errors: {error_count}.')
            return redirect('bulk_upload_accounts')

    else:
        form = AccountUploadForm()
    
    return render(request, 'bulk_upload.html', {'form': form})

def export_subcounty_accounts_csv(request, subcounty_id):
    print(f"Subcounty ID received: {subcounty_id}")  # Debugging step

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="subcounty_{subcounty_id}_accounts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Contact UUID', 'Community Health Unit', 'Username', 'Password',
                     'Account Category', 'Subcounty', 'County'])

    try:
        accounts = Accounts.objects.filter(account_subcounty_id=subcounty_id)
        print(f"Accounts found: {accounts.count()}")  # Debugging step
    except Exception as e:
        print(f"Error: {e}")  # Debugging step
        accounts = []

    for account in accounts:
        writer.writerow([
            account.Name, 
            account.Contact_UUID, 
            account.Community_Health_Unit, 
            account.Username,
            account.Password,
            account.account_category.name, 
            account.account_subcounty.name, 
            account.account_county.name
        ])

    return response
 
def signout(request):
    logout(request)
    messages.success(request,"You have logged out")
           
    return redirect("/")
