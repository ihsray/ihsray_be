# Generated by Django 5.1.2 on 2025-02-28 06:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_admin_product_images_alter_banner_image_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="admin",
            old_name="admin_name",
            new_name="username",
        ),
    ]
