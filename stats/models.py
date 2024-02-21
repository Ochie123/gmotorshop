from django.conf import settings
from django.db import models

# Create your models here.
from django.contrib.auth.models import  AbstractBaseUser
from categories.models import Product

class PageView(models.Model): 
    ##model class for tracking the pages that a customer views """
    class Meta:
        abstract = True
    
    date = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=255, default='')
    
class ProductView(PageView):
    ##""" tracks product pages that customer views """
    product = models.ForeignKey(Product, on_delete=models.CASCADE )
    