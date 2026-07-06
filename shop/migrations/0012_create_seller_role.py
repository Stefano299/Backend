from django.db import migrations

def create_seller_role(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    
    product_ct, _ = ContentType.objects.get_or_create(app_label='shop', model='product')
    
    permissions_to_assign = [
        ('add_product', 'Can add product'),
        ('change_product', 'Can change product'),
        ('delete_product', 'Can delete product'),
        ('view_product', 'Can view product'),
    ]
    
    seller_group, _ = Group.objects.get_or_create(name='Seller')
    
    for codename, name in permissions_to_assign:
        perm, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=product_ct,
            defaults={'name': name}
        )
        seller_group.permissions.add(perm)

def remove_seller_role(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Seller').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_product_seller'),
        ('auth', '__latest__'),
        ('contenttypes', '__latest__'),
    ]

    operations = [
        migrations.RunPython(create_seller_role, remove_seller_role),
    ]
