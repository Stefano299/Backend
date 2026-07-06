from django.db import migrations

def populate_pc_components(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Product = apps.get_model('shop', 'Product')

    # Clean existing categories and products (since we are pivoting the store)
    Product.objects.all().delete()
    Category.objects.all().delete()

    # Define new categories
    categories_data = [
        "Processore",
        "Scheda Madre",
        "Memoria RAM",
        "Scheda Video",
        "Alimentatore",
        "Dissipatore",
        "Storage"
    ]

    categories = {}
    for cat_name in categories_data:
        categories[cat_name], _ = Category.objects.get_or_create(name=cat_name)

    # Define some realistic PC components to showcase the catalog
    products_data = [
        # Processore (CPU)
        {
            "name": "AMD Ryzen 7 7800X3D",
            "description": "Il miglior processore per il gaming. 8 Core, 16 Thread, Cache 3D V-Cache, socket AM5, frequenza fino a 5.0 GHz. Ideale per e-sport e gaming competitivo ad alti framerate.",
            "price": 419.99,
            "stock": 15,
            "category": "Processore"
        },
        {
            "name": "Intel Core i7-14700K",
            "description": "Processore Intel Core di 14a generazione LGA1700. 20 core (8 Performance-core e 12 Efficient-core), frequenza fino a 5.6 GHz sbloccata per l'overclock. Prestazioni mostruose in gaming e produttività.",
            "price": 439.50,
            "stock": 10,
            "category": "Processore"
        },
        # Scheda Madre (Motherboard)
        {
            "name": "MSI MAG B650 Tomahawk WiFi",
            "description": "Scheda madre ATX per socket AMD AM5. Supporta memorie DDR5, PCIe 4.0, dotata di un robusto sistema di alimentazione a 14+2+1 fasi, Wi-Fi 6E e dissipatori M.2 integrati.",
            "price": 219.99,
            "stock": 12,
            "category": "Scheda Madre"
        },
        {
            "name": "ASUS ROG Strix Z790-F Gaming WiFi II",
            "description": "Scheda madre Intel LGA1700 premium. DDR5, PCIe 5.0, WiFi 7 integrato, fasi di alimentazione avanzate 16+1+2 e ampi dissipatori termici. Il top per processori Intel K-Series.",
            "price": 359.00,
            "stock": 8,
            "category": "Scheda Madre"
        },
        # Memoria RAM
        {
            "name": "Corsair Vengeance RGB DDR5 32GB (2x16GB) 6000MHz CL30",
            "description": "Kit di memorie RAM DDR5 ad alte prestazioni ottimizzato per AMD EXPO e Intel XMP. Latenza bassissima CL30 e illuminazione RGB dinamica a dieci zone indirizzabili.",
            "price": 134.99,
            "stock": 25,
            "category": "Memoria RAM"
        },
        {
            "name": "G.Skill Trident Z5 Neo RGB 32GB DDR5 6400MHz CL32",
            "description": "Memoria RAM DDR5 dual-channel di livello enthusiast. Dissipatore in alluminio spazzolato nero opaco con barra luminosa RGB integrata. Stabilità e velocità estreme.",
            "price": 149.99,
            "stock": 20,
            "category": "Memoria RAM"
        },
        # Scheda Video (GPU)
        {
            "name": "ASUS TUF Gaming GeForce RTX 4070 Ti Super 16GB",
            "description": "Scheda video NVIDIA GeForce di ultima generazione con architettura Ada Lovelace. 16GB di VRAM GDDR6X, supporto DLSS 3, Ray Tracing di terza generazione e un eccellere sistema di raffreddamento a tre ventole TUF.",
            "price": 889.00,
            "stock": 6,
            "category": "Scheda Video"
        },
        {
            "name": "Sapphire PULSE AMD Radeon RX 7800 XT 16GB",
            "description": "Scheda grafica basata sull'architettura AMD RDNA 3. Dispone di 16GB di memoria GDDR6, ideale per giocare in 1440p con dettagli al massimo. Silenziosa, efficiente e dal design compatto.",
            "price": 549.99,
            "stock": 14,
            "category": "Scheda Video"
        },
        # Alimentatore (PSU)
        {
            "name": "Corsair RM850x 850W 80+ Gold",
            "description": "Alimentatore ATX completamente modulare con certificazione 80 Plus Gold. Dotato di ventola a levitazione magnetica da 135mm silenziosissima e condensatori giapponesi a 105°C.",
            "price": 139.99,
            "stock": 18,
            "category": "Alimentatore"
        },
        {
            "name": "Seasonic FOCUS GX-750 750W 80+ Gold",
            "description": "Alimentatore modulare compatto di altissima affidabilità. Certificazione 80 Plus Gold, controllo della ventola ibrido silenzioso per il miglior compromesso termico e acustico.",
            "price": 115.00,
            "stock": 15,
            "category": "Alimentatore"
        },
        # Dissipatore (Cooler)
        {
            "name": "Noctua NH-D15 chromax.black",
            "description": "Il re dei dissipatori ad aria per CPU. Doppia torre con due ventole NF-A15 PWM da 140mm. Prestazioni di raffreddamento pari ai sistemi a liquido AIO con la massima silenziosità e durata nel tempo.",
            "price": 109.90,
            "stock": 16,
            "category": "Dissipatore"
        },
        {
            "name": "NZXT Kraken Elite 360 RGB Black",
            "description": "Dissipatore a liquido AIO per CPU con radiatore da 360mm. Dotato di 3 ventole RGB da 120mm e un incredibile display LCD da 2.36\" sulla pompa per monitorare le temperature o mostrare GIF personalizzate.",
            "price": 289.99,
            "stock": 7,
            "category": "Dissipatore"
        },
        # Storage (SSD/HDD)
        {
            "name": "Samsung 990 PRO M.2 NVMe SSD 2TB",
            "description": "SSD PCIe 4.0 NVMe ultra-veloce. Raggiunge velocità di lettura sequenziale fino a 7450 MB/s e di scrittura fino a 6900 MB/s. Prestazioni ed efficienza al top per gaming ed editing video.",
            "price": 179.99,
            "stock": 30,
            "category": "Storage"
        },
        {
            "name": "Crucial P3 Plus 1TB M.2 PCIe 4.0 NVMe",
            "description": "SSD NVMe M.2 ad alte prestazioni a un prezzo eccezionale. Fino a 5000 MB/s in lettura sequenziale, ideale come disco principale o per espandere lo spazio del tuo PC.",
            "price": 79.90,
            "stock": 40,
            "category": "Storage"
        }
    ]

    for p_data in products_data:
        cat_name = p_data.pop("category")
        p = Product.objects.create(**p_data)
        p.categories.add(categories[cat_name])

def remove_pc_components(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Product = apps.get_model('shop', 'Product')
    Product.objects.all().delete()
    Category.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_create_roles'),
    ]

    operations = [
        migrations.RunPython(populate_pc_components, remove_pc_components),
    ]
