from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from catalog.models import Product, Category, Review
from orders.models import Order, OrderItem

User = get_user_model()

class ManagerDashboardTests(TestCase):
    def setUp(self):
        # Create groups
        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        from django.contrib.auth.models import Permission
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label__in=['catalog', 'orders']))
        
        # Create users
        self.customer = User.objects.create_user(username='customer1', password='password123')
        
        self.manager = User.objects.create_user(username='manager1', password='password123')
        self.manager.groups.add(self.manager_group)
        
        self.staff_user = User.objects.create_user(username='staff1', password='password123', is_staff=True)
        from django.contrib.auth.models import Permission
        view_product_perm = Permission.objects.get(codename='view_product', content_type__app_label='catalog')
        self.staff_user.user_permissions.add(view_product_perm)
        
        # Create sample models
        self.category = Category.objects.create(name='Processori')
        self.product = Product.objects.create(
            name='AMD Ryzen 5',
            price=200.00,
            stock=10
        )
        self.product.categories.add(self.category)
        
        self.order = Order.objects.create(
            user=self.customer,
            indirizzo='Via Roma 1',
            citta='Milano',
            codice_postale='20100',
            numero_di_telefono='123456789'
        )

    def test_anonymous_access_denied(self):
        response = self.client.get(reverse('dashboard:manager_dashboard'))
        # Should redirect to login since it has LoginRequiredMixin
        self.assertRedirects(response, f'/accounts/login/?next={reverse("dashboard:manager_dashboard")}')

    def test_customer_access_forbidden(self):
        self.client.login(username='customer1', password='password123')
        response = self.client.get(reverse('dashboard:manager_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_manager_access_granted(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.get(reverse('dashboard:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Manager')

    def test_staff_access_granted(self):
        self.client.login(username='staff1', password='password123')
        response = self.client.get(reverse('dashboard:manager_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_product_create(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('dashboard:product_create'), {
            'name': 'Intel i7',
            'description': 'Super CPU',
            'price': '350.00',
            'stock': 5,
            'image': '',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        self.assertTrue(Product.objects.filter(name='Intel i7').exists())

    def test_product_update(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('dashboard:product_update', args=[self.product.id]), {
            'name': 'AMD Ryzen 5 Updated',
            'price': '180.00',
            'stock': 8,
            'image': '',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'AMD Ryzen 5 Updated')
        self.assertEqual(self.product.stock, 8)

    def test_product_delete(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('dashboard:product_delete', args=[self.product.id]))
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_category_create(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('dashboard:category_create'), {
            'name': 'Schede Madri'
        })
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        self.assertTrue(Category.objects.filter(name='Schede Madri').exists())

    def test_order_update(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('dashboard:order_update', args=[self.order.id]), {
            'shipping_status': 'spedizione',
        })
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        self.order.refresh_from_db()
        self.assertEqual(self.order.shipping_status, 'spedizione')



class CartTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Processori')
        self.product = Product.objects.create(
            name='AMD Ryzen 5',
            price=200.00,
            stock=10
        )
        self.product.categories.add(self.category)

    def test_cart_item_removed_when_product_deleted(self):
        # Aggiungi prodotto al carrello
        response = self.client.post(reverse('orders:cart_add', args=[self.product.id]), {
            'quantity': 1,
            'override': False
        })
        self.assertRedirects(response, reverse('orders:cart_detail'))
        
        # Verifica che il prodotto sia mostrato nel carrello
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5')
        
        # Elimina il prodotto dal database
        self.product.delete()
        
        # Riapri il carrello: deve caricare correttamente e rimuovere il prodotto orfano senza NoReverseMatch
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'AMD Ryzen 5')
        
        # Il carrello deve risultare vuoto
        self.assertContains(response, 'Il tuo carrello è vuoto')


class DatabaseCartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cart_user', password='password123')
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            name='Intel Core i7',
            price=300.00,
            stock=10
        )
        self.product1.categories.add(self.category)
        self.product2 = Product.objects.create(
            name='NVIDIA RTX 4070',
            price=600.00,
            stock=5
        )
        self.product2.categories.add(self.category)

    def test_guest_cart_stored_in_session(self):
        # Aggiungi un prodotto come utente anonimo
        self.client.post(reverse('orders:cart_add', args=[self.product1.id]), {
            'quantity': 2,
            'override': False
        })
        
        # Verifica che sia nella sessione
        session = self.client.session
        self.assertIn('cart', session)
        self.assertIn(str(self.product1.id), session['cart'])
        self.assertEqual(session['cart'][str(self.product1.id)]['quantity'], 2)
        
        # Verifica che non ci siano CartItem nel DB
        from orders.models import CartItem
        self.assertEqual(CartItem.objects.count(), 0)

    def test_cart_merges_on_login(self):
        # Aggiungi un prodotto da anonimo
        self.client.post(reverse('orders:cart_add', args=[self.product1.id]), {
            'quantity': 2,
            'override': False
        })
        
        # Effettua il login
        self.client.login(username='cart_user', password='password123')
        
        # Naviga sul carrello per far innescare il caricamento/merge del carrello
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        
        # Verifica che il carrello della sessione sia stato rimosso ed elementi salvati nel DB
        session = self.client.session
        self.assertNotIn('cart', session)
        
        from orders.models import CartItem
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)
        db_item = CartItem.objects.get(user=self.user, product=self.product1)
        self.assertEqual(db_item.quantity, 2)

    def test_logged_in_cart_persists_in_db(self):
        self.client.login(username='cart_user', password='password123')
        
        # Aggiungi prodotto da loggato
        self.client.post(reverse('orders:cart_add', args=[self.product2.id]), {
            'quantity': 1,
            'override': False
        })
        
        # Verifica che sia direttamente nel DB
        from orders.models import CartItem
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)
        db_item = CartItem.objects.get(user=self.user, product=self.product2)
        self.assertEqual(db_item.quantity, 1)
        
        # Rimuovi il prodotto
        self.client.post(reverse('orders:cart_remove', args=[self.product2.id]))
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_cart_cleared_on_checkout(self):
        self.client.login(username='cart_user', password='password123')
        
        # Aggiungi un prodotto
        self.client.post(reverse('orders:cart_add', args=[self.product1.id]), {
            'quantity': 1,
            'override': False
        })
        
        from orders.models import CartItem
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)
        
        # Procedi al checkout ed esegui l'ordine
        order_data = {
            'first_name': 'Cart',
            'last_name': 'User',
            'email': 'cart@example.com',
            'indirizzo': 'Via Test 12',
            'citta': 'Milano',
            'codice_postale': '20100',
            'numero_di_telefono': '123456789',
            'payment_method': 'card',
        }
        response = self.client.post(reverse('orders:checkout'), order_data)
        self.assertEqual(response.status_code, 302)
        
        # Il carrello nel DB deve essere vuoto ora
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 0)

    def test_cart_merge_quantities_sum_up(self):
        from orders.models import CartItem
        # L'utente ha già il prodotto1 nel carrello DB con quantità 3
        CartItem.objects.create(
            user=self.user,
            product=self.product1,
            quantity=3
        )

        # Da anonimo aggiunge lo stesso prodotto1 con quantità 2
        self.client.post(reverse('orders:cart_add', args=[self.product1.id]), {
            'quantity': 2,
            'override': False
        })

        # Effettua il login
        self.client.login(username='cart_user', password='password123')

        # Visita il carrello per scatenare il merge
        self.client.get(reverse('orders:cart_detail'))

        # La quantità finale nel DB deve essere 5 (3 + 2)
        self.assertEqual(CartItem.objects.filter(user=self.user).count(), 1)
        db_item = CartItem.objects.get(user=self.user, product=self.product1)
        self.assertEqual(db_item.quantity, 5)

    def test_cart_loads_from_db_without_session(self):
        from orders.models import CartItem
        # L'utente ha già il prodotto2 nel carrello DB con quantità 4
        CartItem.objects.create(
            user=self.user,
            product=self.product2,
            quantity=4
        )

        # Effettua il login senza aver aggiunto nulla da anonimo (sessione vuota)
        self.client.login(username='cart_user', password='password123')

        # Visita la pagina del carrello
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)

        # Verifica che il prodotto sia mostrato nel carrello con quantità 4
        self.assertContains(response, 'NVIDIA RTX 4070')
        self.assertContains(response, '4')


class ReviewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Processori')
        self.product = Product.objects.create(
            name='AMD Ryzen 5',
            price=200.00,
            stock=10
        )
        self.product.categories.add(self.category)
        
        # Utente acquirente
        self.buyer = User.objects.create_user(username='buyer1', password='password123')
        # Altro utente che non compra
        self.other_user = User.objects.create_user(username='other1', password='password123')
        
    def test_cannot_review_without_purchase(self):
        self.client.login(username='other1', password='password123')
        response = self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Bellissimo!'
        })
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Review.objects.filter(product=self.product).exists())
        
    def test_can_review_after_purchase(self):
        # Simula un acquisto completato creando un ordine e relativo OrderItem per il buyer
        order = Order.objects.create(
            user=self.buyer,
            indirizzo='Via Roma 1',
            citta='Milano',
            codice_postale='20100',
            numero_di_telefono='123456789'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=1
        )
        
        self.client.login(username='buyer1', password='password123')
        response = self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Ottimo processore!'
        })
        self.assertRedirects(response, reverse('catalog:product_detail', args=[self.product.id]))
        self.assertTrue(Review.objects.filter(product=self.product, user=self.buyer).exists())
        
        # Prova a inserire una seconda recensione sullo stesso prodotto: deve dare 403
        response = self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 4,
            'comment': 'Un altro commento'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.filter(product=self.product, user=self.buyer).count(), 1)

    def test_invalid_review_submission(self):
        # Simula un acquisto completato creando un ordine e relativo OrderItem per il buyer
        order = Order.objects.create(
            user=self.buyer,
            indirizzo='Via Roma 1',
            citta='Milano',
            codice_postale='20100',
            numero_di_telefono='123456789'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=1
        )
        
        self.client.login(username='buyer1', password='password123')
        # Invio di dati non validi (valutazione non ammessa: 10 stelle)
        response = self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 10,
            'comment': 'Fantastico!'
        })
        # Dovrebbe reindirizzare indietro senza salvare nulla nel database
        self.assertRedirects(response, reverse('catalog:product_detail', args=[self.product.id]))
        self.assertFalse(Review.objects.filter(product=self.product).exists())

    def test_review_ui_visibility_anonymous(self):
        # Utente anonimo non deve vedere il form ma il messaggio per accedere
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Accedi per lasciare una recensione.')
        self.assertNotContains(response, 'Lascia una recensione')

    def test_review_ui_visibility_buyer_before_and_after_purchase(self):
        # Prima dell'acquisto
        self.client.login(username='buyer1', password='password123')
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Devi aver acquistato questo prodotto per poter lasciare una recensione.')
        self.assertNotContains(response, 'Lascia una recensione')
        
        # Effettua acquisto
        order = Order.objects.create(
            user=self.buyer,
            indirizzo='Via Roma 1',
            citta='Milano',
            codice_postale='20100',
            numero_di_telefono='123456789'
        )
        OrderItem.objects.create(
            order=order,
            product=self.product,
            price=self.product.price,
            quantity=1
        )
        
        # Dopo l'acquisto ma prima di recensire
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Lascia una recensione')
        self.assertNotContains(response, 'Devi aver acquistato questo prodotto')
        
        # Invia la recensione
        self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Recensione di prova'
        })
        
        # Dopo aver recensito
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Hai già recensito questo prodotto.')
        self.assertNotContains(response, 'Lascia una recensione')

    def test_manager_can_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment='Bella!')
        from django.contrib.auth.models import Group, Permission
        manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        manager_group.permissions.add(*Permission.objects.filter(content_type__app_label__in=['catalog', 'orders']))
        manager = User.objects.create_user(username='manager_review', password='password123')
        manager.groups.add(manager_group)
        
        self.client.login(username='manager_review', password='password123')
        response = self.client.post(reverse('dashboard:review_delete', args=[review.id]))
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_buyer_cannot_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment='Bella!')
        self.client.login(username='buyer1', password='password123')
        response = self.client.post(reverse('dashboard:review_delete', args=[review.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_average_rating_display(self):
        # Prima di recensioni, il rating deve essere "Ancora nessuna recensione"
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Ancora nessuna recensione')
        
        # Aggiungiamo due recensioni
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment='Molto buono')
        other_buyer = User.objects.create_user(username='other_buyer', password='password123')
        Review.objects.create(product=self.product, user=other_buyer, rating=5, comment='Eccellente')
        
        # Media deve essere 4.5 su 5
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'star-icon filled')


class PCBuilderTests(TestCase):
    def setUp(self):
        # Crea o recupera le categorie richieste per il builder
        self.cpu_cat, _ = Category.objects.get_or_create(name='Processore')
        self.cooler_cat, _ = Category.objects.get_or_create(name='Dissipatore')
        self.mobo_cat, _ = Category.objects.get_or_create(name='Scheda Madre')
        self.ram_cat, _ = Category.objects.get_or_create(name='Memoria RAM')
        self.gpu_cat, _ = Category.objects.get_or_create(name='Scheda Video')
        self.storage_cat, _ = Category.objects.get_or_create(name='Storage')
        self.psu_cat, _ = Category.objects.get_or_create(name='Alimentatore')
        self.case_cat, _ = Category.objects.get_or_create(name='Case')

        # Crea prodotti per testare il flusso ed il filtro di compatibilità
        self.cpu_amd = Product.objects.create(name='AMD Ryzen 5 7600', description='Processore socket AM5', price=200.00, stock=5)
        self.cpu_amd.categories.add(self.cpu_cat)

        self.cpu_intel = Product.objects.create(name='Intel Core i5-13400', description='Processore LGA1700', price=210.00, stock=5)
        self.cpu_intel.categories.add(self.cpu_cat)

        self.mobo_amd = Product.objects.create(name='ASUS Prime B650', description='Scheda madre AM5 socket', price=150.00, stock=5)
        self.mobo_amd.categories.add(self.mobo_cat)

        self.mobo_intel = Product.objects.create(name='ASUS Prime B760', description='Scheda madre LGA1700 socket', price=140.00, stock=5)
        self.mobo_intel.categories.add(self.mobo_cat)

        self.cooler = Product.objects.create(name='Be Quiet Pure Rock', description='Cooler', price=40.00, stock=5)
        self.cooler.categories.add(self.cooler_cat)

        self.ram = Product.objects.create(name='Kingston Fury 16GB', description='RAM DDR5', price=70.00, stock=5)
        self.ram.categories.add(self.ram_cat)

        self.gpu = Product.objects.create(name='Nvidia RTX 4060', description='GPU', price=300.00, stock=5)
        self.gpu.categories.add(self.gpu_cat)

        self.storage = Product.objects.create(name='Crucial P3 1TB', description='SSD M.2', price=60.00, stock=5)
        self.storage.categories.add(self.storage_cat)

        self.psu = Product.objects.create(name='Corsair CX650M', description='PSU 650W', price=80.00, stock=5)
        self.psu.categories.add(self.psu_cat)

        self.case = Product.objects.create(name='Corsair 4000D', description='ATX Case', price=90.00, stock=5)
        self.case.categories.add(self.case_cat)

    def test_step_view_and_selection(self):
        # Verifica la visualizzazione dello Step 1 (CPU)
        response = self.client.get(reverse('catalog:pc_builder_step', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'Intel Core i5-13400')

        # Seleziona la CPU AMD inviando il form via POST
        response = self.client.post(reverse('catalog:pc_builder_step', args=[1]), {'product_id': self.cpu_amd.id})
        # Dovrebbe reindirizzare allo step successivo (Step 2)
        self.assertRedirects(response, reverse('catalog:pc_builder_step', args=[2]))
        # Controlla che sia stato salvato in sessione
        self.assertEqual(self.client.session.get('pc_build_step_1'), str(self.cpu_amd.id))

    def test_compatibility_filtering(self):
        # Imposta in sessione la scelta di una CPU AMD al passo 1
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_amd.id)
        session.save()

        # Visita il passo 3 (Scheda Madre)
        response = self.client.get(reverse('catalog:pc_builder_step', args=[3]))
        self.assertEqual(response.status_code, 200)
        # Dovrebbe contenere solo la scheda madre compatibile AMD AM5
        self.assertContains(response, 'ASUS Prime B650')
        self.assertNotContains(response, 'ASUS Prime B760')

        # Cambiamo la CPU in Intel
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_intel.id)
        session.save()

        response = self.client.get(reverse('catalog:pc_builder_step', args=[3]))
        self.assertEqual(response.status_code, 200)
        # Se CPU è Intel, filtriamo (quindi escludiamo la scheda madre AMD 'ASUS Prime B650')
        self.assertContains(response, 'ASUS Prime B760')
        self.assertNotContains(response, 'ASUS Prime B650')

    def test_summary_and_add_to_cart(self):
        # Simula la selezione di tutti gli 8 componenti salvandoli in sessione
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_amd.id)
        session['pc_build_step_2'] = str(self.cooler.id)
        session['pc_build_step_3'] = str(self.mobo_amd.id)
        session['pc_build_step_4'] = str(self.ram.id)
        session['pc_build_step_5'] = str(self.gpu.id)
        session['pc_build_step_6'] = str(self.storage.id)
        session['pc_build_step_7'] = str(self.psu.id)
        session['pc_build_step_8'] = str(self.case.id)
        session.save()

        # Visualizza la pagina di riepilogo
        response = self.client.get(reverse('catalog:pc_builder_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'ASUS Prime B650')
        self.assertContains(response, 'Corsair 4000D')
        self.assertNotContains(response, 'La configurazione è incompleta')

        # Invia la conferma del riepilogo via POST per aggiungere al carrello
        response = self.client.post(reverse('catalog:pc_builder_summary'))
        # Dovrebbe reindirizzare alla pagina di dettaglio del carrello
        self.assertRedirects(response, reverse('orders:cart_detail'))

        # Controlla che i componenti siano nel carrello
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'ASUS Prime B650')
        self.assertContains(response, 'Corsair 4000D')

        # Controlla che la sessione dell'assemblaggio sia stata pulita
        for i in range(1, 9):
            self.assertIsNone(self.client.session.get(f'pc_build_step_{i}'))

    def test_clear_builder(self):
        # Simula alcune scelte parziali in sessione
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_amd.id)
        session['pc_build_step_2'] = str(self.cooler.id)
        session.save()

        # Chiama l'URL di cancellazione
        response = self.client.get(reverse('catalog:pc_builder_clear'))
        self.assertRedirects(response, reverse('catalog:pc_builder_step', args=[1]))

        # Verifica che la sessione sia vuota
        for i in range(1, 9):
            self.assertIsNone(self.client.session.get(f'pc_build_step_{i}'))


from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import shutil
from django.test import override_settings

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ProductImageTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        from django.contrib.auth.models import Permission
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label__in=['catalog', 'orders']))
        self.manager = User.objects.create_user(username='manager_img', password='password123')
        self.manager.groups.add(self.manager_group)
        self.category = Category.objects.create(name='Processori')

    def test_product_create_with_image(self):
        self.client.login(username='manager_img', password='password123')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded_image = SimpleUploadedFile('test_image.gif', small_gif, content_type='image/gif')
        
        response = self.client.post(reverse('dashboard:product_create'), {
            'name': 'Intel Core i9',
            'description': 'Powerful CPU',
            'price': '600.00',
            'stock': 3,
            'image': uploaded_image,
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('dashboard:manager_dashboard'))
        
        product = Product.objects.get(name='Intel Core i9')
        self.assertTrue(product.image.name.startswith('products/test_image'))
        self.assertTrue(product.image.url.startswith('/media/products/test_image'))

    def test_product_fallback_image(self):
        product = Product.objects.create(
            name='Intel Core i3',
            price=100.00,
            stock=15
        )
        self.assertEqual(product.image.url, "/media/products/default.png")


class CheckoutTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username='customer_chk',
            password='password123',
            email='old@example.com',
            first_name='OldFirst',
            last_name='OldLast'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=50.00,
            stock=10
        )

    def test_checkout_prepopulated_fields(self):
        self.client.login(username='customer_chk', password='password123')
        
        # Add product to cart
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'quantity': 1,
                'price': str(self.product.price)
            }
        }
        session.save()

        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'OldFirst')
        self.assertContains(response, 'OldLast')
        self.assertContains(response, 'old@example.com')

    def test_checkout_saves_and_updates_profile(self):
        self.client.login(username='customer_chk', password='password123')
        
        # Add product to cart
        session = self.client.session
        session['cart'] = {
            str(self.product.id): {
                'quantity': 1,
                'price': str(self.product.price)
            }
        }
        session.save()

        post_data = {
            'first_name': 'NewFirst',
            'last_name': 'NewLast',
            'email': 'new@example.com',
            'indirizzo': 'Via Nuova 5',
            'citta': 'Torino',
            'codice_postale': '10100',
            'numero_di_telefono': '0987654321',
            'payment_method': 'paypal'
        }

        response = self.client.post(reverse('orders:checkout'), data=post_data)
        
        # Should redirect to order success page
        self.assertEqual(response.status_code, 302)
        
        # Verify user profile was updated
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'NewFirst')
        self.assertEqual(self.customer.last_name, 'NewLast')
        self.assertEqual(self.customer.email, 'new@example.com')
        self.assertEqual(self.customer.indirizzo, 'Via Nuova 5')
        self.assertEqual(self.customer.citta, 'Torino')
        self.assertEqual(self.customer.codice_postale, '10100')
        self.assertEqual(self.customer.numero_di_telefono, '0987654321')

        # Verify order was created
        order = Order.objects.filter(user=self.customer, payment_method='paypal').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.first_name, 'NewFirst')
        self.assertEqual(order.last_name, 'NewLast')
        self.assertEqual(order.email, 'new@example.com')

        # Verify product stock was decremented
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)


class CatalogPaginationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        # Creiamo 15 prodotti per testare la paginazione di 12 per pagina
        for i in range(15):
            p = Product.objects.create(
                name=f'Product {i:02d}',
                price=10.00 + i,
                stock=5
            )
            p.categories.add(self.category)

    def test_catalog_pagination_first_page(self):
        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&sort=name_asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['products'].paginator.count, 15)
        self.assertEqual(len(response.context['products']), 12)
        # Check active button 1
        self.assertContains(response, 'class="pagination-btn active">1</span>')
        self.assertContains(response, 'Product 00')
        self.assertNotContains(response, 'Product 13')

    def test_catalog_pagination_second_page(self):
        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&page=2&sort=name_asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 3)
        # Check active button 2
        self.assertContains(response, 'class="pagination-btn active">2</span>')
        self.assertContains(response, 'Product 13')
        self.assertNotContains(response, 'Product 00')

    def test_catalog_pagination_invalid_page(self):
        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&page=abc')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&page=999')
        self.assertEqual(response.status_code, 404)


class CatalogAndDashboardCustomizationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
        self.out_of_stock_product = Product.objects.create(
            name='AMD Ryzen Out of Stock',
            price=200.00,
            stock=0
        )
        self.out_of_stock_product.categories.add(self.category)
        
        self.in_stock_product = Product.objects.create(
            name='AMD Ryzen In Stock',
            price=220.00,
            stock=5
        )
        self.in_stock_product.categories.add(self.category)

        # Create manager user
        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        from django.contrib.auth.models import Permission
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label__in=['catalog', 'orders']))
        self.manager = User.objects.create_user(username='manager_cust', password='password123')
        self.manager.groups.add(self.manager_group)

    def test_out_of_stock_badge_in_catalog(self):
        response = self.client.get(reverse('catalog:product_list') + '?q=AMD+Ryzen+Out+of+Stock')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<span class="catalog-tag out-of-stock-tag">Esaurito</span>')
        
    def test_dashboard_sales_history_order_and_collapsed(self):
        self.client.login(username='manager_cust', password='password123')
        response = self.client.get(reverse('dashboard:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        
        # Check order: "History delle Vendite" is before "Gestione Prodotti"
        sales_index = content.find('<h2>History delle Vendite</h2>')
        products_index = content.find('<h2>Gestione Prodotti</h2>')
        
        self.assertNotEqual(sales_index, -1)
        self.assertNotEqual(products_index, -1)
        self.assertTrue(sales_index < products_index, "History delle Vendite should appear before Gestione Prodotti")
        
        # Check that details elements exist
        sales_details_pos = content.find('<details class="dashboard-section">')
        self.assertNotEqual(sales_details_pos, -1, "Sales history details element should be present")


class ProductConstraintTests(TestCase):
    def test_negative_price_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        product = Product(name="Negative Price CPU", price=-10.00, stock=5)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_stock_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        product = Product(name="Negative Stock CPU", price=10.00, stock=-5)
        with self.assertRaises(ValidationError):
            product.full_clean()

    def test_negative_price_database_constraint(self):
        from django.db import IntegrityError
        product = Product(name="Negative Price DB CPU", price=-10.00, stock=5)
        with self.assertRaises(IntegrityError):
            product.save()

    def test_negative_stock_database_constraint(self):
        from django.db import IntegrityError
        product = Product(name="Negative Stock DB CPU", price=10.00, stock=-5)
        with self.assertRaises(IntegrityError):
            product.save()


class OrderItemConstraintTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user_constraint', password='password123')
        self.category = Category.objects.create(name='Test Category Constraint')
        self.product = Product.objects.create(name='Test Product Constraint', price=10.00, stock=5)
        self.order = Order.objects.create(
            user=self.user,
            indirizzo='Test address',
            citta='Test city',
            codice_postale='12345',
            numero_di_telefono='1234567'
        )

    def test_negative_price_raises_validation_error(self):
        from django.core.exceptions import ValidationError
        order_item = OrderItem(order=self.order, product=self.product, price=-5.00, quantity=1)
        with self.assertRaises(ValidationError):
            order_item.full_clean()

    def test_negative_price_database_constraint(self):
        from django.db import IntegrityError
        order_item = OrderItem(order=self.order, product=self.product, price=-5.00, quantity=1)
        with self.assertRaises(IntegrityError):
            order_item.save()
