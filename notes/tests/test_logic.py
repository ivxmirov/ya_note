from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.models import Note

User = get_user_model()


class TestNoteCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='Зарегистрированный пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'any_address',
            'author': 'Пользователь'
        }

    def test_authorized_user_can_create_note(self):
        url = reverse('notes:add')
        self.auth_client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


class TestNoteSlug(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='Зарегистрированный пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='any_address',
            author=cls.user
        )
        cls.form_data = {
            'title': 'Другой заголовок',
            'text': 'Другой текст',
            'slug': 'any_address',
            'author': cls.user
        }

    def test_impossible_to_create_notes_with_same_slug(self):
        url = reverse('notes:add')
        self.auth_client.post(url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)


class TestAutoSlug(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_auto_slug_create_with_slugify(self):
        url = reverse('notes:list')
        self.author_client.get(url)
        self.assertEqual(self.note.slug, slugify(self.note.title))


class TestNoteEditDelete(TestCase):
    TITLE = 'Заголовок'
    TEXT = 'Текст'
    SLUG = 'address'
    NEW_TITLE = 'Другой заголовок'
    NEW_TEXT = 'Другой текст'
    NEW_SLUG = 'another_address'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Другой пользователь')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.form_data = {
            'title': cls.NEW_TITLE,
            'text': cls.NEW_TEXT,
            'slug': cls.NEW_SLUG,
            'author': cls.author
        }

    def test_author_can_delete_note(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_not_author_cant_delete_note(self):
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_TITLE)
        self.assertEqual(self.note.text, self.NEW_TEXT)
        self.assertEqual(self.note.slug, self.NEW_SLUG)
        self.assertEqual(self.note.author, self.author)

    def test_not_author_cant_edit_note(self):
        response = self.not_author_client.post(
            self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)
        self.assertEqual(self.note.author, self.author)
