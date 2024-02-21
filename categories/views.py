from django.shortcuts import render, get_object_or_404 
from categories.models import Brand
from django.urls import reverse_lazy
from django.views.generic.list import ListView 
from django.views.generic.edit import FormView 
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.forms.models import modelform_factory 
from django.apps import apps

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from .filters import ProductFilter
#from carousel.models import Marketing

###NEW HOMEPAGE
from categories import stats
from gmotorshop.settings import PRODUCTS_PER_ROW

##Search
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from categories import search
from gmotorshop import settings

from django import forms
#Authentication
import logging
from django.contrib.auth import login, authenticate 
from django.contrib import messages

from categories import forms, views

from django.core.paginator import Paginator
from django.db.models import Count
from .models import Blog, Category, Marketing, Brand
from categories import models

from django.views.generic.base import TemplateResponseMixin, View 

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Product

logger = logging.getLogger(__name__)
#api


##Basket
from django.http import HttpResponseRedirect 
from django.urls import reverse

from django.contrib.auth.mixins import (
     LoginRequiredMixin, 
     UserPassesTestMixin
)
from django import forms as django_forms
from django.db import models as django_models 
import django_filters
from django_filters.views import FilterView


#Addresses
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
)
#Addresses
class AddressListView(LoginRequiredMixin, ListView): 
    template_name = "address/address_list.html" 
    model = models.Address  

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView): 
    template_name = "address/address_form.html" 
    model = models.Address
    fields = [
        "name", 
        "telephone",
        "address1", 
        "address2", 
        "zip_code",
        "city",
        "county",
     ]
    success_url = reverse_lazy("categories:address_list")

    def form_valid(self, form):
        obj = form.save(commit=False) 
        obj.user = self.request.user 
        obj.save()
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UpdateView): 
    template_name = "address/address_update.html" 
    model = models.Address
    fields = [
        "name", 
        "telephone",
        "address1", 
        "address2", 
        "zip_code", 
        "city", 
        "county",
    ]
    success_url = reverse_lazy("categories:address_list")
    
    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressDeleteView(LoginRequiredMixin, DeleteView): 
    template_name = "address/address_confirm_delete.html" 
    model = models.Address
    success_url = reverse_lazy("categories:address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class ContactUsView(FormView): 
    template_name = "categories/contact_form.html" 
    form_class = forms.ContactForm 
    success_url = "/"

    def form_valid(self, form): 
        form.send_mail()
        return super().form_valid(form)

class LogoutView(FormView): 
    template_name = "logout.html" 

class SignupView(FormView): 
    template_name = "signup.html" 
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/") 
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form) 
        form.save()

        email = form.cleaned_data.get("email") 
        raw_password = form.cleaned_data.get("password1") 
        logger.info(
            "New signup for email=%s through SignupView", email )
        user = authenticate(email=email, password=raw_password) 
        login(self.request, user)

        form.send_mail()
    
        messages.info(
        self.request, "You signed up successfully."
)
        return response


def about_view(request):
    return render(request, 'about.html', )

class BannerView(TemplateView):
    template_name = 'courses/course/banner.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = Brand.objects.all()
        print(context['brands'])  # Check if brands are retrieved
        return context


class ProductListView(TemplateResponseMixin, View):
    model = Product
   
    queryset = Product.objects.all()
    template_name = 'courses/course/list.html' 
    
    def get(self, request, category=None):
        #product_filter = RangeFilter(request.GET)
        products = Product.published.all()
        categories = Category.objects.all()
        toprated_products = Product.published.all().filter(toprated=1)
        bestdeals_products = Product.published.all().filter(bestdeals=1)
        #featured_products = Product.objects.filter(featured=1)
        flashsales_products = Product.published.all().filter(flashsales=1)
        toppicksforyou_products = Product.published.all().filter(toppicksforyou=1)
        monthlysales_products = Product.published.all().filter(monthlysales=1)

        if category:
            category = get_object_or_404(Category, slug=category) 
            products = products.filter(category=category)
          
            paginator = Paginator(products, 4)
            page = request.GET.get('page')
            products = paginator.get_page(page)
        return self.render_to_response({
                                #'product_filter':product_filter,
                                'categories': categories, 
                                'category': category,
                                'products': products, 
                                'toprated_products': toprated_products,
                                'bestdeals_products': bestdeals_products,
                                #'featured_products': featured_products,
                                'flashsales_products':  flashsales_products,
                                'toppicksforyou_products': toppicksforyou_products,
                                'monthlysales_products': monthlysales_products
                            
                                })


class BlogListView(TemplateResponseMixin, View):
    model = Blog
   
    queryset = Blog.objects.all()
    template_name = 'courses/course/blog_list.html' 
    
    def get(self, request):
        #product_filter = RangeFilter(request.GET)
        blogs = Blog.published.all()
  

        return self.render_to_response({
                                #'product_filter':product_filter,
                         
                                'blogs': blogs, 
                          
                            
                                })


def blog_detail(request,slug):

        blog = get_object_or_404(Blog, 
                             
                                         slug=slug,
                                         status=Blog.Status.PUBLISHED,
        
                                         )
        blog_tags_ids = blog.tags.values_list('id', flat=True)
        similar_blogs = Blog.published.filter(tags__in=blog_tags_ids)\
                                  .exclude(pk=blog.pk)
        similar_blogs = similar_blogs.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:5]

        return render(request,
                  'courses/course/blog_detail.html',
                  {'blog': blog,
                   'similar_blogs': similar_blogs,
 
            
                  })

class ProductDetailView(DetailView): 
    model = Product
    
   
    template_name = 'courses/course/detail.html' 

def product_detail(request, year, month, day, slug):

        product = get_object_or_404(Product, 
                                        publish__year=year, 
                                        publish__month=month, 
                                        publish__day=day,
                                         slug=slug,
                                         status=Product.Status.PUBLISHED,
        
                                         )
        stats.log_product_view(request, product)
        view_recs = stats.recommended_from_views(request)
        search_recs = stats.recommended_from_search(request)
        recently_viewed = stats.get_recently_viewed(request)

        #bestseller_products = Product.published.all().filter(bestseller=1)
        toprated_products = Product.published.all().filter(toprated=1)

        product_tags_ids = product.tags.values_list('id', flat=True)
        similar_products = Product.published.filter(tags__in=product_tags_ids)\
                                  .exclude(pk=product.pk)
        similar_products = similar_products.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:5]
        
        return render(request,
                  'courses/course/detail.html',
                  {'product': product,
                   'view_recs': view_recs,
                   'search_recs': search_recs,
                   'recently_viewed': recently_viewed,
                    #"bestseller_products": bestseller_products,
                    "toprated_products": toprated_products,
                    'similar_products': similar_products,
                  })


def product_details(request, uuid, slug):

        product = get_object_or_404(Product, 
                                        uuid=uuid, 
                                         slug=slug,
                                         status=Product.Status.PUBLISHED,
        
                                         )
        stats.log_product_view(request, product)
        view_recs = stats.recommended_from_views(request)
        search_recs = stats.recommended_from_search(request)
        recently_viewed = stats.get_recently_viewed(request)

        #bestseller_products = Product.published.all().filter(bestseller=1)
        toprated_products = Product.published.all().filter(toprated=1)

        product_tags_ids = product.tags.values_list('id', flat=True)
        similar_products = Product.published.filter(tags__in=product_tags_ids)\
                                  .exclude(pk=product.pk)
        similar_products = similar_products.annotate(same_tags=Count('tags'))\
                                .order_by('-same_tags','-publish')[:5]
        
        return render(request,
                  'courses/course/detail.html',
                  {'product': product,
                   'view_recs': view_recs,
                   'search_recs': search_recs,
                   'recently_viewed': recently_viewed,
                    #"bestseller_products": bestseller_products,
                    "toprated_products": toprated_products,
                    'similar_products': similar_products,
                  })


def home(request, category=None):
    bestseller_products = Product.objects.filter(bestseller=1)
    bestdeals_products = Product.objects.filter(bestdeals=1)
    products = Product.objects.all()
    categories = Category.objects.all()

    if category:
        category = get_object_or_404(Category, slug=category) 
        products = products.filter(category=category)
        paginator = Paginator(bestseller_products, 3)
        page = request.GET.get('page')
        bestseller_products = paginator.get_page(page)

    return render(request, 
                'home.html',
                {'categories': categories, 
                'category': category,
                'products': products,
                'bestseller_products': bestseller_products,
                'bestdeals_products': bestdeals_products,

                }
                )


#Advertisements start
def product_bestseller(request, category=None):
    bestseller_products = Product.objects.filter(bestseller=1)
    categories = Category.objects.all()

    if category:
        paginator = Paginator(bestseller_products, 3)
        page = request.GET.get('page')
        bestseller_products = paginator.get_page(page)

    return render(request, 
                'homepage/bestsellerlist.html',
                {'categories': categories, 'bestseller_products': bestseller_products}
                )

def product_toprated(request, category=None):
    toprated_products = Product.published.all().filter(toprated=1)
    categories = Category.objects.all()
    #product_filter = RangeFilter(request.GET)

    if category:
        paginator = Paginator(toprated_products, 3)
        page = request.GET.get('page')
        toprated_products = paginator.get_page(page)

    return render(request, 
                'homepage/bestdealslist.html',
                {'categories': categories, 'toprated_products': toprated_products}
                )




def brand(request, slug=None):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brands__slug=slug)
    title = 'Items tagged with "%s"' % brand
    return render(request, 'brand.html', {'products': products,
                                             'brand':brand,
                                             'title': title
                                             })

def brand_apple(request, slug=None):
    brand = get_object_or_404(Brand, slug=slug)
    products = Product.objects.filter(brands__slug=slug)
    title = 'Items tagged with "%s"' % brand
    return render(request, 'brand.html', {'products': products,
                                             'brand':brand,
                                             'title': title
                                             })




def add_to_basket(request): 
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_uuid") 
    )
    basket = request.basket 
    if not request.basket:
        if request.user.is_authenticated: 
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user) 
        request.session["basket_id"] = basket.id
        
    basketline, created = models.BasketLine.objects.get_or_create( 
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("categories:product_detail", args=(product.publish.year, 
                             product.publish.month,
                             product.publish.day,
                             product.slug,)) 
    )

def manage_basket(request): 
    if not request.basket:
        return render(request, 'other/basket.html', {"formset": None})

    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket 
        )
        if formset.is_valid(): 
            formset.save()
    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket 
        )
    if request.basket.is_empty():
        return render(request, 'other/basket.html', {"formset": None})

    return render(request, 'other/basket.html', {"formset": formset})


class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "other/address_select.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy("categories:checkout_done")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session["basket_id"]
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data["billing_address"],
            form.cleaned_data["shipping_address"],
        )
        return super().form_valid(form)

########################
def my_order_view(request):
    user = request.user
    orders=models.Order.objects.all().filter(user = user)
    ordered_products=[]
    for order in orders:
        ordered_product=models.Product.objects.all().filter(id=order.id)
        ordered_products.append(ordered_product)

    return render(request,'my_order.html',{'data':zip(ordered_products,orders)})

def my_order_view(request):
    user = request.user
    orders = models.Order.objects.filter(user=user).order_by(
        "-date_added" 
    )
    data = []
    for order in orders:
        data.append( 
            {
                "id": order.id,
                "image": order.mobile_thumb_url, 
                "summary": order.summary, 
                "price": order.total_price,
            } 
            )
    return render(request,'my_order.html',{'data':zip(data,orders)})


class DateInput(django_forms.DateInput): 
    input_type = 'date'
class OrderFilter(django_filters.FilterSet): 
    class Meta:
        model = models.Order
        fields = {
                    'user__email': ['icontains'],
                    'status': ['exact'], 
                    'date_updated': ['gt', 'lt'], 
                    'date_added': ['gt', 'lt'],
                }
        filter_overrides = { 
            django_models.DateTimeField: {
                'filter_class': django_filters.DateFilter, 
                'extra': lambda f:{
                    'widget': DateInput}}}

class OrderView(UserPassesTestMixin, FilterView):
    template_name = 'order_filter.html'  
    filterset_class = OrderFilter
    login_url = reverse_lazy("login")

    def test_func(self):
        return self.request.user.is_staff is True

@login_required
def product_chat_room(request, id, slug):
    try:
        # retrieve course with given id joined by the current user
        p = request.user.cs_chats.get(id=id, slug=slug,) 
    except:
        # user is not a student of the course or course does not exist
        return HttpResponseForbidden()
    return render(request, 'chat/room.html', {'p': p})


def room(request, order_id): 
    return render(
        request,
        "chat_room.html", 
        {"room_name_json": str(order_id)},
)


###search

def products(request):
    # get current search phrase
    q = request.GET.get('q', '')
    # get current page number. Set to 1 is missing or invalid 
    try:
        page = int(request.GET.get('page', 1)) 
    except ValueError:
        page = 1
# retrieve the matching products
    matching = search.products(q).get('products', []) 
    # generate the pagintor object
    paginator = Paginator(matching,settings.PRODUCTS_PER_PAGE)
    try:
        results = paginator.page(page).object_list
    except (InvalidPage, EmptyPage):
        results = paginator.page(1).object_list
    # store the search
    search.store(request, q)
    # the usual...
    page_title = 'Search Results for: ' + q


    paginator = Paginator(results, 4)
    page = request.GET.get('page')
    results = paginator.get_page(page)

    return render(request, "search/results.html", {
        "results": results,
            'q': q
            })

###NEW HOMEPAGE

def index(request):
    """ site home page """
    search_recs = stats.recommended_from_search(request)
    toprated_products = Product.published.all().filter(toprated=1)
    recently_viewed = stats.get_recently_viewed(request)
    view_recs = stats.recommended_from_views(request)
    page_title = 'Gmotorshop - Home to Custom Car Chronicles'
    brands= Brand.objects.all()
    blogs = Blog.published.all()
    return render(request,
                "catalog/index.html",{
                'search_recs': search_recs,
                'toprated_products': toprated_products,
                "brands": brands,
                "blogs": blogs,
                'recently_viewed': recently_viewed,
                'view_recs': view_recs,
                'page_title': page_title,
                })