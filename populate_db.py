import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Category, Product, Review
from orders.models import DiscountCode, Order, OrderItem, CartItem

User = get_user_model()

def run():
    print("Flushing database...")
    CartItem.objects.all().delete()
    OrderItem.objects.all().delete()
    Order.objects.all().delete()
    Review.objects.all().delete()
    Product.objects.all().delete()
    Category.objects.all().delete()
    User.objects.all().delete()
    Group.objects.all().delete()
    DiscountCode.objects.all().delete()

    print("Creating Groups and Permissions...")
    manager_group, _ = Group.objects.get_or_create(name='Store Manager')
    customer_group, _ = Group.objects.get_or_create(name='Customer')
    
    for model in [Product, Category, Review, Order, DiscountCode]:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        for perm in permissions:
            manager_group.permissions.add(perm)

    print("Creating Users...")
    admin = User.objects.create_superuser(username='admin', password='admin12345', email='admin@demo.com')
    
    manager = User.objects.create_user(username='manager', password='manager12345', email='manager@demo.com', is_staff=True)
    manager.groups.add(manager_group)
    
    # 3 basic users who will have left the most reviews (5 reviews each)
    bob = User.objects.create_user(username='bob', password='bob12345', email='bob@demo.com')
    bob.groups.add(customer_group)
    bob.first_name = "Bob"
    bob.last_name = "Rossi"
    bob.indirizzo = "Via Roma 1"
    bob.citta = "Milano"
    bob.codice_postale = "20121"
    bob.numero_di_telefono = "3331234567"
    bob.save()

    bobby = User.objects.create_user(username='bobby', password='bobby12345', email='bobby@demo.com')
    bobby.groups.add(customer_group)
    bobby.first_name = "Bobby"
    bobby.last_name = "Verdi"
    bobby.indirizzo = "Corso Vittorio 10"
    bobby.citta = "Torino"
    bobby.codice_postale = "10100"
    bobby.numero_di_telefono = "3337654321"
    bobby.save()

    taylor = User.objects.create_user(username='taylor', password='taylor12345', email='taylor@demo.com')
    taylor.groups.add(customer_group)
    taylor.first_name = "Taylor"
    taylor.last_name = "Bianchi"
    taylor.indirizzo = "Via Garibaldi 5"
    taylor.citta = "Firenze"
    taylor.codice_postale = "50100"
    taylor.numero_di_telefono = "3339876543"
    taylor.save()

    # Basic users with fewer reviews (2 reviews or 1 review)
    john = User.objects.create_user(username='john', password='john12345', email='john@demo.com')
    john.groups.add(customer_group)
    john.first_name = "John"
    john.last_name = "Doe"
    john.indirizzo = "Piazza Duomo 2"
    john.citta = "Milano"
    john.codice_postale = "20121"
    john.numero_di_telefono = "3334445555"
    john.save()

    alice = User.objects.create_user(username='alice', password='alice12345', email='alice@demo.com')
    alice.groups.add(customer_group)
    alice.first_name = "Alice"
    alice.last_name = "Neri"
    alice.indirizzo = "Via Dante 12"
    alice.citta = "Bologna"
    alice.codice_postale = "40121"
    alice.numero_di_telefono = "3335556666"
    alice.save()

    charlie = User.objects.create_user(username='charlie', password='charlie12345', email='charlie@demo.com')
    charlie.groups.add(customer_group)
    charlie.first_name = "Charlie"
    charlie.last_name = "Marrone"
    charlie.indirizzo = "Piazza Erbe 3"
    charlie.citta = "Verona"
    charlie.codice_postale = "37121"
    charlie.numero_di_telefono = "3338889999"
    charlie.save()

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
        # Coolers
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
            'discount_price': Decimal('249.99'),
            'stock': 6,
            'image': 'products/cooler.jpg',
            'categories': [cat_cooler],
        },
        {
            'name': 'Be Quiet! Pure Rock 2 Black',
            'description': 'Dissipatore ad aria per CPU silenzioso ed efficiente. Ottimizzato per sistemi Intel LGA1700/1200.',
            'price': Decimal('39.99'),
            'stock': 15,
            'image': 'products/cooler.jpg',
            'categories': [cat_cooler],
        },
        # Cases
        {
            'name': 'NZXT H9 Flow',
            'description': 'Case mid-tower a doppia camera per un flusso d\'aria eccezionale.',
            'price': Decimal('189.99'),
            'stock': 7,
            'image': 'products/case.jpg',
            'categories': [cat_case],
        },
        {
            'name': 'Corsair 4000D Airflow',
            'description': 'Case ATX mid-tower con pannello frontale ottimizzato per il massimo flusso d\'aria. Vetro temperato.',
            'price': Decimal('99.99'),
            'stock': 0,
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
        },
        {
            'name': 'Crucial P3 Plus 1TB PCIe M.2 2280 SSD',
            'description': 'SSD NVMe PCIe Gen4 con velocità di lettura fino a 5000MB/s.',
            'price': Decimal('79.99'),
            'stock': 25,
            'image': 'products/storage.jpg',
            'categories': [cat_storage],
        }
    ]

    products_map = {}
    for p_data in products_data:
        cats = p_data.pop('categories')
        p = Product.objects.create(**p_data)
        p.categories.set(cats)
        products_map[p.name] = p

    print("Creating Discount Codes...")
    dc_sconto10 = DiscountCode.objects.create(code='SCONTO10', discount_type='percentage', amount=Decimal('10.00'))
    dc_promo20 = DiscountCode.objects.create(code='PROMO20', discount_type='fixed', amount=Decimal('20.00'))
    dc_welcome5 = DiscountCode.objects.create(code='WELCOME5', discount_type='fixed', amount=Decimal('5.00'))

    # Selected products for 3 reviews each
    p_ryzen = products_map['AMD Ryzen 7 7800X3D']
    p_rtx4080 = products_map['NVIDIA GeForce RTX 4080 Super']
    p_samsung990 = products_map['Samsung 990 PRO M.2 NVMe SSD 2TB']

    # Other products to review
    p_i9 = products_map['Intel Core i9-14900K']
    p_z790 = products_map['ASUS ROG Maximus Z790 Hero']
    p_b650 = products_map['MSI MAG B650 Tomahawk WiFi']
    p_ram_corsair = products_map['Corsair Vengeance RGB DDR5 32GB 6000MHz']
    p_i5 = products_map['Intel Core i5-13600K']
    p_rx7800 = products_map['AMD Radeon RX 7800 XT']
    p_z790_p = products_map['MSI PRO Z790-P WIFI']
    p_ram_crucial = products_map['Crucial Pro DDR4 32GB 3200MHz']
    p_x670e = products_map['ASUS TUF Gaming X670E-PLUS']
    p_ryzen5 = products_map['AMD Ryzen 5 7600X']
    p_rx7900 = products_map['AMD Radeon RX 7900 XTX 24GB']
    
    # Newer products (placed on Page 1 of the catalog)
    p_pure_rock = products_map['Be Quiet! Pure Rock 2 Black']
    p_noctua = products_map['Noctua NH-D15']
    p_h9 = products_map['NZXT H9 Flow']
    p_crucial_p3 = products_map['Crucial P3 Plus 1TB PCIe M.2 2280 SSD']

    print("Creating Orders...")
    
    # 1. Bob's Completed Order (contains products he will review)
    order_bob = Order.objects.create(
        user=bob,
        first_name=bob.first_name,
        last_name=bob.last_name,
        email=bob.email,
        indirizzo=bob.indirizzo,
        citta=bob.citta,
        codice_postale=bob.codice_postale,
        numero_di_telefono=bob.numero_di_telefono,
        payment_method='card',
        shipping_status='consegnato',
        discount_code=dc_sconto10,
        discount_amount=Decimal('174.99')
    )
    OrderItem.objects.create(order=order_bob, product=p_ryzen, price=p_ryzen.price, quantity=1)
    OrderItem.objects.create(order=order_bob, product=p_rtx4080, price=p_rtx4080.price, quantity=1)
    OrderItem.objects.create(order=order_bob, product=p_samsung990, price=p_samsung990.current_price, quantity=1)
    OrderItem.objects.create(order=order_bob, product=p_i9, price=p_i9.price, quantity=1)
    OrderItem.objects.create(order=order_bob, product=p_z790, price=p_z790.price, quantity=1)
    OrderItem.objects.create(order=order_bob, product=p_h9, price=p_h9.price, quantity=1)
    
    # Bob's secondary order (just to showcase multiple orders)
    order_bob_2 = Order.objects.create(
        user=bob,
        first_name=bob.first_name,
        last_name=bob.last_name,
        email=bob.email,
        indirizzo=bob.indirizzo,
        citta=bob.citta,
        codice_postale=bob.codice_postale,
        numero_di_telefono=bob.numero_di_telefono,
        payment_method='transfer',
        shipping_status='ricevuto',
    )
    OrderItem.objects.create(order=order_bob_2, product=products_map['Corsair RM850x 850W 80+ Gold'], price=Decimal('149.99'), quantity=1)

    # 2. Bobby's Order (contains products, In Transit)
    order_bobby = Order.objects.create(
        user=bobby,
        first_name=bobby.first_name,
        last_name=bobby.last_name,
        email=bobby.email,
        indirizzo=bobby.indirizzo,
        citta=bobby.citta,
        codice_postale=bobby.codice_postale,
        numero_di_telefono=bobby.numero_di_telefono,
        payment_method='paypal',
        shipping_status='transito',
    )
    OrderItem.objects.create(order=order_bobby, product=p_ryzen, price=p_ryzen.price, quantity=1)
    OrderItem.objects.create(order=order_bobby, product=p_rtx4080, price=p_rtx4080.price, quantity=1)
    OrderItem.objects.create(order=order_bobby, product=p_samsung990, price=p_samsung990.current_price, quantity=1)
    OrderItem.objects.create(order=order_bobby, product=p_b650, price=p_b650.price, quantity=1)
    OrderItem.objects.create(order=order_bobby, product=p_ram_corsair, price=p_ram_corsair.price, quantity=1)
    OrderItem.objects.create(order=order_bobby, product=p_pure_rock, price=p_pure_rock.price, quantity=1)
    OrderItem.objects.create(order=order_bobby, product=p_noctua, price=p_noctua.price, quantity=1)

    # 3. Taylor's Order (contains products, Received/elaborating)
    order_taylor = Order.objects.create(
        user=taylor,
        first_name=taylor.first_name,
        last_name=taylor.last_name,
        email=taylor.email,
        indirizzo=taylor.indirizzo,
        citta=taylor.citta,
        codice_postale=taylor.codice_postale,
        numero_di_telefono=taylor.numero_di_telefono,
        payment_method='card',
        shipping_status='ricevuto',
    )
    OrderItem.objects.create(order=order_taylor, product=p_ryzen, price=p_ryzen.price, quantity=1)
    OrderItem.objects.create(order=order_taylor, product=p_rtx4080, price=p_rtx4080.price, quantity=1)
    OrderItem.objects.create(order=order_taylor, product=p_samsung990, price=p_samsung990.current_price, quantity=1)
    OrderItem.objects.create(order=order_taylor, product=p_i5, price=p_i5.price, quantity=1)
    OrderItem.objects.create(order=order_taylor, product=p_rx7800, price=p_rx7800.price, quantity=1)

    # 4. John's Order (contains products, Consegnato)
    order_john = Order.objects.create(
        user=john,
        first_name=john.first_name,
        last_name=john.last_name,
        email=john.email,
        indirizzo=john.indirizzo,
        citta=john.citta,
        codice_postale=john.codice_postale,
        numero_di_telefono=john.numero_di_telefono,
        payment_method='card',
        shipping_status='consegnato',
        discount_code=dc_welcome5,
        discount_amount=Decimal('5.00')
    )
    OrderItem.objects.create(order=order_john, product=p_z790_p, price=p_z790_p.price, quantity=1)
    OrderItem.objects.create(order=order_john, product=p_ram_crucial, price=p_ram_crucial.price, quantity=1)
    OrderItem.objects.create(order=order_john, product=p_crucial_p3, price=p_crucial_p3.price, quantity=1)

    # 5. Alice's Order (contains products, Consegnato)
    order_alice = Order.objects.create(
        user=alice,
        first_name=alice.first_name,
        last_name=alice.last_name,
        email=alice.email,
        indirizzo=alice.indirizzo,
        citta=alice.citta,
        codice_postale=alice.codice_postale,
        numero_di_telefono=alice.numero_di_telefono,
        payment_method='paypal',
        shipping_status='consegnato',
    )
    OrderItem.objects.create(order=order_alice, product=p_x670e, price=p_x670e.price, quantity=1)
    OrderItem.objects.create(order=order_alice, product=p_ryzen5, price=p_ryzen5.price, quantity=1)

    # 6. Charlie's Order (contains product, In Consegna)
    order_charlie = Order.objects.create(
        user=charlie,
        first_name=charlie.first_name,
        last_name=charlie.last_name,
        email=charlie.email,
        indirizzo=charlie.indirizzo,
        citta=charlie.citta,
        codice_postale=charlie.codice_postale,
        numero_di_telefono=charlie.numero_di_telefono,
        payment_method='transfer',
        shipping_status='consegna',
    )
    OrderItem.objects.create(order=order_charlie, product=p_rx7900, price=p_rx7900.price, quantity=1)

    print("Creating Reviews...")
    # Product 1: Ryzen 7 7800X3D Reviews 
    Review.objects.create(product=p_ryzen, user=bob, rating=5, comment='Ottimo processore per il gaming con temperature molto basse')
    Review.objects.create(product=p_ryzen, user=bobby, rating=4, comment="Scalda un po' troppo... ma va bene")
    Review.objects.create(product=p_ryzen, user=taylor, rating=5, comment='Assolutamente perfetto. Efficienza energetica bestiale')

    # Product 2: NVIDIA GeForce RTX 4080 Super Reviews 
    Review.objects.create(product=p_rtx4080, user=bob, rating=5, comment='Silenziosa a fresce, e fa girare tutto in 4K')
    Review.objects.create(product=p_rtx4080, user=bobby, rating=5, comment='Rispetto alla mia vecchia 3050 è un bestione')
    Review.objects.create(product=p_rtx4080, user=taylor, rating=4, comment='Scheda molto potente e top ma costa davvero tanto')

    # Product 3: Samsung 990 PRO Reviews 
    Review.objects.create(product=p_samsung990, user=bob, rating=5, comment='Super veloce ottima per caricamenti velocisissimi')
    Review.objects.create(product=p_samsung990, user=bobby, rating=4, comment='Molto veloce ma scalda troppo... prendete un buon dissipatore')
    Review.objects.create(product=p_samsung990, user=taylor, rating=3, comment='Ottimo SSD ma troppo costoso secondo me')

    # Bob's other reviews
    Review.objects.create(product=p_i9, user=bob, rating=5, comment='Prestazioni davvero altissime ma scalda parecchio, serve un buon dissipatore a liquido')
    Review.objects.create(product=p_z790, user=bob, rating=5, comment='Scheda madre top di gamma, ovviamente si paga la qualità')
    Review.objects.create(product=p_h9, user=bob, rating=5, comment='Ottimo design... perfettamente tutti i componenti')

    # Bobby's other reviews
    Review.objects.create(product=p_b650, user=bobby, rating=4, comment='Buona scheda madre, ce ne sono di meglio in giro ma per il prezzo va benissimo')
    Review.objects.create(product=p_ram_corsair, user=bobby, rating=2, comment='Costa davvero troppo')
    Review.objects.create(product=p_pure_rock, user=bobby, rating=5, comment='Dissipatore ad aria eccellente. Molto silenzioso, mantiene il mio processore fresco anche sotto sforzo')
    Review.objects.create(product=p_noctua, user=bobby, rating=5, comment='Il miglior dissipatore ad aria sul mercato. Dimensioni enormi ma prestazioni al top')

    # Taylor's other reviews
    Review.objects.create(product=p_i5, user=taylor, rating=5, comment='Miglior processore per rapporto qualità/prezzo del momento')
    Review.objects.create(product=p_rx7800, user=taylor, rating=3, comment='Ottima scheda video per giocare in 1440p, ottima alternativa a Nvidia ma cmq costosetta')

    # John's reviews
    Review.objects.create(product=p_z790_p, user=john, rating=4, comment='Fa il suo dovere ma non aspettatevi miracoli')
    Review.objects.create(product=p_ram_crucial, user=john, rating=4, comment='Classica ram, veloce ed economica')
    Review.objects.create(product=p_crucial_p3, user=john, rating=5, comment='SSD eccellente ad un ottimo prezzo. Caricamenti velocissimi')

    # Alice's reviews
    Review.objects.create(product=p_x670e, user=alice, rating=5, comment='Scheda madre ottima per tutto')
    Review.objects.create(product=p_ryzen5, user=alice, rating=5, comment='Migliore cpu che abbia mai comprato sinceramente')

    # Charlie's reviews
    Review.objects.create(product=p_rx7900, user=charlie, rating=1, comment='Terribile. non compratela')

    print("Database popolato con successo!")

if __name__ == '__main__':
    run()
