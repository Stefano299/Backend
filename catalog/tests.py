from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from catalog.models import Product, Category, Review
from orders.models import Order, OrderItem

User = get_user_model()

class ReviewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Processori')
        self.product = Product.objects.create(
            name='AMD Ryzen 5',
            price=200.00,
            stock=10
        )
        self.product.categories.add(self.category)
        self.buyer = User.objects.create_user(username='buyer1', password='password123')
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
        
        response = self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 4,
            'comment': 'Un altro commento'
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Review.objects.filter(product=self.product, user=self.buyer).count(), 1)

    def test_invalid_review_submission(self):
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
            'rating': 10,
            'comment': 'Fantastico!'
        })
        self.assertRedirects(response, reverse('catalog:product_detail', args=[self.product.id]))
        self.assertFalse(Review.objects.filter(product=self.product).exists())

    def test_review_ui_visibility_anonymous(self):
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Accedi per lasciare una recensione.')
        self.assertNotContains(response, 'Lascia una recensione')

    def test_review_ui_visibility_buyer_before_and_after_purchase(self):
        self.client.login(username='buyer1', password='password123')
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Devi aver acquistato questo prodotto per poter lasciare una recensione.')
        self.assertNotContains(response, 'Lascia una recensione')
        
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
        
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Lascia una recensione')
        self.assertNotContains(response, 'Devi aver acquistato questo prodotto')
        
        self.client.post(reverse('catalog:add_review', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Recensione di prova'
        })
        
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Hai già recensito questo prodotto.')
        self.assertNotContains(response, 'Lascia una recensione')

    def test_manager_can_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment='Bella!')
        manager_group, _ = Group.objects.get_or_create(name='Store Manager')
        from django.contrib.auth.models import Permission
        manager_group.permissions.add(*Permission.objects.filter(content_type__app_label='catalog'))
        manager = User.objects.create_user(username='manager_review', password='password123')
        manager.groups.add(manager_group)
        
        self.client.login(username='manager_review', password='password123')
        response = self.client.post(reverse('catalog:review_delete', args=[review.id]))
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
        self.assertFalse(Review.objects.filter(id=review.id).exists())

    def test_buyer_cannot_delete_review(self):
        review = Review.objects.create(product=self.product, user=self.buyer, rating=5, comment='Bella!')
        self.client.login(username='buyer1', password='password123')
        response = self.client.post(reverse('catalog:review_delete', args=[review.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Review.objects.filter(id=review.id).exists())

    def test_average_rating_display(self):
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'Ancora nessuna recensione')
        
        Review.objects.create(product=self.product, user=self.buyer, rating=4, comment='Molto buono')
        other_buyer = User.objects.create_user(username='other_buyer', password='password123')
        Review.objects.create(product=self.product, user=other_buyer, rating=5, comment='Eccellente')
        
        response = self.client.get(reverse('catalog:product_detail', args=[self.product.id]))
        self.assertContains(response, 'star-icon filled')


class PCBuilderTests(TestCase):
    def setUp(self):
        self.cpu_cat, _ = Category.objects.get_or_create(name='Processore')
        self.cooler_cat, _ = Category.objects.get_or_create(name='Dissipatore')
        self.mobo_cat, _ = Category.objects.get_or_create(name='Scheda Madre')
        self.ram_cat, _ = Category.objects.get_or_create(name='Memoria RAM')
        self.gpu_cat, _ = Category.objects.get_or_create(name='Scheda Video')
        self.storage_cat, _ = Category.objects.get_or_create(name='Storage')
        self.psu_cat, _ = Category.objects.get_or_create(name='Alimentatore')
        self.case_cat, _ = Category.objects.get_or_create(name='Case')

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
        response = self.client.get(reverse('catalog:pc_builder_step', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'Intel Core i5-13400')

        response = self.client.post(reverse('catalog:pc_builder_step', args=[1]), {'product_id': self.cpu_amd.id})
        self.assertRedirects(response, reverse('catalog:pc_builder_step', args=[2]))
        self.assertEqual(self.client.session.get('pc_build_step_1'), str(self.cpu_amd.id))

    def test_compatibility_filtering(self):
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_amd.id)
        session.save()

        response = self.client.get(reverse('catalog:pc_builder_step', args=[3]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ASUS Prime B650')
        self.assertNotContains(response, 'ASUS Prime B760')

        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_intel.id)
        session.save()

        response = self.client.get(reverse('catalog:pc_builder_step', args=[3]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'ASUS Prime B760')
        self.assertNotContains(response, 'ASUS Prime B650')

    def test_summary_and_add_to_cart(self):
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

        response = self.client.get(reverse('catalog:pc_builder_summary'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'ASUS Prime B650')
        self.assertContains(response, 'Corsair 4000D')

        response = self.client.post(reverse('catalog:pc_builder_summary'))
        self.assertRedirects(response, reverse('orders:cart_detail'))

        response = self.client.get(reverse('orders:cart_detail'))
        self.assertContains(response, 'AMD Ryzen 5 7600')
        self.assertContains(response, 'ASUS Prime B650')
        self.assertContains(response, 'Corsair 4000D')

        for i in range(1, 9):
            self.assertIsNone(self.client.session.get(f'pc_build_step_{i}'))

    def test_clear_builder(self):
        session = self.client.session
        session['pc_build_step_1'] = str(self.cpu_amd.id)
        session['pc_build_step_2'] = str(self.cooler.id)
        session.save()

        response = self.client.get(reverse('catalog:pc_builder_clear'))
        self.assertRedirects(response, reverse('catalog:pc_builder_step', args=[1]))

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
        self.manager_group.permissions.add(*Permission.objects.filter(content_type__app_label='catalog'))
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
        
        response = self.client.post(reverse('catalog:product_create'), {
            'name': 'Intel Core i9',
            'description': 'Powerful CPU',
            'price': '600.00',
            'stock': 3,
            'image': uploaded_image,
            'categories': [self.category.id]
        })
        self.assertRedirects(response, reverse('orders:manager_dashboard'))
        
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


class CatalogPaginationTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Test Category')
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
        self.assertContains(response, 'class="pagination-btn active">1</span>')
        self.assertContains(response, 'Product 00')
        self.assertNotContains(response, 'Product 13')

    def test_catalog_pagination_second_page(self):
        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&page=2&sort=name_asc')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 3)
        self.assertContains(response, 'class="pagination-btn active">2</span>')
        self.assertContains(response, 'Product 13')
        self.assertNotContains(response, 'Product 00')

    def test_catalog_pagination_invalid_page(self):
        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&page=abc')
        self.assertEqual(response.status_code, 404)

        response = self.client.get(reverse('catalog:product_list') + f'?categories={self.category.id}&page=999')
        self.assertEqual(response.status_code, 404)


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
