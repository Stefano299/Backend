from django.db import migrations

def add_case_category_and_products(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Product = apps.get_model('shop', 'Product')
    
    # Crea la categoria "Case"
    case_category, _ = Category.objects.get_or_create(name="Case")
    
    # Crea prodotti di tipo "Case"
    cases_data = [
        {
            "name": "Corsair 4000D Airflow Black",
            "description": "Case mid-tower ATX ad elevato flusso d'aria con pannello frontale ottimizzato per la ventilazione, due ventole da 120 mm incluse e sistema di gestione dei cavi RapidRoute.",
            "price": 99.90,
            "stock": 15,
        },
        {
            "name": "NZXT H9 Flow All White",
            "description": "Case mid-tower a doppia camera con vista panoramica in vetro temperato, predisposto per un flusso d'aria eccezionale con 4 ventole da 120 mm incluse.",
            "price": 169.90,
            "stock": 8,
        },
        {
            "name": "Lian Li O11 Dynamic EVO",
            "description": "Case mid-tower modulare di fascia alta con pannelli in vetro temperato, progettato per configurazioni personalizzate ed estremo raffreddamento.",
            "price": 189.90,
            "stock": 10,
        }
    ]
    
    for c_data in cases_data:
        p = Product.objects.create(**c_data)
        p.categories.add(case_category)

def remove_case_category_and_products(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Product = apps.get_model('shop', 'Product')
    
    # Trova la categoria Case
    case_category = Category.objects.filter(name="Case").first()
    if case_category:
        # Elimina i prodotti associati a questa categoria
        Product.objects.filter(categories=case_category).delete()
        case_category.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0013_review'),
    ]

    operations = [
        migrations.RunPython(add_case_category_and_products, remove_case_category_and_products),
    ]
