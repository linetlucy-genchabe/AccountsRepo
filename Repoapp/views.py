from django.shortcuts import get_object_or_404, render, redirect
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.templatetags.static import static
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect
import datetime as dt
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
import csv
from django.http import JsonResponse
import json
from django.db.models import Q
from django.utils import timezone

FULL_ACCESS_ROLES = ['Admin', 'Superuser', 'MOH', 'RDHSO', 'UserManager']
EDIT_ROLES = ['Admin', 'Superuser', 'RDHSO', 'UserManager', 'CountyFocal', 'SubcountyFocal', 'WardCHA']
VIEW_ONLY_ROLES = ['CHA', 'CHEW', 'MOH']


def get_greeting():
    hour = timezone.localtime().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


@login_required(login_url='/login/')
def index(request):
    profile = request.user.profile

    # CHA and CHEW go straight to their personal home
    if profile.role in ['CHA', 'CHEW']:
        return redirect('cha_home')

    if profile.role in FULL_ACCESS_ROLES:
        accounts = Accounts.objects.all()
        counties = County.objects.all()
        countries = Countries.objects.all()
    else:
        accounts = profile.get_accessible_accounts()
        counties = profile.get_accessible_counties()
        countries = profile.allowed_countries.all()

    return render(request, 'index.html', {
        "accounts": accounts,
        "counties": counties,
        "countries": countries,
        "greeting": get_greeting(),
    })


@login_required(login_url='/login/')
def cha_home(request):
    profile = request.user.profile

    # Only CHA and CHEW use this view
    if profile.role not in ['CHA', 'CHEW']:
        return redirect('index')

    subcounties = profile.allowed_subcounties.all()
    if not subcounties.exists():
        messages.warning(request, "You have no assigned subcounty. Please contact your administrator.")
        return render(request, 'cha_home.html', {
            'greeting': get_greeting(),
            'subcounty': None,
            'accounts': [],
            'chus': [],
            'selected_chu': '',
            'search_query': '',
            'accounts_total': 0,
        })

    subcounty = subcounties.first()

    # All CHUs in this subcounty for the dropdown
    chus = Accounts.objects.filter(account_subcounty=subcounty)\
        .values_list('Community_Health_Unit', flat=True)\
        .distinct().order_by('Community_Health_Unit')

    selected_chu = request.GET.get('chu', '').strip()
    search_query = request.GET.get('q', '').strip()

    accounts = Accounts.objects.filter(account_subcounty=subcounty)
    accounts_total = accounts.count()

    if selected_chu:
        accounts = accounts.filter(Community_Health_Unit__iexact=selected_chu)
    if search_query:
        accounts = accounts.filter(
            Q(Name__icontains=search_query) |
            Q(Username__icontains=search_query)
        )

    return render(request, 'cha_home.html', {
        'greeting': get_greeting(),
        'subcounty': subcounty,
        'accounts': accounts,
        'chus': chus,
        'selected_chu': selected_chu,
        'search_query': search_query,
        'accounts_total': accounts_total,
    })


@login_required(login_url='/login/')
def dashboards(request):
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        messages.error(request, "You do not have permission to view dashboards.")
        return redirect('index')

    dashboards = Dashboards.objects.all()
    counties = County.objects.all()
    return render(request, 'dashboards.html', {"dashboards": dashboards, 'counties': counties})


@login_required(login_url='/login/')
def lmsaccounts(request):
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        messages.error(request, "You do not have permission to view LMS accounts.")
        return redirect('index')

    lmsaccounts = Lmsaccounts.objects.all()
    counties = County.objects.all()
    return render(request, 'lmsaccounts.html', {"lmsaccounts": lmsaccounts, 'counties': counties})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Welcome, you are now logged in")
            return redirect("index")
        else:
            messages.error(request, 'Username or password not correct')
            return redirect('login')

    return render(request, 'login.html')


@login_required(login_url='/login/')
def new_account(request):
    current_user = request.user
    profile = request.user.profile

    if profile.role not in EDIT_ROLES:
        messages.error(request, "You do not have permission to add accounts.")
        return redirect('index')

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

    if profile.role not in EDIT_ROLES:
        messages.error(request, "You do not have permission to add accounts.")
        return redirect('dashboards')

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

    if profile.role not in EDIT_ROLES:
        messages.error(request, "You do not have permission to add accounts.")
        return redirect('lmsaccounts')

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
def update_account(request, id):
    profile = request.user.profile

    if profile.role not in EDIT_ROLES:
        messages.error(request, "You do not have permission to edit accounts.")
        return redirect('index')

    update = Accounts.objects.get(id=id)
    if request.method == 'POST':
        form2 = AccountUpdateForm(request.POST, request.FILES, instance=update)
        if form2.is_valid():
            form2.save()
            return redirect('subcounty_detail', subcounty_id=update.account_subcounty.id)
    else:
        form2 = AccountUpdateForm(instance=update)
    return render(request, 'edit_account.html', {'form2': form2, 'account': update})


@login_required(login_url='/login/')
def update_dashboard(request, id):
    profile = request.user.profile

    if profile.role not in EDIT_ROLES:
        messages.error(request, "You do not have permission to edit accounts.")
        return redirect('dashboards')

    update = Dashboards.objects.get(id=id)
    if request.method == 'POST':
        form3 = DashboardUpdateForm(request.POST, request.FILES, instance=update)
        if form3.is_valid():
            form3.save()
            return redirect(dashboards)
    else:
        form3 = DashboardUpdateForm(instance=update)
    return render(request, 'edit_dashboard.html', {'form3': form3})


@login_required(login_url='/login/')
def update_lmsaccount(request, id):
    profile = request.user.profile

    if profile.role not in EDIT_ROLES:
        messages.error(request, "You do not have permission to edit accounts.")
        return redirect('lmsaccounts')

    update = Lmsaccounts.objects.get(id=id)
    if request.method == 'POST':
        form6 = LmsaccountUpdateForm(request.POST, request.FILES, instance=update)
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
        profile = request.user.profile

        if profile.role in FULL_ACCESS_ROLES:
            base_queryset = Accounts.objects.all()
        else:
            base_queryset = profile.get_accessible_accounts()

        searched_projects = base_queryset.filter(
            Q(Username__icontains=search_term) |
            Q(Name__icontains=search_term) |
            Q(Community_Health_Unit__icontains=search_term)
        )

        return render(request, 'search.html', {"message": search_term, "accounts": searched_projects})
    else:
        return render(request, 'search.html', {"message": "You haven't searched for any term"})


@login_required(login_url='/login/')
def search_lmsaccounts(request):
    if 'keyword' in request.GET and request.GET["keyword"]:
        search_term = request.GET.get("keyword")
        searched_projects = Lmsaccounts.search_accounts(search_term)
        message = f"{search_term}"
        return render(request, 'search.html', {"message": message, "lmsaccounts": searched_projects})
    else:
        message = "You haven't searched for any term"
        return render(request, 'search.html', {"message": message})


@login_required(login_url='/login/')
def user_profiles(request):
    current_user = request.user
    profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            current_user = current_user
            profile = form.save(commit=False)
            profile.save()
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm()

    return render(request, 'profile.html', {"form": form})


@login_required(login_url='/login/')
def county(request):
    counties = County.objects.all()
    return render(request, 'index.html', {"counties": counties})


# ─── eCHIS VIEWS ───────────────────────────────────────────────

@login_required(login_url='/login/')
def county_detail(request, county_id):
    county = get_object_or_404(County, id=county_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        accessible_counties = profile.get_accessible_counties()
        if not accessible_counties.filter(id=county_id).exists():
            messages.error(request, "You do not have permission to view this county.")
            return redirect('index')

    subcounty = county.subcounty.all()
    return render(request, 'county.html', {'county': county, 'subcounty': subcounty})


@login_required(login_url='/login/')
def subcounty_detail(request, subcounty_id):
    subcounty = get_object_or_404(Subcounty, id=subcounty_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        accessible_subcounties = profile.get_accessible_subcounties()
        if not accessible_subcounties.filter(id=subcounty_id).exists():
            messages.error(request, "You do not have permission to view this subcounty.")
            return redirect('index')

    chus = Accounts.objects.filter(account_subcounty=subcounty)\
        .values_list('Community_Health_Unit', flat=True)\
        .distinct().order_by('Community_Health_Unit')

    selected_chu = request.GET.get('chu', '').strip()
    search_query = request.GET.get('q', '').strip()

    accounts = Accounts.objects.filter(account_subcounty=subcounty)

    if selected_chu:
        accounts = accounts.filter(Community_Health_Unit__iexact=selected_chu)
    if search_query:
        accounts = accounts.filter(
            Q(Name__icontains=search_query) |
            Q(Username__icontains=search_query)
        )

    can_edit = profile.role in EDIT_ROLES

    return render(request, 'subcounty.html', {
        'subcounty': subcounty,
        'accounts': accounts,
        'chus': chus,
        'selected_chu': selected_chu,
        'search_query': search_query,
        'can_edit': can_edit,
    })


@login_required(login_url='/login/')
def country_detail(request, country_id):
    country = get_object_or_404(Countries, id=country_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        if not profile.allowed_countries.filter(id=country_id).exists():
            messages.error(request, "You do not have permission to view this country.")
            return redirect('index')

    counties = country.counties.all()
    return render(request, 'countries.html', {'country': country, 'counties': counties})


# ─── DASHBOARD VIEWS ───────────────────────────────────────────

@login_required(login_url='/login/')
def dashboard_county_detail(request, county_id):
    county = get_object_or_404(County, id=county_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        accessible_counties = profile.get_accessible_counties()
        if not accessible_counties.filter(id=county_id).exists():
            messages.error(request, "You do not have permission to view this county.")
            return redirect('index')

    subcounties = county.subcounty.all()
    return render(request, 'dashboard_county.html', {'county': county, 'subcounties': subcounties})


@login_required(login_url='/login/')
def dashboard_subcounty_detail(request, subcounty_id):
    subcounty = get_object_or_404(Subcounty, id=subcounty_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        accessible_subcounties = profile.get_accessible_subcounties()
        if not accessible_subcounties.filter(id=subcounty_id).exists():
            messages.error(request, "You do not have permission to view this subcounty.")
            return redirect('index')

    dashboard_accounts = Dashboards.objects.filter(account_subcounty=subcounty)
    return render(request, 'dashboard_subcounty.html', {
        'subcounty': subcounty,
        'dashboard_accounts': dashboard_accounts
    })


@login_required(login_url='/login/')
def dashboard_country_detail(request, country_id):
    country = get_object_or_404(Countries, id=country_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        if not profile.allowed_countries.filter(id=country_id).exists():
            messages.error(request, "You do not have permission to view this country.")
            return redirect('index')

    counties = country.counties.all()
    return render(request, 'dashboard_country.html', {'country': country, 'counties': counties})


# ─── LMS VIEWS ─────────────────────────────────────────────────

@login_required(login_url='/login/')
def lms_county_detail(request, county_id):
    county = get_object_or_404(County, id=county_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        accessible_counties = profile.get_accessible_counties()
        if not accessible_counties.filter(id=county_id).exists():
            messages.error(request, "You do not have permission to view this county.")
            return redirect('index')

    subcounties = county.subcounty.all()
    return render(request, 'lms_county.html', {'county': county, 'subcounties': subcounties})


@login_required(login_url='/login/')
def lms_subcounty_detail(request, subcounty_id):
    subcounty = get_object_or_404(Subcounty, id=subcounty_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        accessible_subcounties = profile.get_accessible_subcounties()
        if not accessible_subcounties.filter(id=subcounty_id).exists():
            messages.error(request, "You do not have permission to view this subcounty.")
            return redirect('index')

    lms_accounts = Lmsaccounts.objects.filter(account_subcounty=subcounty)
    return render(request, 'lms_subcounty.html', {
        'subcounty': subcounty,
        'lms_accounts': lms_accounts
    })


@login_required(login_url='/login/')
def lms_country_detail(request, country_id):
    country = get_object_or_404(Countries, id=country_id)
    profile = request.user.profile

    if profile.role not in FULL_ACCESS_ROLES:
        if not profile.allowed_countries.filter(id=country_id).exists():
            messages.error(request, "You do not have permission to view this country.")
            return redirect('index')

    counties = country.counties.all()
    return render(request, 'lms_country.html', {'country': country, 'counties': counties})


# ─── EDIT LOCATION VIEWS ────────────────────────────────────────

@login_required(login_url='/login/')
def update_county(request, id):
    county = get_object_or_404(County, id=id)
    if request.method == 'POST':
        form = CountyUpdateForm(request.POST, instance=county)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = CountyUpdateForm(instance=county)
    return render(request, 'edit_county.html', {'form': form})


@login_required(login_url='/login/')
def update_subcounty(request, id):
    subcounty = get_object_or_404(Subcounty, id=id)
    if request.method == 'POST':
        form = SubcountyUpdateForm(request.POST, instance=subcounty)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = SubcountyUpdateForm(instance=subcounty)
    return render(request, 'edit_subcounty.html', {'form': form})


# ─── CSV EXPORTS ────────────────────────────────────────────────

def export_accounts_csv(request):
    county_id = request.GET.get('county')
    subcounty_id = request.GET.get('subcounty')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accounts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Contact UUID', 'Area UUID', 'Community Health Unit', 'Username', 'Password',
                     'Account Category', 'Subcounty', 'County'])

    accounts = Accounts.objects.all()
    if county_id:
        county = get_object_or_404(County, id=county_id)
        accounts = accounts.filter(account_county=county)
    if subcounty_id:
        subcounty = get_object_or_404(Subcounty, id=subcounty_id)
        accounts = accounts.filter(account_subcounty=subcounty)

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
            next(reader)

            success_count = 0
            error_count = 0
            duplicate_usernames = set()
            duplicate_uuids = set()
            invalid_subcounties = set()
            invalid_counties = set()
            error_rows = []

            for i, row in enumerate(reader, start=2):
                try:
                    if not any(col.strip() for col in row):
                        continue

                    if len(row) < 9:
                        error_rows.append(f"Row {i}: only {len(row)} columns (expected 9)")
                        error_count += 1
                        continue

                    name, contact_uuid, area_uuid, community_health_unit, username, password, category_name, subcounty_name, county_name = [col.strip() for col in row[:9]]

                    contact_uuid = contact_uuid or None
                    area_uuid = area_uuid or None

                    try:
                        county = County.objects.get(name__iexact=county_name)
                    except County.DoesNotExist:
                        invalid_counties.add(county_name)
                        continue

                    try:
                        subcounty = Subcounty.objects.get(name__iexact=subcounty_name, subcounty_county=county)
                    except Subcounty.DoesNotExist:
                        invalid_subcounties.add(subcounty_name)
                        continue

                    if Accounts.objects.filter(Username=username).exists():
                        duplicate_usernames.add(username)
                        continue

                    if contact_uuid and Accounts.objects.filter(Contact_UUID=contact_uuid).exists():
                        duplicate_uuids.add(contact_uuid)
                        continue

                    if area_uuid and Accounts.objects.filter(Area_UUID=area_uuid).exists():
                        duplicate_uuids.add(area_uuid)
                        continue

                    category, _ = Category.objects.get_or_create(name=category_name)

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
                    error_rows.append(f"Row {i}: {str(e)}")
                    error_count += 1

            if invalid_subcounties:
                messages.error(request, f"Unrecognised subcounties (check spelling): {', '.join(sorted(invalid_subcounties))}")
            if invalid_counties:
                messages.error(request, f"Unrecognised counties (check spelling): {', '.join(sorted(invalid_counties))}")
            if duplicate_usernames:
                messages.warning(request, f"Skipped {len(duplicate_usernames)} duplicate username(s).")
            if duplicate_uuids:
                messages.warning(request, f"Skipped {len(duplicate_uuids)} duplicate UUID(s).")
            if error_rows:
                messages.warning(request, f"Errors on {len(error_rows)} row(s): {' | '.join(error_rows[:5])}")
            if success_count > 0:
                messages.success(request, f'Successfully imported {success_count} accounts. Skipped: {error_count}.')
            else:
                messages.error(request, "No valid accounts were imported.")

            return redirect('bulk_upload_accounts')
    else:
        form = AccountUploadForm()

    return render(request, 'bulk_upload.html', {'form': form})


def export_subcounty_accounts_csv(request, subcounty_id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="subcounty_{subcounty_id}_accounts.csv"'

    writer = csv.writer(response)
    writer.writerow(['Name', 'Contact UUID', 'Area UUID', 'Community Health Unit', 'Username', 'Password',
                     'Account Category', 'Subcounty', 'County'])

    try:
        accounts = Accounts.objects.filter(account_subcounty_id=subcounty_id)
    except Exception as e:
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
        ])

    return response


@login_required(login_url='/login/')
def export_lmsaccounts_csv(request, county_id=None):
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
        ])

    return response


def signout(request):
    logout(request)
    messages.success(request, "You have logged out")
    return redirect("/")