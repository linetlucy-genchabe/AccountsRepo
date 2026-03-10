from django.urls import re_path as url, include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.signout, name='signout'),

    url(r'^new/account$', views.new_account, name='new-account'),
    url(r'^new/dashboard$', views.new_dashboard, name='new-dashboard'),
    url(r'^new/lmsaccount$', views.new_lmsaccount, name='new-lmsaccount'),
    path('county/', views.county, name='county'),

    # ── eCHIS hierarchy ──────────────────────────────────────────
    path('country/<int:country_id>/', views.country_detail, name='country_detail'),
    path('county/<int:county_id>/', views.county_detail, name='county_detail'),
    path('subcounty/<int:subcounty_id>/', views.subcounty_detail, name='subcounty_detail'),

    # ── Dashboard hierarchy ───────────────────────────────────────
    path('dashboards/country/<int:country_id>/', views.dashboard_country_detail, name='dashboard_country_detail'),
    path('dashboards/county/<int:county_id>/', views.dashboard_county_detail, name='dashboard_county_detail'),
    path('dashboards/subcounty/<int:subcounty_id>/', views.dashboard_subcounty_detail, name='dashboard_subcounty_detail'),

    # ── LMS hierarchy ────────────────────────────────────────────
    path('lms/country/<int:country_id>/', views.lms_country_detail, name='lms_country_detail'),
    path('lms/county/<int:county_id>/', views.lms_county_detail, name='lms_county_detail'),
    path('lms/subcounty/<int:subcounty_id>/', views.lms_subcounty_detail, name='lms_subcounty_detail'),

    # ── Full account list pages ───────────────────────────────────
    path('dashboards/', views.dashboards, name='dashboards'),
    path('lmsaccounts/', views.lmsaccounts, name='lmsaccounts'),

    # ── Search ───────────────────────────────────────────────────
    url(r'^search/', views.search_accounts, name='search_results'),
    url(r'^profile/$', views.user_profiles, name='profile'),

    # ── CRUD ─────────────────────────────────────────────────────
    path('update-account/<int:id>', views.update_account, name="update-account"),
    path('update-lmsaccount/<int:id>', views.update_lmsaccount, name="update-lmsaccount"),
    path('update-dashboard/<int:id>', views.update_dashboard, name="update-dashboard"),
    path('update-county/<int:id>/', views.update_county, name='update-county'),
    path('update-subcounty/<int:id>/', views.update_subcounty, name='update-subcounty'),

    # ── Exports ──────────────────────────────────────────────────
    
    url(r'^export-accounts/', views.export_accounts_csv, name='export_accounts_csv'),
    path('export-accounts/subcounty/<int:subcounty_id>/', views.export_subcounty_accounts_csv, name='export_subcounty_accounts_csv'),
    path('export_dashboards/', views.export_dashboards_csv, name='export_dashboards_csv'),
    path('export_lmsaccounts/', views.export_lmsaccounts_csv, name='export_lmsaccounts_csv'),
    path('export_dashboards/<int:county_id>/', views.export_dashboards_csv, name='export_dashboards_csv_by_county'),
    path('export_lmsaccounts/<int:county_id>/', views.export_lmsaccounts_csv, name='export_lmsaccounts_csv_by_county'),

    # ── Bulk upload ───────────────────────────────────────────────
    path('bulk-upload/', views.bulk_upload_accounts, name='bulk_upload_accounts'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)