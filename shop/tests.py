from uuid import uuid4
from django.forms import ValidationError
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from shop.models import Street, Category, Product, ProductInCart, Order, ProductInOrder, UsersProducts
from django.urls import reverse
from decimal import Decimal
from django.db import IntegrityError
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()


class StreetModelTest(TestCase):
    def setUp(self):
        self.street = Street.objects.create(name='Ленина')

    def test_street_creation(self):
        self.assertEqual(self.street.name, 'Ленина')
        self.assertIsInstance(self.street.id, type(self.street.id)) 
        self.assertTrue(Street.objects.filter(name='Ленина').exists())

    def test_street_str(self):
        self.assertEqual(str(self.street), 'Ленина')

    def test_street_unique_name(self):
        with self.assertRaises(IntegrityError):
            Street.objects.create(name='Ленина')


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Смартфоны')

    def test_category_creation(self):
        self.assertEqual(self.category.name, 'Смартфоны')
        self.assertIsNotNone(self.category.slug)
        self.assertTrue(Category.objects.filter(name='Смартфоны').exists())

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Смартфоны')

    def test_category_slug_auto_created(self):
       
        self.assertEqual(self.category.slug, 'smartfonyi')

    def test_get_absolute_url(self):
        expected_url = reverse('shop:product_list_by_category', args=[self.category.slug])
        self.assertEqual(self.category.get_absolute_url(), expected_url)


class ProductModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Ноутбуки')
        self.product = Product.objects.create(
            category=self.category,
            name='MacBook Air M2',
            description='Ультрабук от Apple',
            price=Decimal('1399.99'),
            count=10
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'MacBook Air M2')
        self.assertEqual(self.product.category.name, 'Ноутбуки')
        self.assertEqual(self.product.price, Decimal('1399.99'))
        self.assertEqual(self.product.count, 10)
        self.assertIsNotNone(self.product.slug)

    def test_product_str(self):
        self.assertEqual(str(self.product), 'MacBook Air M2')

    def test_get_absolute_url(self):
        expected_url = reverse('shop:product_detail', args=[self.product.slug])
        self.assertEqual(self.product.get_absolute_url(), expected_url)

    def test_get_average_rating_url_no_feedback(self):
        url = self.product.get_average_rating_url()
        self.assertEqual(url, 'images/rating/0.png')

    def test_get_average_rating_url_half_star(self):
        UsersProducts.objects.create(
            user = self.user,
            product=self.product,
            rating=3
        )

        UsersProducts.objects.create(user =self.user, product=self.product, rating=4)

        url = self.product.get_average_rating_url()
        self.assertEqual(url, 'images/rating/3.5.png')


class ProductInCartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.category = Category.objects.create(name='Смартфоны')
        self.product = Product.objects.create(
            category=self.category,
            name='iPhone 15',
            price=Decimal('999.99'),
            count=5,
        )
        self.cart_item = ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=2
        )

    def test_cart_item_created(self):
        self.assertEqual(self.cart_item.user, self.user)
        self.assertEqual(self.cart_item.product, self.product)
        self.assertEqual(self.cart_item.price, Decimal('999.99'))
        self.assertEqual(self.cart_item.count, 2)

    def test_get_cost(self):
        expected_cost = Decimal('999.99') * 2
        self.assertEqual(self.cart_item.get_cost(), expected_cost)

    def test_str(self):
        self.assertEqual(str(self.cart_item), str(self.product))


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.street = Street.objects.create(name='Ленина')

    def test_order_creation_with_apartment(self):
        order = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=False,
            building='10A',
            apartment='15',
            price=Decimal('1000.00'),
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.street, self.street)
        self.assertEqual(order.building, '10A')
        self.assertEqual(order.apartment, '15')
        self.assertFalse(order.is_private)
        self.assertEqual(order.price, Decimal('1000.00'))
        self.assertFalse(order.is_delivered)

    def test_order_creation_private_house(self):
        order = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=True,
            building='25B',
            apartment=None,
            price=Decimal('500.00'),
        )
        self.assertIsNone(order.apartment)
        self.assertTrue(order.is_private)

    def test_str_representation(self):
        order = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=True,
            building='5',
            price=Decimal('150.00'),
        )
        self.assertEqual(str(order), str(order.id))

    def test_is_delivered_toggle(self):
        order = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=False,
            building='77',
            apartment='2',
            price=Decimal('200.00'),
        )
        self.assertFalse(order.is_delivered)
        order.is_delivered = True
        order.save()
        order.refresh_from_db()
        self.assertTrue(order.is_delivered)


class ProductInOrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass')
        self.category = Category.objects.create(name='Молочные продукты')
        self.product = Product.objects.create(
            category=self.category,
            name='Молоко',
            price=Decimal('60.00'),
            count=50
        )
        self.street = Street.objects.create(name='Тестовая улица')
        self.order = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=False,
            building='12',
            apartment='34',
            price=Decimal('120.00')
        )

    def test_product_in_order_creation(self):
        pio = ProductInOrder.objects.create(
            product=self.product,
            order=self.order,
            price=self.product.price,
            count=2
        )
        self.assertEqual(pio.product, self.product)
        self.assertEqual(pio.order, self.order)
        self.assertEqual(pio.price, Decimal('60.00'))
        self.assertEqual(pio.count, 2)

    def test_str_representation(self):
        pio = ProductInOrder.objects.create(
            product=self.product,
            order=self.order,
            price=self.product.price,
            count=1
        )
        self.assertEqual(str(pio), str(self.product))


class UsersProductsModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='feedback_user', password='testpass')
        self.category = Category.objects.create(name='Овощи')
        self.product = Product.objects.create(
            category=self.category,
            name='Морковь',
            price=Decimal('25.50'),
            count=100
        )

    def test_create_feedback_with_rating_and_review(self):
        feedback = UsersProducts.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            review="Хорошая морковь, свежая."
        )
        self.assertEqual(feedback.rating, 4)
        self.assertEqual(feedback.review, "Хорошая морковь, свежая.")
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.product, self.product)

    def test_rating_validation(self):
        feedback = UsersProducts(
            user=self.user,
            product=self.product,
            rating=6, 
            review="Слишком хороша, чтобы быть правдой."
        )
        with self.assertRaises(ValidationError):
            feedback.full_clean()

    def test_rating_lower_bound_validation(self):
        feedback = UsersProducts(
            user=self.user,
            product=self.product,
            rating=-1,
            review="Отвратительно."
        )
        with self.assertRaises(ValidationError):
            feedback.full_clean()

    def test_create_feedback_without_review(self):
        feedback = UsersProducts.objects.create(
            user=self.user,
            product=self.product,
            rating=3,
            review=None
        )
        self.assertIsNone(feedback.review)
        self.assertEqual(feedback.rating, 3)


class ProductListViewTest(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='Фрукты')
        self.category2 = Category.objects.create(name='Овощи')

        self.product1 = Product.objects.create(
            category=self.category1,
            name='Яблоко',
            price=Decimal('10.00'),
            count=5,
        )
        self.product2 = Product.objects.create(
            category=self.category2,
            name='Морковь',
            price=Decimal('5.00'),
            count=3,
        )

    def test_all_products_list_view(self):
        url = reverse('shop:product_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
        self.assertIn(self.product1, response.context['products'])
        self.assertIn(self.product2, response.context['products'])

    def test_category_filtered_product_list_view(self):
        url = reverse('shop:product_list_by_category', args=[self.category1.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_list.html')
        self.assertIn(self.product1, response.context['products'])
        self.assertNotIn(self.product2, response.context['products'])
        self.assertEqual(response.context['category'], self.category1)


class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.category = Category.objects.create(name='Напитки')
        self.product = Product.objects.create(
            category=self.category,
            name='Сок',
            price=Decimal('3.99'),
            count=10,
        )

    def test_product_detail_view_as_anonymous(self):
        url = reverse('shop:product_detail', args=[self.product.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product_detail.html')
        self.assertEqual(response.context['product'], self.product)
        self.assertFalse(response.context['is_product_in_cart'])

    def test_product_detail_view_authenticated_without_cart_item(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('shop:product_detail', args=[self.product.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_product_in_cart'])

    def test_product_detail_view_authenticated_with_cart_item(self):
        ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=1
        )
        self.client.login(username='testuser', password='testpass123')
        url = reverse('shop:product_detail', args=[self.product.slug])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_product_in_cart'])


class CartViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            account=Decimal('100.00'),
        )
        self.category = Category.objects.create(name =  'testcategory')
        self.product = Product.objects.create(

            name='Тестовый товар',
            price=Decimal('25.00'),
            count=10,
            slug='test-product',
            category = self.category,
        )
        ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=2
        )

    def test_cart_view_requires_login(self):
        url = reverse('shop:cart')
        response = self.client.get(url)
        expected_login_url = reverse('account:login') + f'?next={url}'
        self.assertRedirects(response, expected_login_url)

    def test_cart_view_returns_correct_context_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('shop:cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart.html')

        cart = response.context['cart']
        total = response.context['total']

        self.assertEqual(len(cart), 1)
        self.assertEqual(cart[0].product.name, 'Тестовый товар')
        self.assertEqual(total, Decimal('50.00'))

        self.assertEqual(response.context['site_section'], 'cart')
        self.assertIn('form', response.context)


class CartAddProductViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123',email='testemail')
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Test Category', slug='test-category')
        self.product = Product.objects.create(
            name='Test Product',
            count = 12,
            slug='test-product',
            category=self.category,
            price=100.00,
        )

    def test_cart_add_product_view_adds_product(self):
        url = reverse('shop:cart_add', args=[self.product.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ProductInCart.objects.filter(user=self.user, product=self.product).exists())

    def test_redirects_to_cart_after_add(self):
        url = reverse('shop:cart_add', args=[self.product.id])
        response = self.client.get(url)
        self.assertRedirects(response, reverse('shop:cart'))


class CartDeleteProductViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Test Category', slug='test-category')

        self.image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xFF\xFF\xFF!\xF9\x04',
            content_type='image/gif'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=100.00,
            count=10,
            image=self.image,
        )

        self.product_in_cart = ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            count = 2,
            price = 200,
        )

    def test_cart_delete_product_view(self):
        url = reverse('shop:cart_delete', args=[str(self.product_in_cart.id)])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:cart'))

        self.assertFalse(ProductInCart.objects.filter(id=self.product_in_cart.id).exists())


class CartIncrementViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', account=1000)
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Test Category')

        self.product = Product.objects.create(
            id=uuid4(),
            name='Test Product',
            category=self.category,
            price=Decimal('20.00'),
            count=5,  # на складе 5
        )

        self.cart_item = ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=1,
        )

    def test_increment_success(self):
        original_product_count = self.product.count
        original_cart_count = self.cart_item.count

        url = reverse('shop:cart_increment', args=[self.cart_item.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:cart'))

        self.product.refresh_from_db()
        self.cart_item.refresh_from_db()

        self.assertEqual(self.cart_item.count, original_cart_count + 1)
        self.assertEqual(self.product.count, original_product_count - 1)

    def test_increment_blocked_if_no_stock(self):
        self.product.count = 0
        self.product.save()

        url = reverse('shop:cart_increment', args=[self.cart_item.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:cart'))

        self.cart_item.refresh_from_db()
        self.assertEqual(self.cart_item.count, 1)


class CartDecrementViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', account=1000)
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Test Category')

        self.product = Product.objects.create(
            id=uuid4(),
            name='Test Product',
            category=self.category,
            price=Decimal('15.00'),
            count=3,  # на складе
        )

        self.cart_item = ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=2,  # в корзине 2
        )

    def test_decrement_success(self):
        original_product_count = self.product.count
        original_cart_count = self.cart_item.count

        url = reverse('shop:cart_decrement', args=[self.cart_item.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:cart'))

        self.product.refresh_from_db()
        self.cart_item.refresh_from_db()

        self.assertEqual(self.cart_item.count, original_cart_count - 1)
        self.assertEqual(self.product.count, original_product_count + 1)

    def test_decrement_blocked_if_count_is_1(self):
        self.cart_item.count = 1
        self.cart_item.save()
        original_product_count = self.product.count

        url = reverse('shop:cart_decrement', args=[self.cart_item.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('shop:cart'))

        self.cart_item.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(self.cart_item.count, 1)
        self.assertEqual(self.product.count, original_product_count)


class OrderCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', account=Decimal('1000.00'))
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('100.00'),
            count=10,
        )

        self.cart_item = ProductInCart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=2,
        )

        self.street = Street.objects.create(name='Main Street')

        self.valid_form_data = {
            'street': self.street.id,
            'is_private': False,
            'building': '123',
            'apartment': '45',
        }

    def test_order_created_successfully(self):
        url = reverse('shop:order_create')
        response = self.client.post(url, data=self.valid_form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_done.html')

        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.street, self.street)
        self.assertEqual(order.price, Decimal('200.00'))

        self.assertEqual(ProductInOrder.objects.count(), 1)
        product_in_order = ProductInOrder.objects.first()
        self.assertEqual(product_in_order.count, 2)

        self.assertEqual(ProductInCart.objects.filter(user=self.user).count(), 0)

        self.user.refresh_from_db()
        self.assertEqual(self.user.account, Decimal('800.00'))

    def test_order_not_created_if_balance_too_low(self):
        self.user.account = Decimal('100.00') 
        self.user.save()

        response = self.client.post(reverse('shop:order_create'), data=self.valid_form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/low_balance.html')
        self.assertEqual(Order.objects.count(), 0)

    def test_order_not_created_if_cart_empty(self):
        ProductInCart.objects.all().delete()

        response = self.client.post(reverse('shop:order_create'), data=self.valid_form_data)
        self.assertRedirects(response, reverse('shop:cart'))
        self.assertEqual(Order.objects.count(), 0)


class OrderListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

        self.other_user = User.objects.create_user(username='otheruser', password='pass' ,email='useremail')

        self.street = Street.objects.create(name='Main Street')

        self.order1 = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=False,
            building='10',
            apartment='5',
            price=100,
            is_delivered=False,
        )
        self.order2 = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=False,
            building='20',
            apartment='8',
            price=150,
            is_delivered=True,
        )

        self.order3 = Order.objects.create(
            user=self.other_user,
            street=self.street,
            is_private=True,
            building='99',
            apartment='',
            price=200,
            is_delivered=False,
        )

    def test_order_list_view_returns_only_undelivered_orders_for_user(self):
        url = reverse('shop:order_list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_list.html')

        orders = response.context['orders']
        self.assertEqual(len(orders), 1)
        self.assertIn(self.order1, orders)
        self.assertNotIn(self.order2, orders)
        self.assertNotIn(self.order3, orders)


class OrderRecievedViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123',email='testemail')
        self.client.login(username='testuser', password='testpass123')

        self.category = Category.objects.create(name='Test Category')
        self.street = Street.objects.create(name='Main Street')
        self.product = Product.objects.create(
            category=self.category,
            name='Test Product',
            price=Decimal('10.00'),
            count=5
        )

        self.order = Order.objects.create(
            user=self.user,
            street=self.street,
            is_private=False,
            building='12',
            apartment='34',
            price=Decimal('10.00')
        )

        self.product_in_order = ProductInOrder.objects.create(
            product=self.product,
            price=Decimal('10.00'),
            order=self.order,
            count=1
        )

    def test_get_order_recieved_view_marks_order_as_delivered(self):
        url = reverse('shop:order_recieved', args=[self.order.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_recieved.html')

        self.order.refresh_from_db()
        self.assertTrue(self.order.is_delivered)

    def test_post_valid_feedback_creates_feedback_and_deletes_productinorder(self):
        url = reverse('shop:order_recieved', args=[self.order.id])
        data = {
            'rating': 4,
            'review': 'Great product!',
            'product_id': str(self.product.id),
        }

        response = self.client.post(url, data)

        feedback = UsersProducts.objects.filter(user=self.user, product=self.product).first()
        self.assertIsNotNone(feedback)
        self.assertEqual(feedback.rating, 4)
        self.assertEqual(feedback.review, 'Great product!')

      
        self.assertFalse(
            ProductInOrder.objects.filter(order=self.order, product=self.product).exists()
        )

       
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_recieved.html')

    def test_post_invalid_product_redirects(self):
        other_product = Product.objects.create(
            category=self.category,
            name='Another Product',
            price=Decimal('15.00'),
            count=3
        )

        url = reverse('shop:order_recieved', args=[self.order.id])
        data = {
            'rating': 5,
            'review': 'Should fail',
            'product_id': str(other_product.id),
        }

        response = self.client.post(url, data)

        self.assertRedirects(response, reverse('shop:order_list'))

        self.assertFalse(
            UsersProducts.objects.filter(user=self.user, product=other_product).exists()
        )


class ReviewDeleteViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', email='reviewer@example.com', password='testpass')
        self.other_user = User.objects.create_user(username='otheruser', email='other@example.com', password='testpass')

        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=Decimal('9.99'),
            count=10
        )

        self.review = UsersProducts.objects.create(
            user=self.user,
            product=self.product,
            rating=4,
            review='Nice one'
        )

    def test_user_can_delete_own_review(self):
        self.client.login(username='reviewer', password='testpass')
        url = reverse('shop:review_delete', args=[self.review.id])
        response = self.client.post(url)

        expected_redirect = reverse('shop:product_detail', args=[self.product.slug])
        self.assertRedirects(response, expected_redirect)

        self.assertFalse(UsersProducts.objects.filter(id=self.review.id).exists())

    def test_user_cannot_delete_others_review(self):
        self.client.login(username='otheruser', password='testpass')
        url = reverse('shop:review_delete', args=[self.review.id])
        response = self.client.post(url)

        self.assertNotEqual(response.status_code, 200)
        self.assertTrue(UsersProducts.objects.filter(id=self.review.id).exists())









