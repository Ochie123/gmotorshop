# Generated by Django 5.0.2 on 2024-02-20 20:45

import categories.models
import ckeditor_uploader.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(help_text='Type the title of your product in small letters', max_length=200, unique=True)),
                ('meta_keywords', models.CharField(help_text='Comma-delimited set of SEO keywords for meta tag', max_length=255, verbose_name='Meta Keywords')),
                ('meta_description', models.CharField(help_text='Content for description meta tag', max_length=255, verbose_name='Meta Description')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Marketing',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, default='')),
            ],
            options={
                'verbose_name': 'marketing',
                'verbose_name_plural': 'marketings',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='', max_length=255)),
                ('slug', models.SlugField(blank=True, default='')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', categories.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('telephone', models.CharField(max_length=60)),
                ('address1', models.CharField(max_length=60, verbose_name='Address line 1')),
                ('address2', models.CharField(blank=True, max_length=60, verbose_name='Address line 2')),
                ('zip_code', models.CharField(max_length=12, verbose_name='ZIP / Postal code')),
                ('city', models.CharField(max_length=60)),
                ('county', models.CharField(choices=[('na', 'Nairobi'), ('ms', 'Mombasa')], max_length=3)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(10, 'Open'), (20, 'Submitted')], default=10)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, default='')),
                ('desktop_image', models.ImageField(help_text='Upload the desktop image of size 1170\u200a×\u200a500', unique=True, upload_to='products/%Y/%m/%d')),
                ('mobile_image', models.ImageField(help_text='Upload the mobile image of size 480\u200a×\u200a400', unique=True, upload_to='products/%Y/%m/%d')),
                ('marketing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='brands', to='categories.marketing')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(10, 'New'), (20, 'Paid'), (30, 'Done')], default=10)),
                ('billing_name', models.CharField(max_length=60)),
                ('billing_address1', models.CharField(max_length=60)),
                ('billing_address2', models.CharField(blank=True, max_length=60)),
                ('billing_zip_code', models.CharField(max_length=12)),
                ('billing_city', models.CharField(max_length=60)),
                ('billing_country', models.CharField(max_length=3)),
                ('shipping_name', models.CharField(max_length=60)),
                ('shipping_address1', models.CharField(max_length=60)),
                ('shipping_address2', models.CharField(blank=True, max_length=60)),
                ('shipping_zip_code', models.CharField(max_length=12)),
                ('shipping_city', models.CharField(max_length=60)),
                ('shipping_county', models.CharField(max_length=3)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('uuid', models.UUIDField(default=None, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(help_text='Title of your product, e.g Sofa', max_length=200)),
                ('toprated', models.BooleanField(default=False, help_text='1=bestseller')),
                ('flashsales', models.BooleanField(default=False, help_text='1=flashsales')),
                ('toppicksforyou', models.BooleanField(default=False, help_text='1=Top picks for you')),
                ('monthlysales', models.BooleanField(default=False, help_text='1=monthlysales')),
                ('bestdeals', models.BooleanField(default=False, help_text='1=bestdeals')),
                ('price', models.DecimalField(decimal_places=2, help_text='Current price', max_digits=9)),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, default=0.0, help_text='Old price', max_digits=9)),
                ('quantity', models.IntegerField()),
                ('slug', models.SlugField(help_text='Type the title of your product in small letters, e.g sofa', max_length=200, unique=True)),
                ('meta_keywords', models.CharField(help_text='Comma-delimited set of SEO keywords for meta tag', max_length=255)),
                ('meta_description', models.CharField(help_text='Content for description meta tag', max_length=255)),
                ('overview', ckeditor_uploader.fields.RichTextUploadingField()),
                ('is_active', models.BooleanField(default=True)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('DF', 'Draft'), ('PB', 'Published')], default='DF', max_length=2)),
                ('categories', models.ManyToManyField(related_name='category_products', to='categories.category', verbose_name='Categories')),
                ('tags', models.ManyToManyField(blank=True, to='categories.tag')),
            ],
            options={
                'verbose_name': 'Product',
                'verbose_name_plural': 'Products',
                'ordering': ['-publish'],
            },
        ),
        migrations.CreateModel(
            name='OrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(choices=[(10, 'New'), (20, 'Processing'), (30, 'Sent'), (40, 'Cancelled')], default=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='categories.order')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='categories.product')),
            ],
        ),
        migrations.CreateModel(
            name='BasketLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('basket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.basket')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.product')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('image', models.ImageField(upload_to='product-images', verbose_name='image')),
                ('thumbnail', models.ImageField(null=True, upload_to='product-thumbnails')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.product')),
            ],
            options={
                'verbose_name': 'Image',
                'verbose_name_plural': 'Images',
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductView',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('tracking_id', models.CharField(db_index=True, max_length=255)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='categories.product')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SearchTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('q', models.CharField(max_length=200)),
                ('tracking_id', models.CharField(max_length=255)),
                ('search_date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(blank=True, default='')),
                ('image', models.ImageField(help_text='Upload the blog image', unique=True, upload_to='blogs/%Y/%m/%d')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField()),
                ('youtube_video_embed', models.TextField(blank=True, help_text='Embed YouTube video code (optional)', null=True)),
                ('publish', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('DF', 'Draft'), ('PB', 'Published')], default='DF', max_length=2)),
                ('tags', models.ManyToManyField(blank=True, to='categories.tag')),
            ],
            options={
                'verbose_name': 'blog',
                'verbose_name_plural': 'blogs',
                'ordering': ['-publish'],
            },
        ),
        migrations.AddIndex(
            model_name='product',
            index=models.Index(fields=['-publish'], name='categories__publish_07d8e2_idx'),
        ),
        migrations.AddIndex(
            model_name='blog',
            index=models.Index(fields=['-publish'], name='categories__publish_255c1b_idx'),
        ),
    ]
