# Generated by Django 5.0.6 on 2024-06-14 20:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_alter_categories_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='permission',
            old_name='category_id',
            new_name='category',
        ),
        migrations.RenameField(
            model_name='permission',
            old_name='post_id',
            new_name='post',
        ),
    ]
