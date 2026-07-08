from django.db import migrations
from django.contrib.auth.management import create_permissions

def create_roles_and_permissions(apps, schema_editor):
    # Force creation of permissions for catalog models
    app_config = apps.get_app_config('catalog')
    app_config.models_module = True
    create_permissions(app_config, apps=apps, verbosity=0)
    
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')
    
    # Assign permissions for catalog models (add, change, delete, view for Product, Category, Review)
    catalog_permissions = Permission.objects.filter(content_type__app_label='catalog')
    manager_group.permissions.add(*catalog_permissions)

def remove_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Store Manager').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_populate_pc_components'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ]
