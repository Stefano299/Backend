from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from shop.models import Product, Category, Order

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
