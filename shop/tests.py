from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from shop.models import Product, Category, Order, OrderItem, Review

User = get_user_model()

class ManagerDashboardTests(TestCase):
    def setUp(self):
        # Create groups
        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        
        # Create users
        self.customer = User.objects.create_user(username='customer1', password='password123')
        
        self.manager = User.objects.create_user(username='manager1', password='password123')
        self.manager.groups.add(self.manager_group)
        
        self.staff_user = User.objects.create_user(username='staff1', password='password123', is_staff=True)
        
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
        response = self.client.get(reverse('shop:manager_dashboard'))
        # Should redirect to login since it has LoginRequiredMixin
        self.assertRedirects(response, f'/accounts/login/?next={reverse("shop:manager_dashboard")}')

    def test_customer_access_forbidden(self):
        self.client.login(username='customer1', password='password123')
        response = self.client.get(reverse('shop:manager_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_manager_access_granted(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.get(reverse('shop:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Manager')

    def test_staff_access_granted(self):
        self.client.login(username='staff1', password='password123')
        response = self.client.get(reverse('shop:manager_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_product_create(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('shop:product_create'), {
            'name': 'Intel i7',
            'description': 'Super CPU',
            'price': '350.00',
            'stock': 5,
            'image': '',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.assertTrue(Product.objects.filter(name='Intel i7').exists())

    def test_product_update(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('shop:product_update', args=[self.product.id]), {
            'name': 'AMD Ryzen 5 Updated',
            'price': '180.00',
            'stock': 8,
            'image': '',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'AMD Ryzen 5 Updated')
        self.assertEqual(self.product.stock, 8)

    def test_product_delete(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('shop:product_delete', args=[self.product.id]))
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_category_create(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('shop:category_create'), {
            'name': 'Schede Madri'
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.assertTrue(Category.objects.filter(name='Schede Madri').exists())

    def test_order_update(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('shop:order_update', args=[self.order.id]), {
            'shipping_status': 'spedizione',
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
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
        response = self.client.post(reverse('shop:cart_add', args=[self.product.id]), {
            'quantity': 1,
            'override': False
        })
        self.assertRedirects(response, reverse('shop:cart_detail'))
        
        # Verifica che il prodotto sia mostrato nel carrello
        response = self.client.get(reverse('shop:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5')
        
        # Elimina il prodotto dal database
        self.product.delete()
        
        # Riapri il carrello: deve caricare correttamente e rimuovere il prodotto orfano senza NoReverseMatch
        response = self.client.get(reverse('shop:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'AMD Ryzen 5')
        
        # Il carrello deve risultare vuoto
        self.assertContains(response, 'Il tuo carrello è vuoto')


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
        response = self.client.post(reverse('shop:add_review', args=[self.product.id]), {
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
        response = self.client.post(reverse('shop:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Ottimo processore!'
        })
        self.assertRedirects(response, reverse('shop:product_detail', args=[self.product.id]))
        self.assertTrue(Review.objects.filter(product=self.product, user=self.buyer).exists())
        
        # Prova a inserire una seconda recensione sullo stesso prodotto: deve dare 403
        response = self.client.post(reverse('shop:add_review', args=[self.product.id]), {
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
        response = self.client.post(reverse('shop:add_review', args=[self.product.id]), {
            'rating': 10,
            'comment': 'Fantastico!'
        })
        # Dovrebbe reindirizzare indietro senza salvare nulla nel database
        self.assertRedirects(response, reverse('shop:product_detail', args=[self.product.id]))
        self.assertFalse(Review.objects.filter(product=self.product).exists())

    def test_review_ui_visibility_anonymous(self):
        # Utente anonimo non deve vedere il form ma il messaggio per accedere
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Accedi per lasciare una recensione.')
        self.assertNotContains(response, 'Lascia una recensione')

    def test_review_ui_visibility_buyer_before_and_after_purchase(self):
        # Prima dell'acquisto
        self.client.login(username='buyer1', password='password123')
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id]))
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
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Lascia una recensione')
        self.assertNotContains(response, 'Devi aver acquistato questo prodotto')
        
        # Invia la recensione
        self.client.post(reverse('shop:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Recensione di prova'
        })
        
        # Dopo aver recensito
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Hai già recensito questo prodotto.')
        self.assertNotContains(response, 'Lascia una recensione')

    def test_manager_can_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment='Bella!')
        from django.contrib.auth.models import Group
        manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        manager = User.objects.create_user(username='manager_review', password='password123')
        manager.groups.add(manager_group)
        
        self.client.login(username='manager_review', password='password123')
        response = self.client.post(reverse('shop:review_delete', args=[review.id]))
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_buyer_cannot_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment='Bella!')
        self.client.login(username='buyer1', password='password123')
        response = self.client.post(reverse('shop:review_delete', args=[review.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_average_rating_display(self):
        # Prima di recensioni, il rating deve essere "Ancora nessuna recensione"
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Ancora nessuna recensione')
        
        # Aggiungiamo due recensioni
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment='Molto buono')
        other_buyer = User.objects.create_user(username='other_buyer', password='password123')
        Review.objects.create(product=self.product, user=other_buyer, rating=5, comment='Eccellente')
        
        # Media deve essere 4.5 su 5
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id]))
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
        response = self.client.get(reverse('shop:pc_builder_step', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'Intel Core i5-13400')

        # Seleziona la CPU AMD inviando il form via POST
        response = self.client.post(reverse('shop:pc_builder_step', args=[1]), {'product_id': self.cpu_amd.id})
        # Dovrebbe reindirizzare allo step successivo (Step 2)
        self.assertRedirects(response, reverse('shop:pc_builder_step', args=[2]))
        # Controlla che sia stato salvato in sessione
        self.assertEqual(self.client.session.get('pc_build_step_1'), str(self.cpu_amd.id))

    def test_compatibility_filtering(self):
        # Imposta in sessione la scelta di una CPU AMD al passo 1
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_amd.id)
        session.save()

        # Visita il passo 3 (Scheda Madre)
        response = self.client.get(reverse('shop:pc_builder_step', args=[3]))
        self.assertEqual(response.status_code, 200)
        # Dovrebbe contenere solo la scheda madre compatibile AMD AM5
        self.assertContains(response, 'ASUS Prime B650')
        self.assertNotContains(response, 'ASUS Prime B760')

        # Cambiamo la CPU in Intel
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_intel.id)
        session.save()

        response = self.client.get(reverse('shop:pc_builder_step', args=[3]))
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
        response = self.client.get(reverse('shop:pc_builder_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'ASUS Prime B650')
        self.assertContains(response, 'Corsair 4000D')
        self.assertNotContains(response, 'La configurazione è incompleta')

        # Invia la conferma del riepilogo via POST per aggiungere al carrello
        response = self.client.post(reverse('shop:pc_builder_summary'))
        # Dovrebbe reindirizzare alla pagina di dettaglio del carrello
        self.assertRedirects(response, reverse('shop:cart_detail'))

        # Controlla che i componenti siano nel carrello
        response = self.client.get(reverse('shop:cart_detail'))
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
        response = self.client.get(reverse('shop:pc_builder_clear'))
        self.assertRedirects(response, reverse('shop:pc_builder_step', args=[1]))

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
        
        response = self.client.post(reverse('shop:product_create'), {
            'name': 'Intel Core i9',
            'description': 'Powerful CPU',
            'price': '600.00',
            'stock': 3,
            'image': uploaded_image,
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        
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


