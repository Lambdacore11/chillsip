from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal


User = get_user_model()


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
        )
        self.assertEqual(user.username,'testuser')
        self.assertEqual(user.slug, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.account, 0)


class AccountViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.password = 'password123'
        self.user = User.objects.create_user(
            username='loginuser',
            email='login@example.com',
            password=self.password,
            account=Decimal('50.00'),
            is_active=True,
        )


    def test_user_register_view(self):
            url = reverse('account:register')
            response = self.client.post(url, {
                'username': 'newuser',
                'email': 'new@example.com',
                'password': 'newpassword123',
                'password2': 'newpassword123',
            })
            self.assertEqual(response.status_code, 200)
            self.assertTrue(User.objects.filter(username='newuser').exists())


    def test_user_login_view(self):
        url = reverse('account:login')
        response = self.client.post(url, {
            'username': self.user.username,
            'password': self.password
        })
        self.assertEqual(response.status_code, 302)


    def test_user_logout_view(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('account:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)


    def test_user_password_change_view(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('account:password_change')
        response = self.client.post(url, {
            'old_password': self.password,
            'new_password1': 'newsecurepass123',
            'new_password2': 'newsecurepass123',
        })
        self.assertRedirects(response, reverse('account:password_change_done'))


    def test_user_update_view(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('account:profile', kwargs={'slug': self.user.slug})

        response = self.client.post(url, {
            'email': self.user.email,
            'first_name': 'updatedname',
            'middle_name':'updatedmiddlename',
            'last_name': 'updatedlastname',
            'age': 45,
            'gender':'m',
        })

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'updatedname')
        self.assertEqual(self.user.middle_name, 'updatedmiddlename')
        self.assertEqual(self.user.last_name, 'updatedlastname')
        self.assertEqual(self.user.age, 45)
        self.assertEqual(self.user.gender, 'm')



    def test_money_update_view(self):
        self.client.login(username=self.user.username, password=self.password)
        url = reverse('account:money', kwargs={'slug': self.user.slug})
        response = self.client.post(url, {'account': '100.00'})
        self.assertRedirects(response, reverse('account:money_done'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.account, Decimal('150.00'))


    def test_password_reset_complete_view(self):
        url = reverse('account:password_reset_complete')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)