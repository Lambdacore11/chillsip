import os
import shutil
import tempfile
import uuid
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase,override_settings,Client
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.text import slugify
from PIL import Image
from django.conf import settings
from account.models import SuspiciousUser
from .forms import *


User = get_user_model()

TEMP_MEDIA_ROOT = os.path.join(settings.BASE_DIR, 'temp_test_media')

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            middle_name='Иванович',
            account=100.00,
            age=30,
            gender='m'
        )

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser test@example.com')
    
    def test_username_is_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser',
                email='anotheruser@email.com',
                password='anotherpass123',
            )

    def test_email_is_unique(self):
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='anotheruser',
                email='test@example.com',
                password='anotherpass123',
            )

    def test_create_superuser_flags(self):
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpass',
                is_staff=False
            )

    def test_account_default(self):
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='newpass123',
        )
        self.assertEqual(user.account, 0)

    def test_uuid_is_assigned(self):
        self.assertIsInstance(self.user.id, uuid.UUID)

    def test_gender_choices(self):
        self.user.gender = 'f'
        self.user.full_clean()
        self.user.gender = 'x'
        with self.assertRaises(ValidationError):
            self.user.full_clean()

    def test_slug_is_generated(self):
        self.assertEqual(self.user.slug, slugify(self.user.username))

    def test_slug_is_unique(self):
        
        user = User.objects.create_user(
            username='тестусер',
            email='user2@example.com',
            password='12345678'
        )
        self.assertNotEqual(self.user.slug, user.slug)

    def test_email_required(self):
        with self.assertRaises(TypeError):
            User.objects.create_user(username='noemail', password='pass123')

        with self.assertRaises(ValueError):
            User.objects.create_user(username='noemail', email='', password='pass123')
    

    def test_age_constraints(self):
        self.user.age = 151
        with self.assertRaises(ValidationError):
            self.user.full_clean()

        self.user.age = 0
        with self.assertRaises(ValidationError):
            self.user.full_clean()

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserImageUploadTest(TestCase):

    def tearDown(self):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_image_upload(self):
        img = BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(img, format='JPEG')
        img.seek(0)

        image_file = SimpleUploadedFile(
            name='test.jpg',
            content=img.read(),
            content_type='image/jpeg'
        )

        user = User.objects.create_user(
            username='picuser',
            email='pic@example.com',
            password='12345678',
            foto=image_file,
        )

        self.assertTrue(user.foto.name.startswith('foto/'))
        self.assertTrue(user.foto.storage.exists(user.foto.name))


class UserRegisterFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_username_too_short(self):
        form_data = {
            'username': 'abc',
            'email': 'test@example.com',
            'password': 'StrongPass123',
            'password2': 'StrongPass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_password_too_short(self):
        form_data = {
            'username': 'goodname',
            'email': 'test@example.com',
            'password': '12345',
            'password2': '12345'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_password_all_digits(self):
        form_data = {
            'username': 'goodname',
            'email': 'test@example.com',
            'password': '12345678',
            'password2': '12345678'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_passwords_do_not_match(self):
        form_data = {
            'username': 'goodname',
            'email': 'test@example.com',
            'password': 'Goodpass123',
            'password2': 'Wrongpass123'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class UserPasswordChangeFormTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='changepass',
            email='change@example.com',
            password='OldPass123'
        )

    def test_valid_password_change(self):
        form_data = {
            'old_password': 'OldPass123',
            'new_password1': 'NewStrongPass123',
            'new_password2': 'NewStrongPass123',
        }
        form = UserPasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())

    def test_short_new_password(self):
        form_data = {
            'old_password': 'OldPass123',
            'new_password1': 'short',
            'new_password2': 'short',
        }
        form = UserPasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password1', form.errors)
        self.assertIn('не менее 8 символов', form.errors['new_password1'][0])

    def test_numeric_password(self):
        form_data = {
            'old_password': 'OldPass123',
            'new_password1': '12345678',
            'new_password2': '12345678',
        }
        form = UserPasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password1', form.errors)
        self.assertIn('состоит только из цифр', form.errors['new_password1'][0])

    def test_password_mismatch(self):
        form_data = {
            'old_password': 'OldPass123',
            'new_password1': 'NewPass123',
            'new_password2': 'OtherPass456',
        }
        form = UserPasswordChangeForm(user=self.user, data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_password2', form.errors)
    
    def test_save_changes_password(self):
        form_data = {
            'old_password': 'OldPass123',
            'new_password1': 'NewValidPass456',
            'new_password2': 'NewValidPass456',
        }
        form = UserPasswordChangeForm(user=self.user, data=form_data)
        self.assertTrue(form.is_valid())
        
        form.save()
        
        self.user.refresh_from_db()
        
        self.assertTrue(self.user.check_password('NewValidPass456'))


class UserLoginFormTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )

    def test_login_with_username(self):
        form_data = {
            'username': 'testuser',
            'password': 'TestPass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = authenticate(username='testuser', password='TestPass123')
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_login_with_email(self):
        form_data = {
            'username': 'test@example.com',
            'password': 'TestPass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = authenticate(username='test@example.com', password='TestPass123')
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_login_with_invalid_password(self):
        form_data = {
            'username': 'testuser',
            'password': 'WrongPass123'
        }
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserUpdateFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='securepass123'
        )
        os.makedirs(TEMP_MEDIA_ROOT, exist_ok=True)

    def tearDown(self):
        if os.path.exists(TEMP_MEDIA_ROOT):
            shutil.rmtree(TEMP_MEDIA_ROOT)

    def generate_image_file(self, name='test.jpg'):
        img = BytesIO()
        image = Image.new('RGB', (100, 100), color='blue')
        image.save(img, format='JPEG')
        img.seek(0)
        return SimpleUploadedFile(name, img.read(), content_type='image/jpeg')

    def test_valid_data_updates_user(self):
        form_data = {
            'first_name': 'Иван',
            'middle_name': 'Иванович',
            'last_name': 'Петров',
            'email': 'new@example.com',
            'age': 30,
            'gender': 'm',
        }
        image_file = self.generate_image_file()
        form = UserUpdateForm(data=form_data, files={'foto': image_file}, instance=self.user)

        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertEqual(user.first_name, 'Иван')
        self.assertEqual(user.middle_name, 'Иванович')
        self.assertEqual(user.last_name, 'Петров')
        self.assertEqual(user.email, 'new@example.com')
        self.assertEqual(user.age, 30)
        self.assertEqual(user.gender, 'm')
        self.assertTrue(user.foto.name.startswith('foto/'))


class MoneyUpdateFormTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='moneyboy',
            email='money@example.com',
            password='12345678',
            account=Decimal('0.00')
        )

    def test_valid_money_choice(self):
        form = MoneyUpdateForm(data={'account': '100'})
        self.assertTrue(form.is_valid())
        cleaned = form.cleaned_data['account']
        self.assertEqual(cleaned, Decimal('100'))

    def test_invalid_money_choice(self):
        form = MoneyUpdateForm(data={'account': '777'})
        self.assertFalse(form.is_valid())
        self.assertIn('account', form.errors)

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

class UserRegisterViewTests(TestCase):
    def setUp(self):
        self.url = reverse('account:register')
        self.data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',  
        }

    def test_register_view_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')

    def test_register_view_post_invalid_data(self):
        invalid_data = self.data.copy()
        invalid_data['password2'] = 'Mismatch123'
        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'password2', 'Пароли не совпадают')
        self.assertEqual(get_user_model().objects.count(), 0)

    def test_register_view_post_invalid_data(self):
        invalid_data = self.data.copy()
        invalid_data['password2'] = 'Mismatch123'
        response = self.client.post(self.url, invalid_data)

        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertFormError(form, 'password2', 'Пароли не совпадают') 
        self.assertEqual(get_user_model().objects.count(), 0)

class UserLoginViewTest(TestCase):
    def setUp(self):
        self.login_url = reverse('account:login')
        self.password = 'testpass123'
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password=self.password
        )

    def test_login_page_loads(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_success_with_email(self):
        response = self.client.post(self.login_url, {
            'username': self.user.email,
            'password': self.password
        })
        self.assertRedirects(response, '/')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_success_with_username(self):
        response = self.client.post(self.login_url, {
            'username': self.user.username,
            'password': self.password
        })
        self.assertRedirects(response, '/')
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_login_fail_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'wrong',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertFalse('_auth_user_id' in self.client.session)

class UserLogoutViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='secret123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='secret123')
        self.logout_url = reverse('account:logout')

    def test_logout_with_post(self):
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)  
        self.assertNotIn('_auth_user_id', self.client.session)  

    def test_logout_with_get_disallowed(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 405)


class UserPasswordChangeTest(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.password = 'OldPassword123'
        self.user = self.user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password=self.password
        )
        self.login_url = reverse('account:login')
        self.change_url = reverse('account:password_change')
        self.done_url = reverse('account:password_change_done')

    def test_password_change_view_requires_login(self):
        response = self.client.get(self.change_url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(self.login_url))

    def test_password_change_page_loads_for_logged_in_user(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.get(self.change_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_change.html')

    def test_password_change_success(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.post(self.change_url, {
            'old_password': self.password,
            'new_password1': 'NewSecurePassword456',
            'new_password2': 'NewSecurePassword456',
        })
        self.assertRedirects(response, self.done_url)

    
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePassword456'))

    def test_password_change_done_view_loads(self):
        self.client.login(username='testuser', password=self.password)
        self.client.post(self.change_url, {
            'old_password': self.password,
            'new_password1': 'NewSecurePassword456',
            'new_password2': 'NewSecurePassword456',
        })
        response = self.client.get(self.done_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_change_done.html')

    def test_password_change_invalid_old_password(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.post(self.change_url, {
            'old_password': 'WrongOldPassword',
            'new_password1': 'AnotherPass123',
            'new_password2': 'AnotherPass123',
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)

    def test_password_change_mismatched_passwords(self):
        self.client.login(username='testuser', password=self.password)
        response = self.client.post(self.change_url, {
            'old_password': self.password,
            'new_password1': 'Mismatch123',
            'new_password2': 'Mismatch456',
        })
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)


class UserUpdateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='TestPass123',
            slug='user1-slug'
        )
        self.other_user = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='TestPass123',
            slug='user2-slug'
        )
        self.url = reverse('account:profile', kwargs={'slug': self.user.slug})

    def test_login_required_redirect(self):
        """Анонимный пользователь должен быть перенаправлен на логин"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('account:login')))

    def test_get_own_profile_update_page(self):
        """Аутентифицированный пользователь может получить доступ к своей странице"""
        self.client.login(username='user1', password='TestPass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile.html')
        self.assertIsInstance(response.context['form'], UserUpdateForm)

    def test_update_own_profile(self):
        self.client.login(username='user1', password='TestPass123')
        response = self.client.post(self.url, {
            'first_name': 'Updated',
            'middle_name': 'Middle',
            'last_name': 'User',
            'email': 'newemail@example.com',
            'age': 30,
            'gender': 'f',
        })

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.middle_name, 'Middle')
        self.assertEqual(self.user.last_name, 'User')
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.age, 30)
        self.assertEqual(self.user.gender, 'f')
        self.assertRedirects(response, self.url)

    def test_access_other_user_profile_creates_suspicious_entry(self):
        self.client.login(username='user1', password='TestPass123')
        other_url = reverse('account:profile', kwargs={'slug': self.other_user.slug})
        response = self.client.get(other_url)
        self.assertRedirects(response, self.url)
        suspicious_entries = SuspiciousUser.objects.filter(user=self.user)
        self.assertEqual(suspicious_entries.count(), 1)
        self.assertIn(self.other_user.slug, suspicious_entries.first().reason)

    def test_post_to_other_user_profile_creates_suspicious_entry(self):
        self.client.login(username='user1', password='TestPass123')
        other_url = reverse('account:profile', kwargs={'slug': self.other_user.slug})
        response = self.client.post(other_url, {
            'username': 'hacker_user',
            'email': 'hacker@example.com',
        })

        self.user.refresh_from_db()
        self.assertNotEqual(self.user.username, 'hacker_user')
        self.assertRedirects(response, self.url)
        self.assertTrue(SuspiciousUser.objects.filter(user=self.user).exists())

class MoneyUpdateViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='user1',
            email='user1@example.com',
            password='Test1234',
            slug='user1',
            account=100 
        )
        self.other_user = get_user_model().objects.create_user(
            username='user2',
            email='user2@example.com',
            password='Test1234',
            slug='user2',
            account=500
        )
        self.url = reverse('account:money_update', kwargs={'slug': self.user.slug})

    def test_authenticated_user_can_access_own_money_page(self):
        self.client.login(username='user1', password='Test1234')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/money_update.html')

    def test_authenticated_user_cannot_access_other_user_money_page(self):
        self.client.login(username='user2', password='Test1234')
        url = reverse('account:money_update', kwargs={'slug': self.user.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('account:profile', kwargs={'slug': self.other_user.slug}))
        self.assertTrue(SuspiciousUser.objects.filter(user=self.other_user).exists())

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        login_url = reverse('account:login')
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_successful_money_update(self):
        self.client.login(username='user1', password='Test1234')
        response = self.client.post(self.url, {'account': '100'})  
        self.user.refresh_from_db()
        self.assertEqual(self.user.account, 200) 
        self.assertRedirects(response, reverse('account:money_done'))

    def test_invalid_form_does_not_change_account(self):
        self.client.login(username='user1', password='Test1234')
        response = self.client.post(self.url, {'account': 'не число'})
        self.user.refresh_from_db()
        self.assertEqual(self.user.account, 100)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/money_update.html')
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertIn('account', form.errors)

class MoneyDoneViewTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser', email='test@example.com', password='Test1234'
        )
        self.url = reverse('account:money_done')  

    def test_authenticated_user_can_access(self):
        self.client.login(username='testuser', password='Test1234')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/money_done.html')
        self.assertContains(response, "успешно", status_code=200) 

    def test_anonymous_user_redirected(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('account:login')))

    def test_url_resolves_correctly(self):
        from django.urls import resolve
        from account.views import MoneyDoneView
        resolver = resolve(self.url)
        self.assertEqual(resolver.func.view_class, MoneyDoneView)