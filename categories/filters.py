import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
  age = django_filters.AllValuesFilter()

  class Meta:
      model = Product
      fields = ['price']