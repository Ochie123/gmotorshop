from django.contrib import admin
from django.utils.html import format_html
from django import forms
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
# Register your models here.
from categories import models 
from datetime import datetime, timedelta 
import logging
from django.contrib import admin

from django.shortcuts import get_object_or_404, render
from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import mark_safe
#from weasyprint import HTML
import tempfile

from .models import Category, Product, Tag, SearchTerm, Marketing,Brand,ProductImage,ProductView, Blog

from django.contrib.auth.admin import ( 
    UserAdmin as DjangoUserAdmin
)

from django.utils.html import format_html
from django.db.models.functions import TruncDay
from django.db.models import Avg, Count, Min, Sum 
from django.urls import path
from django.template.response import TemplateResponse

from . import models

logger = logging.getLogger(__name__)

def make_active(self, request, queryset):
    queryset.update(active=True)


make_active.short_description = "Mark selected items as active"


def make_inactive(self, request, queryset):
    queryset.update(active=False)


make_inactive.short_description = (
    "Mark selected items as inactive"
)


class TagAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {"slug": ("title",)}

class SearchTermAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','ip_address','search_date', 'user') 
    list_filter = ('ip_address', 'q', 'user', 'search_date')
    exclude = ('user',)

class ProductViewAdmin(admin.ModelAdmin):
    list_display = ['product','ip_address', 'user', 'date', 'tracking_id']
    list_filter = ['product', 'user', 'date']
    exclude = ('user',)
  
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)} 

class MarketingAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)} 

class BrandAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)} 

class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)} 

class ProductForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        label=("Categories"), 
        queryset=Category.objects.all(), 
        widget=forms.CheckboxSelectMultiple(), 
        required=True,
    )
    
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

      

def export_xlsx(modeladmin, request, queryset):
    wb = Workbook()
    ws = wb.active
    ws.title = "Products"

    number_alignment = Alignment(horizontal="right")
    wb.add_named_style(
        NamedStyle(
            "Identifier", alignment=number_alignment, number_format=FORMAT_NUMBER
        )
    )
    wb.add_named_style(
        NamedStyle("Normal Wrapped", alignment=Alignment(wrap_text=True))
    )

    class Config:
        def __init__(
            self,
            heading,
            width=None,
            heading_style="Headline 1",
            style="Normal Wrapped",
            number_format=None,
        ):
            self.heading = heading
            self.width = width
            self.heading_style = heading_style
            self.style = style
            self.number_format = number_format

    column_config = {
        "A": Config("ID", width=10, style="Identifier"),
        "B": Config("Title", width=30),
        "C": Config("Description", width=60),
        "D": Config("Price", width=15, style="Currency", number_format="#,##0.00 $"),
        "E": Config("Preview", width=100, style="Hyperlink"),
    }

    # Set up column widths, header values and styles
    for col, conf in column_config.items():
        ws.column_dimensions[col].width = conf.width

        column = ws[f"{col}1"]
        column.value = conf.heading
        column.style = conf.heading_style

    # Add products
    for obj in queryset.order_by("pk"):
        project_images = obj.productimage_set.all()[:1]
        url = ""
        if project_images:
            url = project_images[0].image.url

        data = [obj.pk, obj.title, obj.description, obj.price, url]
        ws.append(data)

        row = ws.max_row
        for row_cells in ws.iter_cols(min_row=row, max_row=row):
            for cell in row_cells:
                conf = column_config[cell.column_letter]
                cell.style = conf.style
                if conf.number_format:
                    cell.number_format = conf.number_format

    mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    charset = "utf-8"
    response = HttpResponse(
        content=save_virtual_workbook(wb),
        content_type=f"{mimetype}; charset={charset}",
        charset=charset,
    )
    response["Content-Disposition"] = "attachment; filename=products.xlsx"
    return response


export_xlsx.short_description = ("Export XLSX")


ZERO = "zero"
ONE = "one"
MANY = "many"


class ImageFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = ("images")

    # Parameter for the filter that will be used in the
    # URL query.
    parameter_name = "images"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples, akin to the values given for
        model field choices. The first element in each tuple is the
        coded value for the option that will appear in the URL
        query. The second element is the human-readable name for
        the option that will appear in the right sidebar.
        """
        return (
            (ZERO, ("Has no images")),
            (ONE, ("Has one image")),
            (MANY, ("Has more than one image")),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        qs = queryset.annotate(num_images=models.Count("productimage"))

        if self.value() == ZERO:
            qs = qs.filter(num_images=0)
        elif self.value() == ONE:
            qs = qs.filter(num_images=1)
        elif self.value() == MANY:
            qs = qs.filter(num_images__gte=2)
        return qs

class ProductImageInline(OrderedTabularInline):
    model = ProductImage
    extra = 0
    fields = ("get_image_preview", "image", "order", "move_up_down_links")
    readonly_fields = ("get_image_preview", "order", "move_up_down_links")
    ordering = ("order",)

    def get_image_preview(self, obj):
        photo_preview = render_to_string(
            "admin/products/includes/photo-preview.html",
            {"image": obj, "product": obj.product},
        )
        return mark_safe(photo_preview)

    get_image_preview.short_description = ("Preview")

@admin.register(Product)
class ProductAdmin(OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ["first_image",'publish','status', "title", "has_overview", "price"]
    list_display_links = ["first_image", "title"]
    list_editable = ["price"]
    list_filter = [ImageFilter,  'toprated', 'status', ]

    actions = [export_xlsx]

    fieldsets = ((("Product"), {"fields": ("category","tags",'toprated',"title", "slug", "overview", "price", "status")}),)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProductImageInline]

    def first_image(self, obj):
        project_images = obj.productimage_set.all()[:1]
        if project_images.count() > 0:
            image_preview = render_to_string(
                "admin/products/includes/photo-preview.html",
                {"image": project_images[0], "product": obj},
            )
            return mark_safe(image_preview)
        return ""

    first_image.short_description = ("Preview")

    def has_overview(self, obj):
        return bool(obj.overview)

    has_overview.short_overview = ("Has overview?")
    has_overview.boolean = True

   

class UserAdmin(DjangoUserAdmin): 
    fieldsets = (
        (None, {"fields": ("email", "password")}), 
        (
            "Personal info",
            {"fields": ("first_name", "last_name")
        },
        ), (
            "Permissions", 
            {
                "fields": ( 
                    "is_active",
                    "is_staff", 
                    "is_superuser",
                    "groups",
                    "user_permissions", )
            }, ),
(
                "Important dates",
                {"fields": ("last_login", "date_joined")},
), )
    add_fieldsets = ( 
        (
            None, 
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"), },
        ), )
    list_display = ( 
                "email",
                "first_name", 
                "last_name", 
                "is_staff",
)
    search_fields = ("email", "first_name", "last_name") 
    ordering = ("email",)


class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "name",
        "telephone",
        "address1",
        "address2",
        "city",
        "county",
    )
    readonly_fields = ("user",)


class BasketLineInline(admin.TabularInline):
    model = models.BasketLine
    raw_id_fields = ("product",)

class BasketAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "count")
    list_editable = ("status",)
    list_filter = ("status",)
    inlines = (BasketLineInline,)


class OrderLineInline(admin.TabularInline):
    model = models.OrderLine
    raw_id_fields = ("product",)


class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    list_filter = ("status", 'user',"shipping_county", "date_added")
    inlines = (OrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "billing_address1",
                    "billing_address2",
                    "billing_zip_code",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_county",
                )
            },
        ),
    )

# Employees need a custom version of the order views because
# they are not allowed to change products already purchased
# without adding and removing lines
class CentralOfficeOrderLineInline(admin.TabularInline):
    model = models.OrderLine
    readonly_fields = ("product",)

class CentralOfficeOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status")
    list_editable = ("status",)
    readonly_fields = ("user",)
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (None, {"fields": ("user", "status")}),
        (
            "Billing info",
            {
                "fields": (
                    "billing_name",
                    "telephone",
                    "billing_address1",
                    "billing_address2",
                    "billing_zip_code",
                    "billing_city",
                    "billing_country",
                )
            },
        ),
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )

# Dispatchers do not need to see the billing address in the fields
class DispatchersOrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "shipping_name",
        "date_added",
        "status",
    )
    list_filter = ("status", "shipping_country", "date_added")
    inlines = (CentralOfficeOrderLineInline,)
    fieldsets = (
        (
            "Shipping info",
            {
                "fields": (
                    "shipping_name",
                    "shipping_address1",
                    "shipping_address2",
                    "shipping_zip_code",
                    "shipping_city",
                    "shipping_country",
                )
            },
        ),
    )
# Dispatchers are only allowed to see orders that 
# # are ready to be shipped
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=models.Order.PAID)

# The class below will pass to the Django Admin templates a couple 
# # of extra values that represent colors of headings

class ColoredAdminSite(admin.sites.AdminSite):
    def each_context(self, request):
        context = super().each_context(request)
        context["site_header_color"] = getattr(
            self, "site_header_color", None
        )
        context["module_caption_color"] = getattr(
            self, "module_caption_color", None
        )
        return context

# The following will add reporting views to the list of
# available urls and will list them from the index page
class PeriodSelectForm(forms.Form):
    PERIODS = ((30, "30 days"), (60, "60 days"), (90, "90 days"))
    period = forms.TypedChoiceField(
        choices=PERIODS, coerce=int, required=True
    )


class ReportingColoredAdminSite(ColoredAdminSite):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "orders_per_day/",
                self.admin_view(self.orders_per_day),
            ),

            path(
                "productviews_per_day/",
                self.admin_view(self.productviews_per_day),
            ),

            path(
                "most_bought_products/",
                self.admin_view(self.most_bought_products),
                name="most_bought_products",
            ),

            path(
                "most_searched_terms/",
                self.admin_view(self.most_searched_terms),
                name="most_searched_terms",
            ),
            path(
                "most_viewed_products/",
                self.admin_view(self.most_viewed_products),
                name="most_viewed_products",
            ),
        ]
        return my_urls + urls


    def orders_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        order_data = (
            models.Order.objects.filter(
                date_added__gt=starting_day
            )
            .annotate(day=TruncDay("date_added"))
            .values("day")
            .annotate(c=Count("id"))
        )
        logger.info("orders_per_day query: %s", order_data.query)
        labels = [
            x["day"].strftime("%Y-%m-%d") for x in order_data
        ]
        values = [x["c"] for x in order_data]

        context = dict(
            self.each_context(request),
            title="Orders per day",
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "orders_per_day.html", context
        )


    def productviews_per_day(self, request):
        starting_day = datetime.now() - timedelta(days=180)
        productview_data = (
            models.ProductView.objects.filter(
                date__gt=starting_day
            )
            .annotate(day=TruncDay("date"))
            .values("day")
            .annotate(c=Count("id"))
        )
        logger.info("productviews_per_day query: %s", productview_data.query)
        labels = [
            x["day"].strftime("%Y-%m-%d") for x in productview_data
        ]
        values = [x["c"] for x in productview_data]

        context = dict(
            self.each_context(request),
            title="Product views per day",
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "productviews_per_day.html", context
        )

    def most_viewed_products(self, request):
        if request.method == "POST":
            form = PeriodSelectForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(
                    days=days
                )
                data = (
                    models.ProductView.objects.filter(
                        date__gt=starting_day
                    )
                    .values("product__title")
                    .annotate(c=Count("id"))
                )
                logger.info(
                    "most_viewed_products query: %s", data.query
                )
                labels = [x["product__title"] for x in data]
                values = [x["c"] for x in data]
        else:
            form = PeriodSelectForm()
            labels = None
            values = None

        context = dict(
            self.each_context(request),
            title="Most viewed products",
            form=form,
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "most_viewed_products.html", context
        )

    def most_searched_terms(self, request):
        if request.method == "POST":
            form = PeriodSelectForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(
                    days=days
                )
                data = (
                    models.SearchTerm.objects.filter(
                        search_date__gt=starting_day
                    )
                    .values("q")
                    .annotate(c=Count("id"))
                )
                logger.info(
                    "most_viewed_products query: %s", data.query
                )
                labels = [x["q"] for x in data]
                values = [x["c"] for x in data]
        else:
            form = PeriodSelectForm()
            labels = None
            values = None

        context = dict(
            self.each_context(request),
            title="Most searched terms",
            form=form,
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "most_searched_terms.html", context
        )

    def most_bought_products(self, request):
        if request.method == "POST":
            form = PeriodSelectForm(request.POST)
            if form.is_valid():
                days = form.cleaned_data["period"]
                starting_day = datetime.now() - timedelta(
                    days=days
                )
                data = (
                    models.OrderLine.objects.filter(
                        order__date_added__gt=starting_day
                    )
                    .values("product__title")
                    .annotate(c=Count("id"))
                )
                logger.info(
                    "most_bought_products query: %s", data.query
                )
                labels = [x["product__title"] for x in data]
                values = [x["c"] for x in data]
        else:
            form = PeriodSelectForm()
            labels = None
            values = None

        context = dict(
            self.each_context(request),
            title="Most bought products",
            form=form,
            labels=labels,
            values=values,
        )
        return TemplateResponse(
            request, "most_bought_products.html", context
        )

    def index(self, request, extra_context=None):
        reporting_pages = [
            {
                "name": "Orders per day",
                "link": "orders_per_day/",
            },
            {
                "name": "Product views per day",
                "link": "productviews_per_day/",
            },

            {
                "name": "Most viewed products",
                "link": "most_viewed_products/",
            },
            {
                "name": "Most searched terms",
                "link": "most_searched_terms/",
            },
            {
                "name": "Most bought products",
                "link": "most_bought_products/",
            },
        ]
        if not extra_context:
            extra_context = {}
        extra_context = {"reporting_pages": reporting_pages}
        return super().index(request, extra_context)

# Finally we define 3 instances of AdminSite, each with their own 
# # set of required permissions and colors

class InvoiceMixin:
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                "invoice/<int:order_id>/",
                self.admin_view(self.invoice_for_order),
                name="invoice",
            )
        ]
        return my_urls + urls

    def invoice_for_order(self, request, order_id):
        order = get_object_or_404(models.Order, pk=order_id)

        if request.GET.get("format") == "pdf":
            html_string = render_to_string(
                "invoice.html", {"order": order}
            )
            html = HTML(
                string=html_string,
                base_url=request.build_absolute_uri(),
            )

            result = html.write_pdf()

            response = HttpResponse(
                content_type="application/pdf"
            )
            response[
                "Content-Disposition"
            ] = "inline; filename=invoice.pdf"
            response["Content-Transfer-Encoding"] = "binary"
            with tempfile.NamedTemporaryFile(
                delete=True
            ) as output:
                output.write(result)
                output.flush()
                output = open(output.name, "rb")
                binary_pdf = output.read()
                response.write(binary_pdf)

            return response

        return render(request, "invoice.html", {"order": order})

# This mixin will be used for the invoice functionality, which is 
# # only available to owners and employees, but not dispatchers

class OwnersAdminSite(InvoiceMixin, ReportingColoredAdminSite):
    site_header = "Mackenya owners administration"
    site_header_color = "black"
    module_caption_color = "grey"

    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_superuser
        )

class CentralOfficeAdminSite(
    InvoiceMixin,
     ReportingColoredAdminSite
):
    site_header = "Mackenya central office administration"
    site_header_color = "purple"
    module_caption_color = "pink"

    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_employee
        )


class DispatchersAdminSite(ColoredAdminSite):
    site_header = "Mackenya central dispatch administration"
    site_header_color = "green"
    module_caption_color = "lightgreen"

    def has_permission(self, request):
        return (
            request.user.is_active and request.user.is_dispatcher
        )

categories_admin = OwnersAdminSite()
categories_admin.register(models.SearchTerm, SearchTermAdmin)
categories_admin.register(models.ProductView, ProductViewAdmin)
categories_admin.register(models.Product, ProductAdmin)
categories_admin.register(models.Tag, TagAdmin)
categories_admin.register(models.Brand, BrandAdmin)
categories_admin.register(models.Blog, BlogAdmin)
categories_admin.register(models.Marketing, MarketingAdmin)
categories_admin.register(models.Category, CategoryAdmin)
#categories_admin.register(models.ProductImage, ProductImageAdmin)
categories_admin.register(models.User, UserAdmin)
categories_admin.register(models.Address, AddressAdmin)
categories_admin.register(models.Basket, BasketAdmin)
categories_admin.register(models.Order, OrderAdmin)

