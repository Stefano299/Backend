from django.db import migrations

def delete_seller_role(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Seller').delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0019_remove_product_seller'),
    ]

    operations = [
        migrations.RunPython(delete_seller_role, migrations.RunPython.noop),
    ]
