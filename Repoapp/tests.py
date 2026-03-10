
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import (
    Category, Countries, County, Subcounty,
    Profile, Accounts, Dashboards, Lmsaccounts
)


# ── Helpers ────────────────────────────────────────────────────────────────

def create_base_data():
    """Creates and returns common test fixtures."""
    country = Countries.objects.create(name='Kenya', code='KE')
    county = County.objects.create(name='Nairobi', county_country=country)
    subcounty = Subcounty.objects.create(name='Westlands', subcounty_county=county)
    county2 = County.objects.create(name='Mombasa', county_country=country)
    subcounty2 = Subcounty.objects.create(name='Nyali', subcounty_county=county2)
    category = Category.objects.create(name='CHW')
    return country, county, subcounty, county2, subcounty2, category


def create_user(username='testuser', password='testpass123', role='RDHSO'):
    user = User.objects.create_user(username=username, password=password)
    profile = Profile.objects.get(user=user)
    profile.role = role
    profile.save()
    return user


def create_account(name, username, subcounty, county, category, admin):
    return Accounts.objects.create(
        Name=name,
        Contact_UUID=f'uuid-{username}',
        Area_UUID=f'area-{username}',
        Community_Health_Unit=f'{name} CHU',
        Username=username,
        Password='pass123',
        account_category=category,
        account_subcounty=subcounty,
        account_county=county,
        Admin=admin,
    )


# ── Model Tests ────────────────────────────────────────────────────────────

class CountryModelTest(TestCase):
    def test_country_creation(self):
        country = Countries.objects.create(name='Kenya', code='KE')
        self.assertEqual(str(country), 'Kenya')

    def test_country_unique_name(self):
        Countries.objects.create(name='Kenya', code='KE')
        with self.assertRaises(Exception):
            Countries.objects.create(name='Kenya', code='KE2')


class CountyModelTest(TestCase):
    def setUp(self):
        self.country = Countries.objects.create(name='Kenya', code='KE')

    def test_county_creation(self):
        county = County.objects.create(name='Nairobi', county_country=self.country)
        self.assertEqual(str(county), 'Nairobi')

    def test_county_belongs_to_country(self):
        county = County.objects.create(name='Nairobi', county_country=self.country)
        self.assertEqual(county.county_country, self.country)


class SubcountyModelTest(TestCase):
    def setUp(self):
        country = Countries.objects.create(name='Kenya', code='KE')
        self.county = County.objects.create(name='Nairobi', county_country=country)

    def test_subcounty_creation(self):
        sub = Subcounty.objects.create(name='Westlands', subcounty_county=self.county)
        self.assertEqual(str(sub), 'Westlands')

    def test_subcounty_belongs_to_county(self):
        sub = Subcounty.objects.create(name='Westlands', subcounty_county=self.county)
        self.assertEqual(sub.subcounty_county, self.county)


class ProfileModelTest(TestCase):
    def setUp(self):
        self.country, self.county, self.subcounty, self.county2, self.subcounty2, self.category = create_base_data()
        self.admin = create_user('admin', role='Admin')

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(username='newuser', password='pass')
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_country_access_gives_all_counties(self):
        user = create_user('countryuser')
        profile = user.profile
        profile.allowed_countries.add(self.country)
        counties = profile.get_accessible_counties()
        self.assertIn(self.county, counties)
        self.assertIn(self.county2, counties)

    def test_county_access_gives_subcounties(self):
        user = create_user('countyuser')
        profile = user.profile
        profile.allowed_counties.add(self.county)
        subcounties = profile.get_accessible_subcounties()
        self.assertIn(self.subcounty, subcounties)
        self.assertNotIn(self.subcounty2, subcounties)

    def test_subcounty_access_is_restricted(self):
        user = create_user('subuser')
        profile = user.profile
        profile.allowed_subcounties.add(self.subcounty)
        subcounties = profile.get_accessible_subcounties()
        self.assertIn(self.subcounty, subcounties)
        self.assertNotIn(self.subcounty2, subcounties)

    def test_subcounty_only_access_restricts_accounts(self):
        account1 = create_account('Alice', 'alice', self.subcounty, self.county, self.category, self.admin)
        account2 = create_account('Bob', 'bob', self.subcounty2, self.county2, self.category, self.admin)

        user = create_user('subonlyuser')
        profile = user.profile
        profile.allowed_subcounties.add(self.subcounty)

        accounts = profile.get_accessible_accounts()
        self.assertIn(account1, accounts)
        self.assertNotIn(account2, accounts)

    def test_county_access_shows_all_subcounty_accounts(self):
        account1 = create_account('Alice', 'alice', self.subcounty, self.county, self.category, self.admin)
        account2 = create_account('Bob', 'bob', self.subcounty2, self.county2, self.category, self.admin)

        user = create_user('countyonlyuser')
        profile = user.profile
        profile.allowed_counties.add(self.county)

        accounts = profile.get_accessible_accounts()
        self.assertIn(account1, accounts)
        self.assertNotIn(account2, accounts)


class AccountsModelTest(TestCase):
    def setUp(self):
        self.country, self.county, self.subcounty, _, _, self.category = create_base_data()
        self.admin = create_user('admin', role='Admin')

    def test_account_creation(self):
        account = create_account('Jane Doe', 'janedoe', self.subcounty, self.county, self.category, self.admin)
        self.assertEqual(str(account), 'Jane Doe')

    def test_search_by_username(self):
        create_account('Jane Doe', 'janedoe', self.subcounty, self.county, self.category, self.admin)
        results = Accounts.search_accounts('janedoe')
        self.assertEqual(results.count(), 1)

    def test_search_by_name(self):
        create_account('Jane Doe', 'janedoe', self.subcounty, self.county, self.category, self.admin)
        results = Accounts.search_accounts('Jane')
        self.assertEqual(results.count(), 1)

    def test_search_returns_empty_for_no_match(self):
        create_account('Jane Doe', 'janedoe', self.subcounty, self.county, self.category, self.admin)
        results = Accounts.search_accounts('xxxxxx')
        self.assertEqual(results.count(), 0)


# ── View Tests ─────────────────────────────────────────────────────────────

class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = create_user('testuser', 'testpass123')

    def test_login_page_loads(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, '/')

    def test_login_with_invalid_credentials(self):
        response = self.client.post('/login/', {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 302)

    def test_logout_redirects(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/logout/')
        self.assertRedirects(response, '/')


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country, self.county, self.subcounty, _, _, _ = create_base_data()
        self.user = create_user('testuser', 'testpass123', role='RDHSO')
        self.user.profile.allowed_countries.add(self.country)

    def test_index_redirects_if_not_logged_in(self):
        response = self.client.get('/')
        self.assertRedirects(response, '/login/?next=/')

    def test_index_loads_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_index_contains_allowed_counties(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/')
        self.assertIn(self.county, response.context['counties'])


class CountyDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country, self.county, self.subcounty, self.county2, _, _ = create_base_data()

    def test_county_detail_requires_login(self):
        response = self.client.get(f'/county/{self.county.id}/')
        self.assertEqual(response.status_code, 302)

    def test_full_access_role_can_view_any_county(self):
        user = create_user('rdhso', role='RDHSO')
        self.client.login(username='rdhso', password='testpass123')
        response = self.client.get(f'/county/{self.county.id}/')
        self.assertEqual(response.status_code, 200)

    def test_restricted_user_cannot_view_unallowed_county(self):
        user = create_user('restricted', role='County Officer')
        user.profile.allowed_counties.add(self.county)
        self.client.login(username='restricted', password='testpass123')
        response = self.client.get(f'/county/{self.county2.id}/')
        self.assertRedirects(response, '/')

    def test_restricted_user_can_view_allowed_county(self):
        user = create_user('restricted', role='County Officer')
        user.profile.allowed_counties.add(self.county)
        self.client.login(username='restricted', password='testpass123')
        response = self.client.get(f'/county/{self.county.id}/')
        self.assertEqual(response.status_code, 200)


class SubcountyDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country, self.county, self.subcounty, _, self.subcounty2, _ = create_base_data()

    def test_subcounty_detail_requires_login(self):
        response = self.client.get(f'/subcounty/{self.subcounty.id}/')
        self.assertEqual(response.status_code, 302)

    def test_restricted_user_cannot_view_unallowed_subcounty(self):
        user = create_user('restricted', role='Subcounty Officer')
        user.profile.allowed_subcounties.add(self.subcounty)
        self.client.login(username='restricted', password='testpass123')
        response = self.client.get(f'/subcounty/{self.subcounty2.id}/')
        self.assertRedirects(response, '/')

    def test_restricted_user_can_view_allowed_subcounty(self):
        user = create_user('restricted', role='Subcounty Officer')
        user.profile.allowed_subcounties.add(self.subcounty)
        self.client.login(username='restricted', password='testpass123')
        response = self.client.get(f'/subcounty/{self.subcounty.id}/')
        self.assertEqual(response.status_code, 200)


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country, self.county, self.subcounty, self.county2, self.subcounty2, self.category = create_base_data()
        self.admin = create_user('admin', role='Admin')
        self.account1 = create_account('Alice Wanjiru', 'alicew', self.subcounty, self.county, self.category, self.admin)
        self.account2 = create_account('Bob Otieno', 'bobotieno', self.subcounty2, self.county2, self.category, self.admin)

    def test_search_requires_login(self):
        response = self.client.get('/search/?keyword=alice')
        self.assertEqual(response.status_code, 302)

    def test_full_access_user_can_search_all(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/search/?keyword=alice')
        self.assertIn(self.account1, response.context['accounts'])

    def test_restricted_user_cannot_search_outside_access(self):
        user = create_user('restricted', role='Subcounty Officer')
        user.profile.allowed_subcounties.add(self.subcounty)
        self.client.login(username='restricted', password='testpass123')
        response = self.client.get('/search/?keyword=bob')
        self.assertNotIn(self.account2, response.context['accounts'])

    def test_restricted_user_can_search_within_access(self):
        user = create_user('restricted', role='Subcounty Officer')
        user.profile.allowed_subcounties.add(self.subcounty)
        self.client.login(username='restricted', password='testpass123')
        response = self.client.get('/search/?keyword=alice')
        self.assertIn(self.account1, response.context['accounts'])

    def test_empty_search_term(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/search/?keyword=')
        self.assertIn('message', response.context)


class BulkUploadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country, self.county, self.subcounty, _, _, self.category = create_base_data()

    def test_bulk_upload_requires_login(self):
        response = self.client.get('/bulk-upload/')
        self.assertEqual(response.status_code, 302)

    def test_bulk_upload_page_loads(self):
        user = create_user('admin', role='Admin')
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/bulk-upload/')
        self.assertEqual(response.status_code, 200)


class ExportViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.country, self.county, self.subcounty, _, _, self.category = create_base_data()
        self.admin = create_user('admin', role='Admin')
        create_account('Alice', 'alice', self.subcounty, self.county, self.category, self.admin)

    def test_export_accounts_csv_requires_login(self):
        response = self.client.get('/export-accounts/')
        self.assertEqual(response.status_code, 302)

    def test_export_accounts_csv_returns_csv(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get('/export-accounts/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')

    def test_export_subcounty_accounts_csv(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(f'/export-accounts/subcounty/{self.subcounty.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
