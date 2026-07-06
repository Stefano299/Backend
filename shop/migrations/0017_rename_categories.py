from django.db import migrations

def rename_categories(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    mapping = {
        'Processore (CPU)': 'Processore',
        'Scheda Madre (Motherboard)': 'Scheda Madre',
        'Scheda Video (GPU)': 'Scheda Video',
        'Alimentatore (PSU)': 'Alimentatore',
        'Dissipatore (Cooler)': 'Dissipatore',
        'Storage (SSD/HDD)': 'Storage',
    }
    for old_name, new_name in mapping.items():
        Category.objects.filter(name=old_name).update(name=new_name)

def reverse_rename_categories(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    mapping = {
        'Processore': 'Processore (CPU)',
        'Scheda Madre': 'Scheda Madre (Motherboard)',
        'Scheda Video': 'Scheda Video (GPU)',
        'Alimentatore': 'Alimentatore (PSU)',
        'Dissipatore': 'Dissipatore (Cooler)',
        'Storage': 'Storage (SSD/HDD)',
    }
    for old_name, new_name in mapping.items():
        Category.objects.filter(name=old_name).update(name=new_name)

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_alter_product_image'),
    ]

    operations = [
        migrations.RunPython(rename_categories, reverse_rename_categories),
    ]
