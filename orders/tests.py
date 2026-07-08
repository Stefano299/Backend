from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from catalog.models import Product, Category, Review
from orders.models import Order, OrderItem

User = get_user_model()

class ManagerDashboardTests(TestCase):
    def setUp(self):
        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        from django.contrib.auth.models import Permission
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label='catalog'))
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label='orders'))
        
        self.customer = User.objects.create_user(username='customer1', password='password123')
        
        self.manager = User.objects.create_user(username='manager1', password='password123')
        self.manager.groups.add(self.manager_group)
        
        self.staff_user = User.objects.create_user(username='staff1', password='password123', is_staff=True)
        view_product_perm = Permission.objects.get(codename='view_product', content_type__app_label='catalog')
        self.staff_user.user_permissions.add(view_product_perm)
        
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
        response = self.client.get(reverse('orders:manager_dashboard'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("orders:manager_dashboard")}')

    def test_customer_access_forbidden(self):
        self.client.login(username='customer1', password='password123')
        response = self.client.get(reverse('orders:manager_dashboard'))
        self.assertEqual(response.status_code, 403)

    def test_manager_access_granted(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.get(reverse('orders:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard Manager')

    def test_staff_access_granted(self):
        self.client.login(username='staff1', password='password123')
        response = self.client.get(reverse('orders:manager_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_product_create(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('catalog:product_create'), {
            'name': 'Intel i7',
            'description': 'Super CPU',
            'price': '350.00',
            'stock': 5,
            'image': '',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
        self.assertTrue(Product.objects.filter(name='Intel i7').exists())

    def test_product_update(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('catalog:product_update', args=[self.product.id]), {
            'name': 'AMD Ryzen 5 Updated',
            'price': '180.00',
            'stock': 8,
            'image': '',
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'AMD Ryzen 5 Updated')
        self.assertEqual(self.product.stock, 8)

    def test_product_delete(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('catalog:product_delete', args=[self.product.id]))
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())

    def test_category_create(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('catalog:category_create'), {
            'name': 'Schede Madri'
        })
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
        self.assertTrue(Category.objects.filter(name='Schede Madri').exists())

    def test_order_update(self):
        self.client.login(username='manager1', password='password123')
        response = self.client.post(reverse('orders:order_update', args=[self.order.id]), {
            'shipping_status': 'spedizione',
        })
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
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
        response = self.client.post(reverse('orders:cart_add', args=[self.product.id]), {
            'quantity': 1,
            'override': False
        })
        self.assertRedirects(response, reverse('orders:cart_detail'))
        
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5')
        
        self.product.delete()
        
        response = self.client.get(reverse('orders:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'AMD Ryzen 5')
        self.assertContains(response, 'Il tuo carrello è vuoto')


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
        self.assertEqual(response.status_code, 302)
        
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.first_name, 'NewFirst')
        self.assertEqual(self.customer.last_name, 'NewLast')
        self.assertEqual(self.customer.email, 'new@example.com')
        self.assertEqual(self.customer.indirizzo, 'Via Nuova 5')
        self.assertEqual(self.customer.citta, 'Torino')
        self.assertEqual(self.customer.codice_postale, '10100')
        self.assertEqual(self.customer.numero_di_telefono, '0987654321')

        order = Order.objects.filter(user=self.customer, payment_method='paypal').first()
        self.assertIsNotNone(order)
        self.assertEqual(order.first_name, 'NewFirst')
        self.assertEqual(order.last_name, 'NewLast')
        self.assertEqual(order.email, 'new@example.com')

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 9)


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

        self.manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        from django.contrib.auth.models import Permission
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label='catalog'))
        self.manager = User.objects.create_user(username='manager_cust', password='password123')
        self.manager.groups.add(self.manager_group)

    def test_out_of_stock_badge_in_catalog(self):
        response = self.client.get(reverse('catalog:product_list') + '?q=AMD+Ryzen+Out+of+Stock')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="badge-out-of-stock">Esaurito</div>')
        
    def test_dashboard_sales_history_order_and_collapsed(self):
        self.client.login(username='manager_cust', password='password123')
        response = self.client.get(reverse('orders:manager_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        content = response.content.decode('utf-8')
        
        sales_index = content.find('<h2>History delle Vendite</h2>')
        products_index = content.find('<h2>Gestione Prodotti</h2>')
        
        self.assertNotEqual(sales_index, -1)
        self.assertNotEqual(products_index, -1)
        self.assertTrue(sales_index < products_index)
        
        sales_details_pos = content.find('<details class="dashboard-section">')
        self.assertNotEqual(sales_details_pos, -1)
        
        products_details_pos = content.find('<details open class="dashboard-section">')
        self.assertNotEqual(products_details_pos, -1)


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
