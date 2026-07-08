from django.db import migrations
from django.contrib.auth.management import create_permissions

def assign_orders_permissions(apps, schema_editor):
    # Force creation of permissions for orders models
    app_config = apps.get_app_config('orders')
    app_config.models_module = True
    create_permissions(app_config, apps=apps, verbosity=0)
    
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')
    
    # Assign permissions for orders models
    orders_permissions = Permission.objects.filter(content_type__app_label='orders')
    manager_group.permissions.add(*orders_permissions)

def remove_orders_permissions(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(assign_orders_permissions, remove_orders_permissions),
    ]
