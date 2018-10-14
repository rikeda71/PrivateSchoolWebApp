from django.test import TestCase
from django.urls import reverse, resolve
from django.forms import widgets
from accounts.views import upload_file
from accounts.forms import UploadFileForm
from accounts.models import User
import pdb


class UploadViewTest(TestCase):

    def setUp(self):
        super().setUp()
        url = reverse('accounts:upload')
        self.response = self.client.get(url)

    def test_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_class(self):
        view = resolve('/accounts/upload/')
        self.assertEqual(view.func, upload_file)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_value_of_contain_form_inputs(self):
        self.assertContains(self.response, '<input', 3)

    def test_accept_for_only_pdf(self):
        self.assertContains(self.response, 'accept="application/pdf"')


class UploadFormTest(TestCase):

    def setUp(self):
        super().setUp()
        self.form = UploadFileForm

    def test_field_widget_type(self):
        self.assertEqual(widgets.ClearableFileInput,
                         self.form.base_fields['attach'].widget.__class__)


class UploadFileTest(TestCase):

    def test_upload_valid(self):
        with open('accounts/tests/test.pdf', "rb") as f:
            response = self.client.post(reverse('accounts:upload'), {'attach': f})
            self.assertRedirects(response, '/accounts/')

    def test_upload_invalid(self):
        with open('accounts/tests/test.png', "rb") as f:
            response = self.client.post(reverse('accounts:upload'), {'attach': f})
            self.assertEqual(response.status_code, 200)
