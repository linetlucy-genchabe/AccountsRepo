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


def dashboards(request):
    dashboards = Dashboards.objects.all()
    counties = County.objects.all()

    return render(request, 'dashboards.html', {"dashboards":dashboards, 'counties':counties})

def lmsaccounts(request):
    lmsaccounts = Lmsaccounts.objects.all()
    counties = County.objects.all()

    return render(request, 'lmsaccounts.html', {"lmsaccounts":lmsaccounts, 'counties':counties})

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
def new_dashboard(request):
    current_user = request.user
    profile = request.user.profile
   

    if request.method == 'POST':
        form = NewDashboardAccountForm(request.POST, request.FILES)
        if form.is_valid():
            dashboardaccount = form.save(commit=False)
            dashboardaccount.Author = current_user
            dashboardaccount.author_profile = profile

            dashboardaccount.save()
        return redirect('dashboards')

    else:
        form4 = NewDashboardAccountForm()
    return render(request, 'new_dashboard.html', {"form4": form4})


@login_required(login_url='/login/')
def new_lmsaccount(request):
    current_user = request.user
    profile = request.user.profile
   

    if request.method == 'POST':
        form = NewLmsaccountForm(request.POST, request.FILES)
        if form.is_valid():
            lmsaccount = form.save(commit=False)
            lmsaccount.Author = current_user
            lmsaccount.author_profile = profile

            lmsaccount.save()
        return redirect('lmsaccounts')

    else:
        form5 = NewLmsaccountForm()
    return render(request, 'new_lmsaccount.html', {"form5": form5})

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
def update_dashboard(request,id):
    
    update = Dashboards.objects.get(id=id)
    if request.method == 'POST':
        form3= DashboardUpdateForm(
            request.POST, request.FILES, instance=update)
        if form3.is_valid():
            form3.save()
            return redirect(dashboards)
    else:
        form3 = DashboardUpdateForm(instance=update)
    return render(request, 'edit_dashboard.html', {'form3': form3})


@login_required(login_url='/login/')
def update_lmsaccount(request,id):
    
    update = Lmsaccounts.objects.get(id=id)
    if request.method == 'POST':
        form6= LmsaccountUpdateForm(
            request.POST, request.FILES, instance=update)
        if form6.is_valid():
            form6.save()
            return redirect(lmsaccounts)
    else:
        form6 = LmsaccountUpdateForm(instance=update)
    return render(request, 'edit_lmsaccount.html', {'form6': form6})

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
    # accounts = subcounty.accountnames.all()  # Fetch accounts for this subcounty
    accounts = Accounts.objects.filter(account_subcounty=subcounty)
    

    
    # print("Subcounty:", subcounty)
    # print("Fetched accounts:", accounts)

    return render(request, 'subcounty.html', {'subcounty': subcounty, 'accounts': accounts})


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
            account.Area_UUID,
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
            duplicate_usernames = set()
            duplicate_uuids = set()
            invalid_subcounties = set()
            invalid_counties = set()

            for row in reader:
                try:
                    name, contact_uuid, area_uuid, community_health_unit, username, password, category_name, subcounty_name, county_name = row

                    # Check if county exists
                    try:
                        county = County.objects.get(name=county_name)
                    except County.DoesNotExist:
                        invalid_counties.add(county_name)
                        continue  # Skip this row

                    # Check if subcounty exists under the given county
                    try:
                        subcounty = Subcounty.objects.get(name=subcounty_name, subcounty_county=county)
                    except Subcounty.DoesNotExist:
                        invalid_subcounties.add(subcounty_name)
                        continue  # Skip this row

                    # Check for duplicate username or contact_uuid
                    if Accounts.objects.filter(Username=username).exists():
                        duplicate_usernames.add(username)
                        continue  # Skip this row

                    if Accounts.objects.filter(Contact_UUID=contact_uuid).exists():
                        duplicate_uuids.add(contact_uuid)
                        continue  # Skip this row

                    if Accounts.objects.filter(Area_UUID=area_uuid).exists():
                        duplicate_uuids.add(area_uuid)
                        continue  # Skip this row

                    # Get or create category
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # Create account
                    Accounts.objects.create(
                        Name=name,
                        Contact_UUID=contact_uuid,
                        Area_UUID=area_uuid,
                        Community_Health_Unit=community_health_unit,
                        Username=username,
                        Password=password,
                        account_category=category,
                        account_subcounty=subcounty,
                        account_county=county,
                        Admin=request.user
                    )
                    success_count += 1
                except Exception as e:
                    print(f"Error importing row: {row} - {str(e)}")
                    error_count += 1

            # Display error messages for invalid entries
            if invalid_subcounties:
                messages.error(request, f"Invalid subcounties: {', '.join(invalid_subcounties)}. Please correct them and try again.")
            if invalid_counties:
                messages.error(request, f"Invalid counties: {', '.join(invalid_counties)}. Please correct them and try again.")
            if duplicate_usernames:
                messages.warning(request, f"Skipped {len(duplicate_usernames)} duplicate usernames: {', '.join(duplicate_usernames)}.")
            if duplicate_uuids:
                messages.warning(request, f"Skipped {len(duplicate_uuids)} duplicate Contact UUIDs: {', '.join(duplicate_uuids)}.")

            # Show success message if any accounts were imported
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} accounts. Errors: {error_count}.')
            else:
                messages.error(request, "No valid accounts were imported. Please check errors and try again.")

            return redirect('bulk_upload_accounts')

    else:
        form = AccountUploadForm()
    
    return render(request, 'bulk_upload.html', {'form': form})

def export_subcounty_accounts_csv(request, subcounty_id):
    print(f"Subcounty ID received: {subcounty_id}")  # Debugging step

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="subcounty_{subcounty_id}_accounts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Contact UUID','Area UUID', 'Community Health Unit', 'Username', 'Password',
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
            account.Area_UUID,
            account.Community_Health_Unit, 
            account.Username,
            account.Password,
            account.account_category.name, 
            account.account_subcounty.name, 
            account.account_county.name
        ])

    return response
 
@login_required(login_url='/login/')
def export_dashboards_csv(request, county_id=None):
    """
    Exports dashboard data as a CSV file.
    If a county_id is provided, only dashboards from that county are included.
    """
    if county_id:
        try:
            county = County.objects.get(id=county_id)
            dashboards = Dashboards.objects.filter(account_county=county)
            filename = f"dashboards_{county.name}.csv"
        except County.DoesNotExist:
            return HttpResponse("County not found.", status=404)
    else:
        dashboards = Dashboards.objects.all()
        filename = "all_dashboards.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Role", "Community Health Unit", "Username", "Password", "Subcounty", "County"])

    for dashboard in dashboards:
        writer.writerow([
            dashboard.Name, 
            dashboard.Role,
            dashboard.Community_Health_Unit,
            dashboard.Username,
            dashboard.Password,
            dashboard.account_subcounty.name,
            dashboard.account_county.name,
            # dashboard.pub_date.strftime('%Y-%m-%d %H:%M')
        ])

    return response


@login_required(login_url='/login/')
def export_lmsaccounts_csv(request, county_id=None):
    """
    Exports lmsaccounts data as a CSV file.
    If a county_id is provided, only lmsaccounts from that county are included.
    """
    if county_id:
        try:
            county = County.objects.get(id=county_id)
            lmsaccounts = Lmsaccounts.objects.filter(account_county=county)
            filename = f"lmsaccounts_{county.name}.csv"
        except County.DoesNotExist:
            return HttpResponse("County not found.", status=404)
    else:
        lmsaccounts = Lmsaccounts.objects.all()
        filename = "all_lmsaccounts.csv"

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Community Health Unit", "Username", "Password", "Subcounty", "County"])

    for lmsaccount in lmsaccounts:
        writer.writerow([
            lmsaccount.Name, 
            lmsaccount.Community_Health_Unit,
            lmsaccount.Username,
            lmsaccount.Password,
            lmsaccount.account_subcounty.name,
            lmsaccount.account_county.name,
            # dashboard.pub_date.strftime('%Y-%m-%d %H:%M')
        ])

    return response


def signout(request):
    logout(request)
    messages.success(request,"You have logged out")
           
    return redirect("/")
