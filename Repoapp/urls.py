from django.urls import  re_path as url, include,path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^$', views.index, name= 'index'),
    url(r'login/$',views.user_login, name='login'),
    url(r'logout/$',views.signout),
    url(r'^new/account$', views.new_account, name='new-account'),
    url(r'^search/', views.search_accounts, name='search_results'),
    url(r'^profile/$', views.user_profiles, name='profile'),
   
   
]

if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)