from django.test import TestCase
from django.contrib.auth import get_user_model
from blog.models import *
from blog.forms import *
from uuid import UUID
from datetime import datetime
from datetime import timedelta
import re
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

User = get_user_model()

def get_test_image_file():
    img = Image.new('RGB', (100, 100), color='red')
    buf = BytesIO()
    img.save(buf, format='JPEG')
    buf.seek(0)
    return SimpleUploadedFile('test.jpg', buf.read(), content_type='image/jpeg')

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='secret123'
        )
        self.post = Post.objects.create(
            user=self.user,
            name='Тестовый пост',
            content='Это содержимое тестового поста.'
        )
    def test_post_creation(self):
        self.assertIsInstance(self.post, Post)
        self.assertEqual(self.post.name, 'Тестовый пост')
        self.assertEqual(self.post.user, self.user)
        self.assertFalse(self.post.is_published)

    def test_slug_auto_generated(self):
        self.assertTrue(re.match(r'^testovyij-post(-\d+)?$', self.post.slug))

    def test_get_absolute_url(self):
        expected_url = f'/blog/post/{self.post.slug}/'
        self.assertEqual(self.post.get_absolute_url(), expected_url)

    def test_uuid_primary_key(self):
        self.assertIsInstance(self.post.id, UUID)

    def test_created_and_updated_auto_fields(self):
        self.assertIsInstance(self.post.created, datetime)
        self.assertIsInstance(self.post.updated, datetime)
        self.assertAlmostEqual(self.post.created, self.post.updated, delta=timedelta(seconds=1))

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )
        self.post = Post.objects.create(
            user=self.user,
            name='Пост для теста',
            content='Контент поста'
        )
        self.comment = Comment.objects.create(
            user=self.user,
            post=self.post,
            content='Это тестовый комментарий.'
        )

    def test_comment_creation(self):
        self.assertIsInstance(self.comment, Comment)
        self.assertEqual(self.comment.content, 'Это тестовый комментарий.')
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.post, self.post)

    def test_uuid_field(self):
        self.assertIsInstance(self.comment.id, UUID)

    def test_created_and_updated_fields(self):
        self.assertIsNotNone(self.comment.created)
        self.assertIsNotNone(self.comment.updated)
        self.assertAlmostEqual(
            self.comment.created,
            self.comment.updated,
            delta=timedelta(seconds=1)
        )

    def test_str_method(self):
        self.assertEqual(str(self.comment), 'Это тестовый комментарий.')


class CommentFormTest(TestCase):
    def test_form_valid_with_content(self):
        form_data = {'content': 'Это тестовый комментарий'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_content(self):
        form_data = {'content': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_fields(self):
        form = CommentForm()
        self.assertIn('content', form.fields)
        self.assertEqual(len(form.fields), 1)


class PostFormTest(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123'
        )

        self.image = get_test_image_file()
    
    def tearDown(self):
        if hasattr(self, 'post') and self.post.image:
            image_path = self.post.image.path
            if os.path.exists(image_path):
                os.remove(image_path)

    def test_form_valid_with_all_fields(self):
        form_data = {
            'name': 'Тестовый пост',
            'content': 'Контент поста',
        }
        form_files = {
            'image': self.image
        }
        form = PostForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid())
        self.post = form.save(commit=False)
        self.post.user = self.user
        self.post.save()

class PostListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='user1', email='u1@example.com', password='pass')
        for i in range(5):
            Post.objects.create(
                user=cls.user,
                name=f'Пост {i}',
                content='Контент',
                is_published= True
            )
        for i in range(2):
            Post.objects.create(
            user=cls.user,
            name=f'Неопубликованный {i}',
            content='Контент',
            is_published=False
        )
            
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/blog/') 
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        url = reverse('blog:post_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        url = reverse('blog:post_list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'blog/post_list.html')

    def test_pagination_is_three(self):
        url = reverse('blog:post_list')
        response = self.client.get(url)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] is True)
        self.assertEqual(len(response.context['posts']), 3)

    def test_only_published_posts_in_queryset(self):
        url = reverse('blog:post_list')
        response = self.client.get(url)
        posts = response.context['posts']
        for post in posts:
            self.assertTrue(post.is_published)
        self.assertEqual(posts.count(), 3)

class PostCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shadow', password='pass123',email='test@email.com')
        self.url = reverse('blog:post_create') 

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/account/login/?next={self.url}')

    def test_get_create_form_logged_in(self):
        self.client.login(username='shadow', password='pass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_create.html')

    def test_post_create_post_valid(self):
        self.client.login(username='shadow', password='pass123')
        image = get_test_image_file()
        data = {
            'name': 'Новый пост',
            'content': 'Тестовый контент',
            'image': image,
        }

        response = self.client.post(self.url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        post = Post.objects.get(name='Новый пост')
        self.assertEqual(post.user, self.user)
        self.assertEqual(post.content, 'Тестовый контент')
        if post.image:
            post.image.delete(save=False)

class PostCreateDoneViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shadow', password='pass123',email='test@email.com')
        self.url = reverse('blog:post_done')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f'/account/login/?next={self.url}')

    def test_get_done_page_logged_in(self):
        self.client.login(username='shadow', password='pass123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_done.html')


class PostDetailViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='shadow', password='pass123',email='test@email.com')
        cls.post = Post.objects.create(
            user=cls.user,
            name='Тестовый пост',
            content='Контент поста',
            is_published=True
        )
   
        for i in range(12):
            Comment.objects.create(
                post=cls.post,
                user=cls.user,
                content=f'Комментарий {i}',
            )

    def test_post_detail_status_and_template(self):
        url = reverse('blog:post_detail', args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')

    def test_context_contains_post_and_form(self):
        url = reverse('blog:post_detail', args=[self.post.slug])
        response = self.client.get(url)
        self.assertEqual(response.context['post'], self.post)
        self.assertIsInstance(response.context['form'], CommentForm)

    def test_comments_pagination(self):
        url = reverse('blog:post_detail', args=[self.post.slug])
        response = self.client.get(url)
        comments = response.context['comments']
        self.assertTrue(comments.has_other_pages())
        self.assertEqual(comments.paginator.per_page, 5)
        self.assertEqual(len(comments.object_list), 5) 

      
        response2 = self.client.get(url + '?page=2')
        comments_page2 = response2.context['comments']
        self.assertEqual(len(comments_page2.object_list), 5)

        response3 = self.client.get(url + '?page=3')
        comments_page3 = response3.context['comments']
        self.assertEqual(len(comments_page3.object_list), 2)

class CommentCreateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='shadow', password='pass123',email='test@email.com')
        self.post = Post.objects.create(
            user=self.user,
            name='Тестовый пост',
            content='Тестовый контент',
            is_published=True
        )
        self.url = reverse('blog:comment_create')

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url, {'post_id': self.post.id, 'content': 'Комментарий'})
        self.assertNotEqual(response.status_code, 200)
        self.assertIn('/account/login/', response.url)

    def test_create_comment_logged_in(self):
        self.client.login(username='shadow', password='pass123')
        data = {
            'post_id': str(self.post.id),
            'content': 'Тестовый комментарий'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.content, 'Тестовый комментарий')
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.user, self.user)

class CommentDeleteViewTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='shadow', password='pass123',email='test@email,com')
        self.user2 = User.objects.create_user(username='not_shadow', password='pass123',email='test@email2,com')
        self.post = Post.objects.create(
            user=self.user1,
            name='Пост для удаления',
            content='Контент',
            is_published=True
        )
        self.comment = Comment.objects.create(
            post=self.post,
            user=self.user1,
            content='Комментарий для удаления'
        )
        self.url = reverse('blog:comment_delete', args=[self.comment.id])

    def test_redirect_if_not_logged_in(self):
        response = self.client.post(self.url)
        self.assertNotEqual(response.status_code, 200)
        self.assertIn('/account/login/', response.url)

    def test_delete_comment_by_owner(self):
        self.client.login(username='shadow', password='pass123')
        response = self.client.post(self.url)
        self.assertRedirects(response, self.post.get_absolute_url())
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_by_other_user_404(self):
        self.client.login(username='not_shadow', password='pass123')
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())
