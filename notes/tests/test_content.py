from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор заметки')
        cls.not_author = User.objects.create(username='Другой пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='any_address',
            author=cls.author
        )

    def test_separate_note_is_in_author_notes_list(self):
        self.client.force_login(self.author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_is_not_in_not_author_notes_list(self):
        self.client.force_login(self.not_author)
        url = reverse('notes:list')
        response = self.client.get(url)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        for name, args in (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        ):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
