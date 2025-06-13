from unittest import mock
from unittest.mock import patch
from uuid import uuid4
from django.forms import ValidationError
from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from shop.forms import OrderForm
from shop.models import Street, Category, Product, Cart, Order, ProductInOrder, Feedback
from django.urls import reverse
from decimal import Decimal
from django.db import IntegrityError
from django.utils.http import urlencode


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
        self.user = User.objects.create_user(username='testuser', password='testpass',email='testemail')
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
        Feedback.objects.create(
            user = self.user,
            product=self.product,
            rating=3
        )

        Feedback.objects.create(user =self.user, product=self.product, rating=4)

        url = self.product.get_average_rating_url()
        self.assertEqual(url, 'images/rating/3.5.png')


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass',email='testemail')
        self.category = Category.objects.create(name='Смартфоны')
        self.product = Product.objects.create(
            category=self.category,
            name='iPhone 15',
            price=Decimal('999.99'),
            count=5,
        )
        self.cart_item = Cart.objects.create(
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
        self.user = User.objects.create_user(username='testuser', password='pass',email='testemail')
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
        self.user = User.objects.create_user(username='testuser', password='pass',email='testemail')
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


class FeedbackModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='feedback_user', password='testpass',email='testemail')
        self.category = Category.objects.create(name='Овощи')
        self.product = Product.objects.create(
            category=self.category,
            name='Морковь',
            price=Decimal('25.50'),
            count=100
        )

    def test_create_feedback_with_rating_and_review(self):
        feedback = Feedback.objects.create(
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
        feedback = Feedback(
            user=self.user,
            product=self.product,
            rating=6, 
            review="Слишком хороша, чтобы быть правдой."
        )
        with self.assertRaises(ValidationError):
            feedback.full_clean()

    def test_rating_lower_bound_validation(self):
        feedback = Feedback(
            user=self.user,
            product=self.product,
            rating=-1,
            review="Отвратительно."
        )
        with self.assertRaises(ValidationError):
            feedback.full_clean()

    def test_create_feedback_without_review(self):
        feedback = Feedback.objects.create(
            user=self.user,
            product=self.product,
            rating=3,
            review=None
        )
        self.assertIsNone(feedback.review)
        self.assertEqual(feedback.rating, 3)


class AboutTemplateViewTests(TestCase):
    def test_about_page_status_code(self):
        response = self.client.get(reverse('shop:about'))
        self.assertEqual(response.status_code, 200)

    def test_about_page_template_used(self):
        response = self.client.get(reverse('shop:about'))
        self.assertTemplateUsed(response, 'shop/about.html')

    def test_about_page_context_data(self):
        response = self.client.get(reverse('shop:about'))
        self.assertIn('site_section', response.context)
        self.assertEqual(response.context['site_section'], 'about')


class ProductListViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.category = Category.objects.create(name="Test Category")
        for i in range(10):
            Product.objects.create(
                category=cls.category,
                name=f"Product {i}",
                price=10.0,
                count=5
            )

    def test_product_list_status_code(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_product_list_template_used(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertTemplateUsed(response, 'shop/product_list.html')

    def test_product_list_htmx_template(self):
        response = self.client.get(
            reverse('shop:product_list'),
            HTTP_HX_REQUEST='true'
        )
        self.assertTemplateUsed(response, 'shop/product_partial.html')

    def test_product_list_context_data(self):
        response = self.client.get(reverse('shop:product_list'))
        context = response.context
        self.assertIn('products', context)
        self.assertIn('categories', context)
        self.assertEqual(context['category'], None)
        self.assertEqual(context['site_section'], 'product_list')

    def test_product_list_by_category(self):
        url = reverse('shop:product_list_by_category', args=[self.category.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context['products']),
            list(Product.objects.filter(category=self.category).order_by('-created')[:8])  
        )
        
    def test_product_list_pagination(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertTrue(response.context['is_paginated'])
        self.assertEqual(len(response.context['products']), 8)  

        response = self.client.get(f"{reverse('shop:product_list')}?{urlencode({'page': 2})}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 2)  


class ProductDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass',email='testemail')
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=100,
            count=10,
        )

    def test_product_detail_anonymous(self):
        url = self.product.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['product'], self.product)
        self.assertIn('is_product_in_cart', response.context)
        self.assertFalse(response.context['is_product_in_cart'])

    def test_product_detail_authenticated_not_in_cart(self):
        self.client.login(username='testuser', password='testpass',email='testemail')
        url = self.product.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_product_in_cart'])

    def test_product_detail_authenticated_in_cart(self):
        Cart.objects.create(user=self.user, product=self.product, price=100, count=1)
        self.client.login(username='testuser', password='testpass',email='testemail')
        url = self.product.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_product_in_cart'])


class CartListViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product1 = Product.objects.create(
            name='Test Product 1',
            category=self.category,
            price=10,
            count=5
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            category=self.category,
            price=20,
            count=3
        )
        Cart.objects.create(user=self.user, product=self.product1, price=self.product1.price, count=2)
        Cart.objects.create(user=self.user, product=self.product2, price=self.product2.price, count=1)

    def test_login_required(self):
        response = self.client.get(reverse('shop:cart_list'))
        self.assertRedirects(response, f'/account/login/?next={reverse("shop:cart_list")}')

    def test_cart_list_view(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('shop:cart_list'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/cart_list.html')
        self.assertIn('cart', response.context)
        self.assertIn('form', response.context)
        self.assertIn('total', response.context)
        self.assertIn('site_section', response.context)
        self.assertIsInstance(response.context['form'], OrderForm)

        cart_items = list(response.context['cart'])
        self.assertEqual(len(cart_items), 2)

        total_expected = (
            self.product1.price * 2 +
            self.product2.price * 1
        )
        self.assertEqual(response.context['total'], total_expected)
        self.assertEqual(response.context['site_section'], 'cart')


class CartAddProductViewTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Test Category')
        self.product = Product.objects.create(
            name='Test Product',
            category=self.category,
            price=50,
            count=5
        )
        self.url = reverse('shop:cart_add', args=[self.product.id])

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/account/login/?next={self.url}')

    def test_add_new_product_to_cart(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('shop:cart_list'))
        cart_item = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.count, 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.count, 4)

    def test_increment_existing_product_in_cart(self):
        Cart.objects.create(user=self.user, product=self.product, price=self.product.price, count=2)
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('shop:cart_list'))
        cart_item = Cart.objects.get(user=self.user, product=self.product)
        self.assertEqual(cart_item.count, 3)
        self.product.refresh_from_db()
        self.assertEqual(self.product.count, 4)

    def test_does_not_add_if_product_out_of_stock(self):
        self.product.count = 0
        self.product.save()

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.url)

        self.assertRedirects(response, self.product.get_absolute_url())
        self.assertFalse(Cart.objects.filter(user=self.user, product=self.product).exists())

    def test_transaction_rollback_on_error(self):
        self.client.login(username='testuser', password='testpass123')
     
        original_count = self.product.count

        with patch('shop.views.Cart.objects.get_or_create') as mocked_get_or_create:
            mocked_get_or_create.side_effect = IntegrityError('Forced integrity error')

            with self.assertRaises(IntegrityError):  
                self.client.get(self.url)

        self.assertFalse(Cart.objects.filter(user=self.user, product=self.product).exists())

        self.product.refresh_from_db()
        self.assertEqual(self.product.count, original_count)


class CartDeleteProductViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@mail.com', password='testpass123')
        self.category = Category.objects.create(name = 'testcategory')
        self.product = Product.objects.create(name='Test Product', price=50, count=5,category=self.category)
        self.cart_item = Cart.objects.create(user=self.user, product=self.product, count=2, price=self.product.price)
        self.url = reverse('shop:cart_delete', args=[self.cart_item.id])

    def test_cart_item_deleted_and_product_restored(self):
        self.client.login(username='testuser', password='testpass123')
        original_product_count = self.product.count
        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('shop:cart_list'))

        self.assertFalse(Cart.objects.filter(id=self.cart_item.id).exists())

        self.product.refresh_from_db()
        self.assertEqual(self.product.count, original_product_count + self.cart_item.count)

    def test_cart_item_only_deletes_if_owner(self):
        User.objects.create_user(username='other', email='other@mail.com', password='pass123')
        self.client.login(username='other', password='pass123')

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Cart.objects.filter(id=self.cart_item.id).exists())

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/account/login/?next={self.url}")
    
    def test_transaction_rollback_on_delete_error(self):
        self.client.login(username='testuser', password='testpass123')

        original_count = self.product.count

        with patch('shop.models.Cart.delete', side_effect=IntegrityError("Forced error")):
            with self.assertRaises(IntegrityError):
                self.client.get(self.url)

        self.assertTrue(Cart.objects.filter(id=self.cart_item.id).exists())

        self.product.refresh_from_db()
        self.assertEqual(self.product.count, original_count)


class CartIncrementViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.category = Category.objects.create(name='testcategory')
        self.product = Product.objects.create(
            id=uuid4(),
            name='Test Product',
            category = self.category,
            price=10,
            count=5,
            slug='test-product'
        )
        self.cart_item = Cart.objects.create(
            id=uuid4(),
            user=self.user,
            product=self.product,
            count=1,
            price=self.product.price
        )
        self.url = reverse('shop:cart_increment', args=[self.cart_item.id])

    def test_increment_cart_item(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.cart_item.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart_item.count, 2)
        self.assertEqual(self.product.count, 4)

    def test_increment_cart_item_product_out_of_stock(self):
        self.product.count = 0
        self.product.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.cart_item.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(self.cart_item.count, 1)  
        self.assertEqual(self.product.count, 0)   
        self.assertRedirects(response, reverse('shop:cart_list'))

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)


class CartDecrementViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.category = Category.objects.create(name='testcategory')
        self.product = Product.objects.create(
            id=uuid4(),
            name='Test Product',
            category = self.category,
            price=15,
            count=3,
            slug='test-product'
        )
        self.cart_item = Cart.objects.create(
            id=uuid4(),
            user=self.user,
            product=self.product,
            count=2,
            price=self.product.price
        )
        self.url = reverse('shop:cart_decrement', args=[self.cart_item.id])

    def test_decrement_cart_item_success(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.cart_item.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.cart_item.count, 1)
        self.assertEqual(self.product.count, 4)

    def test_decrement_not_allowed_when_count_is_one(self):
        self.cart_item.count = 1
        self.cart_item.save()

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.cart_item.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(self.cart_item.count, 1)
        self.assertEqual(self.product.count, 3)
        self.assertRedirects(response, reverse('shop:cart_list'))

    def test_requires_login(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)
    
    def test_transaction_rollback_on_error(self):
        self.client.force_login(self.user)

        with patch('shop.models.Cart.save', side_effect=IntegrityError("Forced error")):
            response = None
            try:
                response = self.client.get(self.url)
            except IntegrityError:
                pass 

            self.cart_item.refresh_from_db()
            self.product.refresh_from_db()

            self.assertEqual(self.cart_item.count, 2)
            self.assertEqual(self.product.count, 3)

            self.assertIsNone(response) 


class OrderCreateViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='testcategory')
        self.street = Street.objects.create(name='teststreet')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            account=1000
        )
        self.product = Product.objects.create(
            id=uuid4(),
            name='Test Product',
            category = self.category,
            price=200,
            count=10,
            slug='test-product'
        )
        self.cart_item = Cart.objects.create(
            user=self.user,
            product=self.product,
            price=self.product.price,
            count=2
        )
        self.url = reverse('shop:order_create')
        self.valid_form_data = {
            'street': self.street.id,
            'building': '42A',
            'apartment': '10',
            'is_private': False
        }

    def test_order_created_successfully(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.valid_form_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_done.html')

        self.user.refresh_from_db()
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(ProductInOrder.objects.count(), 1)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 0)

        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.price, 400) 
        self.assertEqual(self.user.account, 600)

    def test_order_not_created_due_to_low_balance(self):
        self.user.account = 100
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.post(self.url, self.valid_form_data)

        self.assertTemplateUsed(response, 'shop/low_balance.html')
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(ProductInOrder.objects.count(), 0)
        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)

    def test_order_not_created_due_to_invalid_form(self):
        self.user.account = Decimal('1000.00')
        self.user.save()
        self.client.force_login(self.user)

        Cart.objects.create(user=self.user, product=self.product, price=self.product.price, count=1)

        data = {
            'building': '123',
            'apartment': '45',
            'is_private': False,
        }

        response = self.client.post(reverse('shop:order_create'), data,follow=True)

        self.assertTemplateUsed(response, 'shop/cart_list.html')
        self.assertFormError(response.context['form'], 'street', 'Обязательное поле.')

    def test_login_required(self):
        response = self.client.post(self.url, self.valid_form_data)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/account/login/', response.url)

    def test_transaction_rollback_on_exception(self):
        self.user.account = 1000
        self.user.save()
        self.client.force_login(self.user)

        Cart.objects.filter(user=self.user).delete()
        Cart.objects.create(user=self.user, product=self.product, price=100, count=1)
    
        valid_data = {
            'street': self.street.id,
            'is_private': True,
            'building': '1',
        }

        with mock.patch('shop.views.ProductInOrder.objects.create', side_effect=IntegrityError):
            with self.assertRaises(IntegrityError):
                self.client.post(self.url, data=valid_data)

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(ProductInOrder.objects.count(), 0)

        self.user.refresh_from_db()
        self.assertEqual(self.user.account, 1000)

        self.assertEqual(Cart.objects.filter(user=self.user).count(), 1)


class OrderReceivedViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123',email='test@email.com')
        self.category = Category.objects.create(name='testcategory')
        self.street = Street.objects.create(name='teststreet')
        self.product = Product.objects.create(name='TestProduct', price=100,category=self.category,count=10)
        self.order = Order.objects.create(user=self.user, is_delivered=False,price=2000,is_private=True,street=self.street)
        self.order_item = ProductInOrder.objects.create(order=self.order, product=self.product, price=100, count=1)
        self.url = reverse('shop:order_received', kwargs={'id': self.order.id})

    def test_redirects_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403])

    def test_marks_order_as_delivered_on_get(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(self.url)
        self.order.refresh_from_db()
        self.assertTrue(self.order.is_delivered)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/order_received.html')

    def test_valid_feedback_submission_creates_feedback_and_removes_product(self):
        self.client.login(username='testuser', password='pass123')
        data = {
            'product_id': str(self.product.id),
            'rating': 5,
            'review': 'Отличный товар!',
        }
        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(Feedback.objects.count(), 1)

        feedback = Feedback.objects.first()
        self.assertEqual(feedback.user, self.user)
        self.assertEqual(feedback.product, self.product)
        self.assertEqual(feedback.rating, 5)

        self.assertFalse(
            ProductInOrder.objects.filter(order=self.order, product=self.product).exists()
        )
        self.assertTemplateUsed(response, 'shop/order_received.html')

    def test_post_for_product_not_in_order_redirects(self):
        self.client.login(username='testuser', password='pass123')

        ProductInOrder.objects.filter(order=self.order, product=self.product).delete()

        data = {
            'product_id': str(self.product.id),
            'rating': 4,
            'review': 'ещё отзыв',
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('shop:order_list'))
        self.assertEqual(Feedback.objects.count(), 0)


class ReviewDeleteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='pass',email='test@email.com')
        self.other_user = User.objects.create_user(username='user2', password='pass',email='test2@email.com')
        self.category = Category.objects.create(name='testcategory')
        self.product = Product.objects.create(name='TestProduct', price=100,category=self.category,count=10)
        self.feedback = Feedback.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            review='Отзыв!',
        )

        self.url = reverse('shop:review_delete', kwargs={'id': self.feedback.id})

    def test_redirects_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn(response.status_code, [302, 403])

    def test_user_can_clear_own_review(self):
        self.client.login(username='user1', password='pass')
        response = self.client.post(self.url, follow=True)
        self.feedback.refresh_from_db()
        self.assertIsNone(self.feedback.review)
        self.assertRedirects(response, self.product.get_absolute_url())

    def test_user_cannot_clear_others_review(self):
        self.client.login(username='user2', password='pass')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.review, 'Отзыв!')



