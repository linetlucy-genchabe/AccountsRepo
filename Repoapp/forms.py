from django import forms
from .models import *
from django.contrib.auth.models import User


class NewAccountForm(forms.ModelForm):
    class Meta:
        model = Accounts
        exclude = ['Author', 'pub_date', 'author_profile','admin_profile', ]
        widgets = {
          'account': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }

class NewLmsaccountForm(forms.ModelForm):
    class Meta:
        model = Lmsaccounts
        exclude = ['Author', 'pub_date', 'author_profile','admin_profile', ]
        widgets = {
          'account': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }

class NewDashboardAccountForm(forms.ModelForm):
    class Meta:
        model = Dashboards
        exclude = ['Author', 'pub_date', 'author_profile','admin_profile', ]
        widgets = {
          'account': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }
class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Accounts
        exclude = ['Author', 'pub_date', 'author_profile','admin_profile', ]
        widgets = {
          'account': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }

class DashboardUpdateForm(forms.ModelForm):
    class Meta:
        model = Dashboards
        exclude = ['Author', 'pub_date', 'author_profile','admin_profile', ]
        widgets = {
          'account': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }


class LmsaccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Lmsaccounts
        exclude = ['Author', 'pub_date', 'author_profile','admin_profile', ]
        widgets = {
          'account': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['user']
        widgets = {
          'bio': forms.Textarea(attrs={'rows':2, 'cols':10,}),
        }
class AccountUploadForm(forms.Form):
    file = forms.FileField(label="Upload CSV File")