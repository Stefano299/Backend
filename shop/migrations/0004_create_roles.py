from django.db import migrations

def create_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    product_ct, _ = ContentType.objects.get_or_create(app_label='shop', model='product')
    category_ct, _ = ContentType.objects.get_or_create(app_label='shop', model='category')
    
    permissions_to_create = [
        ('add_product', 'Can add product', product_ct),
        ('change_product', 'Can change product', product_ct),
        ('delete_product', 'Can delete product', product_ct),
        ('view_product', 'Can view product', product_ct),
        ('add_category', 'Can add category', category_ct),
        ('change_category', 'Can change category', category_ct),
        ('delete_category', 'Can delete category', category_ct),
        ('view_category', 'Can view category', category_ct),
    ]
    
    Group.objects.get_or_create(name='Customer')
    
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')
    
    for codename, name, ct in permissions_to_create:
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=ct,
            defaults={'name': name}
        )
        manager_group.permissions.add(perm)

def remove_roles_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['Customer', 'Store Manager']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_category_product_categories'),
        ('auth', '__latest__'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(create_roles_and_permissions, remove_roles_and_permissions),
    ]
