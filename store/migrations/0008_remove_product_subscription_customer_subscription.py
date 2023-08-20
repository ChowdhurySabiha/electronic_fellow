# Generated by Django 4.2.2 on 2023-08-18 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_subscriptionplan_product_subscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='subscription',
        ),
        migrations.AddField(
            model_name='customer',
            name='subscription',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.subscriptionplan'),
        ),
    ]