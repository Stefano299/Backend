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
            'image_url': 'http://example.com/img.jpg',
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
            'image_url': self.product.image_url,
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


class SellerRoleTests(TestCase):
    def setUp(self):
        # Recupera o crea i gruppi
        self.seller_group, _ = Group.objects.get_or_create(name='Seller')
        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        
        # Crea utenti
        self.seller = User.objects.create_user(username='seller1', password='password123')
        self.seller.groups.add(self.seller_group)
        
        self.other_seller = User.objects.create_user(username='seller2', password='password123')
        self.other_seller.groups.add(self.seller_group)
        
        self.manager = User.objects.create_user(username='manager1', password='password123')
        self.manager.groups.add(self.manager_group)
        
        # Crea dati di test
        self.category = Category.objects.create(name='Memorie')
        
        # Prodotto venditore 1
        self.product_own = Product.objects.create(
            name='Corsair Vengeance',
            price=80.00,
            stock=15,
            seller=self.seller
        )
        # Prodotto venditore 2
        self.product_other = Product.objects.create(
            name='G.Skill Trident',
            price=120.00,
            stock=5,
            seller=self.other_seller
        )
        
    def test_seller_dashboard_access(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.get(reverse('shop:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Venditore')
        # Deve contenere il proprio prodotto ma non quello dell'altro venditore
        self.assertContains(response, 'Corsair Vengeance')
        self.assertNotContains(response, 'G.Skill Trident')
        
    def test_seller_can_create_product(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('shop:product_create'), {
            'name': 'Kingston Fury',
            'description': 'RAM',
            'price': '90.00',
            'stock': 12,
            'image_url': 'http://example.com/ram.jpg',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        prod = Product.objects.get(name='Kingston Fury')
        self.assertEqual(prod.seller, self.seller)

    def test_seller_can_update_own_product(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('shop:product_update', args=[self.product_own.id]), {
            'name': 'Corsair Vengeance Updated',
            'price': '85.00',
            'stock': 10,
            'image_url': self.product_own.image_url,
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.product_own.refresh_from_db()
        self.assertEqual(self.product_own.name, 'Corsair Vengeance Updated')

    def test_seller_cannot_update_other_product(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('shop:product_update', args=[self.product_other.id]), {
            'name': 'G.Skill Trident Hacked',
            'price': '10.00',
            'stock': 99,
            'image_url': self.product_other.image_url,
            'categories': [self.category.id]
        })
        self.assertEqual(response.status_code, 403)
        self.product_other.refresh_from_db()
        self.assertNotEqual(self.product_other.name, 'G.Skill Trident Hacked')

    def test_seller_cannot_delete_other_product(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('shop:product_delete', args=[self.product_other.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Product.objects.filter(id=self.product_other.id).exists())

    def test_seller_cannot_create_category(self):
        self.client.login(username='seller1', password='password123')
        response = self.client.post(reverse('shop:category_create'), {'name': 'Alimentatori'})
        self.assertEqual(response.status_code, 403)
        
    def test_manager_can_update_any_product(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('shop:product_update', args=[self.product_own.id]), {
            'name': 'Corsair Vengeance Hacked By Manager',
            'price': '85.00',
            'stock': 10,
            'image_url': self.product_own.image_url,
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.product_own.refresh_from_db()
        self.assertEqual(self.product_own.name, 'Corsair Vengeance Hacked By Manager')


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

class SellerWalletAndAverageRatingTests(TestCase):
    def setUp(self):
        self.seller_group, _ = Group.objects.get_or_create(name='Seller')
        
        # Create seller
        self.seller = User.objects.create_user(username='seller_wallet', password='password123')
        self.seller.groups.add(self.seller_group)
        
        # Create buyer
        self.buyer = User.objects.create_user(username='buyer_wallet', password='password123')
        
        # Create seller's product
        self.product = Product.objects.create(
            name='GPU GeForce RTX',
            price=500.00,
            stock=5,
            seller=self.seller
        )
        
    def test_wallet_earning_on_purchase(self):
        # Initial wallet check
        self.assertEqual(self.seller.wallet_balance, 0.00)
        
        # Simula il checkout inserendo un ordine e un articolo nel carrello
        self.client.login(username='buyer_wallet', password='password123')
        
        # Inserisci nel carrello
        self.client.post(reverse('shop:cart_add', args=[self.product.id]), {'quantity': 2, 'override': False})
        
        # Esegui il checkout
        response = self.client.post(reverse('shop:checkout'), {
            'indirizzo': 'Via Roma 1',
            'citta': 'Milano',
            'codice_postale': '20100',
            'numero_di_telefono': '123456789',
            'payment_method': 'card'
        })
        self.assertEqual(response.status_code, 302)
        
        # Ricarica il venditore dal database
        self.seller.refresh_from_db()
        # Il saldo dovrebbe essere 2 * 500.00 = 1000.00
        self.assertEqual(self.seller.wallet_balance, 1000.00)
        
    def test_wallet_transfer_funds(self):
        self.seller.wallet_balance = 500.00
        self.seller.save()
        
        self.client.login(username='seller_wallet', password='password123')
        
        # Trasferimento valido
        response = self.client.post(reverse('shop:transfer_wallet'), {'amount': '200.00'})
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.wallet_balance, 300.00)
        
        # Trasferimento non valido (fondi insufficienti)
        response = self.client.post(reverse('shop:transfer_wallet'), {'amount': '400.00'})
        self.assertRedirects(response, reverse('shop:manager_dashboard'))
        self.seller.refresh_from_db()
        self.assertEqual(self.seller.wallet_balance, 300.00)
        
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
