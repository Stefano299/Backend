import os
import django
import random
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from shop.models import Category, Product, DiscountCode, Review, Order

User = get_user_model()

def run():
    print("Flushing database...")
    Order.objects.all().delete()
    DiscountCode.objects.all().delete()
    Review.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()
    Group.objects.all().delete()

    print("Creating Groups and Permissions...")
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')
    
    for model in [Product, Category, Order, DiscountCode]:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            manager_group.permissions.add(perm)

    print("Creating Users...")
    admin = User.objects.create_superuser(username='admin', password='admin12345', email='admin@demo.com')
    manager = User.objects.create_user(username='manager', password='manager12345', email='manager@demo.com', is_staff=True)
    manager.groups.add(manager_group)
    bob = User.objects.create_user(username='bob', password='bob12345', email='bob@demo.com')
    bobby = User.objects.create_user(username='bobby', password='bobby12345', email='bobby@demo.com')
    taylor = User.objects.create_user(username='taylor', password='taylor12345', email='taylor@demo.com')
    john = User.objects.create_user(username='john', password='john12345', email='john@demo.com')

    print("Creating Categories...")
    cat_cpu = Category.objects.create(name='Processore')
    cat_mobo = Category.objects.create(name='Scheda Madre')
    cat_ram = Category.objects.create(name='Memoria RAM')
    cat_gpu = Category.objects.create(name='Scheda Video')
    cat_psu = Category.objects.create(name='Alimentatore')
    cat_case = Category.objects.create(name='Case')
    cat_cooler = Category.objects.create(name='Dissipatore')
    cat_storage = Category.objects.create(name='Storage')

    print("Creating Products...")
    products_data = [
        # Intel Build
        {
            'name': 'Intel Core i9-14900K',
            'description': 'Processore Intel Core di 14a generazione socket LGA1700. Frequenze altissime per gaming e produttività, compatibile con schede madri della serie 700.',
            'price': Decimal('599.99'),
            'discount_price': Decimal('549.99'),
            'stock': 10,
            'image': 'products/cpu.jpg',
            'categories': [cat_cpu],
        },
        {
            'name': 'ASUS ROG Maximus Z790 Hero',
            'description': 'Scheda madre premium per processori Intel LGA1700. Supporta memorie DDR5 e PCIe 5.0.',
            'price': Decimal('649.99'),
            'stock': 5,
            'image': 'products/motherboard.jpg',
            'categories': [cat_mobo],
        },
        {
            'name': 'Intel Core i5-13600K',
            'description': 'Ottimo processore Intel LGA1700 per gaming in 1440p, eccellente rapporto qualità-prezzo.',
            'price': Decimal('329.99'),
            'stock': 15,
            'image': 'products/cpu.jpg',
            'categories': [cat_cpu],
        },
        {
            'name': 'MSI PRO Z790-P WIFI',
            'description': 'Scheda madre LGA1700 affidabile per processori Intel, supporto DDR5 e Wi-Fi 6E.',
            'price': Decimal('239.99'),
            'discount_price': Decimal('209.99'),
            'stock': 8,
            'image': 'products/motherboard.jpg',
            'categories': [cat_mobo],
        },
        # AMD Build
        {
            'name': 'AMD Ryzen 7 7800X3D',
            'description': 'Il miglior processore per il gaming. Socket AM5. Cache 3D V-Cache.',
            'price': Decimal('399.99'),
            'stock': 15,
            'image': 'products/cpu.jpg',
            'categories': [cat_cpu],
        },
        {
            'name': 'MSI MAG B650 Tomahawk WiFi',
            'description': 'Scheda madre ATX per socket AMD AM5. Supporta memorie DDR5 e PCIe 4.0.',
            'price': Decimal('229.99'),
            'stock': 20,
            'image': 'products/motherboard.jpg',
            'categories': [cat_mobo],
        },
        {
            'name': 'AMD Ryzen 5 7600X',
            'description': 'Processore AMD per socket AM5, perfetto per una build gaming economica.',
            'price': Decimal('249.99'),
            'stock': 25,
            'image': 'products/cpu.jpg',
            'categories': [cat_cpu],
        },
        {
            'name': 'ASUS TUF Gaming X670E-PLUS',
            'description': 'Scheda madre AM5 robusta e durevole con PCIe 5.0 per le ultime GPU AMD e NVIDIA.',
            'price': Decimal('319.99'),
            'stock': 12,
            'image': 'products/motherboard.jpg',
            'categories': [cat_mobo],
        },
        # RAM
        {
            'name': 'Corsair Vengeance RGB DDR5 32GB 6000MHz',
            'description': 'Memoria RAM DDR5 ad alte prestazioni. Compatibile con schede madri DDR5.',
            'price': Decimal('139.99'),
            'stock': 30,
            'image': 'products/ram.jpg',
            'categories': [cat_ram],
        },
        {
            'name': 'G.Skill Trident Z5 Neo RGB 32GB DDR5 6000MHz EXPO',
            'description': 'Memorie DDR5 ottimizzate per profili EXPO delle schede madri AM5.',
            'price': Decimal('145.99'),
            'stock': 18,
            'image': 'products/ram.jpg',
            'categories': [cat_ram],
        },
        {
            'name': 'Kingston FURY Beast DDR4 16GB 3200MHz',
            'description': 'Memoria RAM DDR4, attenzione, NON compatibile con le ultime schede madri LGA1700/AM5 che richiedono DDR5.',
            'price': Decimal('49.99'),
            'stock': 0, # Esaurito
            'image': 'products/ram.jpg',
            'categories': [cat_ram],
        },
        {
            'name': 'Crucial Pro DDR4 32GB 3200MHz',
            'description': 'Kit RAM DDR4 da 32GB per sistemi di passata generazione.',
            'price': Decimal('69.99'),
            'discount_price': Decimal('59.99'),
            'stock': 10,
            'image': 'products/ram.jpg',
            'categories': [cat_ram],
        },
        # GPU
        {
            'name': 'NVIDIA GeForce RTX 4080 Super',
            'description': 'Scheda video ad alte prestazioni. Richiede alimentatore potente.',
            'price': Decimal('1199.99'),
            'stock': 8,
            'image': 'products/gpu.jpg',
            'categories': [cat_gpu],
        },
        {
            'name': 'AMD Radeon RX 7800 XT',
            'description': 'Ottima scheda per gaming in 1440p.',
            'price': Decimal('549.99'),
            'discount_price': Decimal('499.99'),
            'stock': 12,
            'image': 'products/gpu.jpg',
            'categories': [cat_gpu],
        },
        {
            'name': 'NVIDIA GeForce RTX 4060 Ti 8GB',
            'description': 'Scheda video ideale per il gaming in 1080p a dettagli massimi.',
            'price': Decimal('419.99'),
            'stock': 0, # Esaurito
            'image': 'products/gpu.jpg',
            'categories': [cat_gpu],
        },
        {
            'name': 'AMD Radeon RX 7900 XTX 24GB',
            'description': 'Il vertice delle prestazioni AMD. Perfetta per il gaming in 4K.',
            'price': Decimal('1049.99'),
            'discount_price': Decimal('999.99'),
            'stock': 4,
            'image': 'products/gpu.jpg',
            'categories': [cat_gpu],
        },
        # PSU
        {
            'name': 'Corsair RM850x 850W 80+ Gold',
            'description': 'Alimentatore ATX completamente modulare da 850W. Ideale per RTX 4080.',
            'price': Decimal('149.99'),
            'stock': 25,
            'image': 'products/powersupply.jpg',
            'categories': [cat_psu],
        },
        {
            'name': 'Seasonic FOCUS GX-750 750W 80+ Gold',
            'description': 'Alimentatore affidabile e silenzioso per build di fascia media.',
            'price': Decimal('119.99'),
            'stock': 14,
            'image': 'products/powersupply.jpg',
            'categories': [cat_psu],
        },
        # Dissipatori
        {
            'name': 'Noctua NH-D15',
            'description': 'Il re dei dissipatori ad aria. Include kit per LGA1700 e AM5.',
            'price': Decimal('109.99'),
            'stock': 18,
            'image': 'products/cooler.jpg',
            'categories': [cat_cooler],
        },
        {
            'name': 'NZXT Kraken Elite 360',
            'description': 'Dissipatore a liquido AIO. Compatibile LGA1700 e AM5.',
            'price': Decimal('279.99'),
            'stock': 0, # Esaurito
            'image': 'products/cooler.jpg',
            'categories': [cat_cooler],
        },
        # Case
        {
            'name': 'NZXT H9 Flow',
            'description': 'Case mid-tower a doppia camera per un flusso d\'aria eccezionale.',
            'price': Decimal('189.99'),
            'stock': 7,
            'image': 'products/case.jpg',
            'categories': [cat_case],
        },
        # Storage
        {
            'name': 'Samsung 990 PRO M.2 NVMe SSD 2TB',
            'description': 'SSD ultra-veloce PCIe 4.0.',
            'price': Decimal('169.99'),
            'discount_price': Decimal('149.99'),
            'stock': 22,
            'image': 'products/storage.jpg',
            'categories': [cat_storage],
        }
    ]

    products_obj = []
    for p_data in products_data:
        cats = p_data.pop('categories')
        p = Product.objects.create(**p_data)
        p.categories.set(cats)
        products_obj.append(p)

    print("Creating Discount Codes...")
    DiscountCode.objects.create(code='SCONTO10', amount=Decimal('10.00'))
    DiscountCode.objects.create(code='PROMO20', amount=Decimal('20.00'))
    DiscountCode.objects.create(code='WELCOME5', amount=Decimal('5.00'))

    print("Creating Reviews...")
    Review.objects.create(product=products_obj[4], user=bob, rating=5, comment='Processore eccezionale!') # 7800X3D
    Review.objects.create(product=products_obj[4], user=bobby, rating=4, comment='Ottimo, ma scalda un po\'.')
    Review.objects.create(product=products_obj[0], user=taylor, rating=5, comment='Un mostro di potenza.') # 14900K
    Review.objects.create(product=products_obj[12], user=john, rating=5, comment='Prestazioni incredibili in 4K.') # 4080 Super
    Review.objects.create(product=products_obj[10], user=bob, rating=1, comment='Ho sbagliato acquisto, non va sulla mia scheda madre nuova.') # DDR4
    Review.objects.create(product=products_obj[1], user=john, rating=5, comment='Scheda madre top per LGA1700!') # ROG Z790
    Review.objects.create(product=products_obj[15], user=taylor, rating=5, comment='RX 7900 XTX fantastica, nessun problema.') # 7900 XTX
    Review.objects.create(product=products_obj[21], user=bobby, rating=5, comment='SSD Samsung super veloce, sistema si avvia in un lampo.') # 990 PRO

    print("Database popolato con successo!")

if __name__ == '__main__':
    run()
