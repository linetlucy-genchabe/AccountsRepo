from django.db import models
import datetime as dt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404


# Create your models here.
   
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    
    def __str__(self):
        return self.name


    def save_category(self):
        self.save()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    

    def save_profile(self):
        self.save()
        
        

    def delete_profile(self):
        self.delete()

    def __str__(self):
        return str(self.user)
    
    # def __str__(self):
    #     return f"{self.user}, {self.bio}, {self.photo}"
    
    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

class County(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    
    def __str__(self):
        return self.name


    def save_county(self):
        self.save()

class Subcounty(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    
    def __str__(self):
        return self.name


    def save_subcounty(self):
        self.save()

        
class Accounts(models.Model):
    Name = models.CharField(max_length=255)
    Contact_UUID = models.CharField(max_length=1000)
    Community_Health_Unit = models.CharField(max_length=255)
    Username = models.CharField(max_length=255)
    Password = models.CharField(max_length=255)
    account_category = models.ForeignKey(Category, on_delete=models.CASCADE)
    account_subcounty = models.ForeignKey(Subcounty, on_delete=models.CASCADE)
    account_county = models.ForeignKey(County, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now_add=True)
    Admin = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    admin_profile = models.ForeignKey(Profile,on_delete=models.CASCADE, blank=True, default='1')
    
    
    def save_accounts(self):
        self.save()
    
    def delete_accounts(self):
        self.delete()
        
    @classmethod
    def get_allaccounts(cls):
        accounts = cls.objects.all()
        return accounts
    
    @classmethod
    def search_accounts(cls, search_term):
        accounts = cls.objects.filter(Username__icontains=search_term)| cls.objects.filter(Name__icontains=search_term)

        
        return accounts
    
    @classmethod
    def get_by_Category(cls, categories):
        accounts = cls.objects.filter(category__name__icontains=categories)
        return accounts
    
    @classmethod
    def get_by_County(cls, counties):
        accounts = cls.objects.filter(category__name__icontains=counties)
        return accounts
    
    @classmethod
    def get_by_Subcounty(cls, subcounties):
        accounts = cls.objects.filter(category__name__icontains=subcounties)
        return accounts
    
    @classmethod
    def get_accounts(request, id):
        try:
            account = Accounts.objects.get(pk = id)
            
        except ObjectDoesNotExist:
            raise Http404()
        
        return account
    
    def update_accounts(self):
        self.update_accounts()
    
    def __str__(self):
        return self.Name
    
    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'My Accounts'
        verbose_name_plural = 'Accounts'
