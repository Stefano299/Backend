from django.db import migrations
from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions

def assign_additional_permissions(apps, schema_editor):
    for app_config in global_apps.get_app_configs():
        create_permissions(app_config, verbosity=0)
        
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')
    
    order_ct, _ = ContentType.objects.get_or_create(app_label='shop', model='order')
    review_ct, _ = ContentType.objects.get_or_create(app_label='shop', model='review')
    
    permissions_to_add = [
        ('change_order', order_ct),
        ('delete_order', order_ct),
        ('view_order', order_ct),
        ('delete_review', review_ct),
    ]
    
    for codename, ct in permissions_to_add:
        perm = Permission.objects.filter(codename=codename, content_type=ct).first()
        if perm:
            manager_group.permissions.add(perm)

def rollback_additional_permissions(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0020_delete_seller_group'),
    ]

    operations = [
        migrations.RunPython(assign_additional_permissions, rollback_additional_permissions),
    ]
