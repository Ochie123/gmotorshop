# Generated by Django 5.0.2 on 2024-02-21 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0004_remove_product_categories_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='toprated',
            field=models.BooleanField(default=False, help_text='1=toprated'),
        ),
    ]
