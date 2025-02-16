from django.urls import  re_path as url, include,path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'$', views.index, name='index'),
    url(r'login/$',views.user_login, name='login'),
    url(r'logout/$',views.signout),
    url(r'^new/account$', views.new_account, name='new-account'),
    path('county/', views.county, name='county'),
    path('county/<int:county_id>/', views.county_detail, name='county_detail'),
    path('subcounty/<int:subcounty_id>/', views.subcounty_detail, name='subcounty_detail'),
    url(r'^search/', views.search_accounts, name='search_results'),
    url(r'^profile/$', views.user_profiles, name='profile'),
    path('update-account/<int:id>', views.update_account, name="update-account"),
    url(r'export-accounts/', views.export_accounts_csv, name='export_accounts_csv'),
    path('export-accounts/subcounty/<int:subcounty_id>/', views.export_subcounty_accounts_csv, name='export_subcounty_accounts_csv'),
    path('bulk-upload/', views.bulk_upload_accounts, name='bulk_upload_accounts'),
   
   
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)