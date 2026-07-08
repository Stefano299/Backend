from django.db import migrations
from django.contrib.auth.management import create_permissions

def assign_permissions(apps, schema_editor):
    from django.apps import apps as global_apps
    app_config = global_apps.get_app_config('shop')
    create_permissions(app_config, apps=apps, verbosity=0)

    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    DiscountCode = apps.get_model('shop', 'DiscountCode')
    content_type = ContentType.objects.get_for_model(DiscountCode)
    
    try:
        manager_group = Group.objects.get(name='Store Manager')
    except Group.DoesNotExist:
        return
        
    permissions = Permission.objects.filter(content_type=content_type)
    for perm in permissions:
        manager_group.permissions.add(perm)

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0032_discountcode_order_discount_amount_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_permissions),
    ]
