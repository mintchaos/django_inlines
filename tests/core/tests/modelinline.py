from django.test import TestCase
from django_inlines.inlines import Registry, inline_for_model, InlineInputError
from django.conf import settings
from test_inlines import UserInline
from core.models import User

class ModelInlineTestCase(TestCase):

    fixtures = ['users']

    def setUp(self):
        inlines = Registry()
        inlines.register('user', UserInline)
        self.inlines = inlines

    def testModelInlines(self):
        self.assertEqual(self.inlines.process("{{ user 1 }}"), "Xian")
        self.assertEqual(self.inlines.process("{{ user 1 }} vs {{ user 2 }}"), "Xian vs Evil Xian")

    def testModelInlineVariants(self):
        self.assertEqual(self.inlines.process("{{ user:contact 1 }}"), "Xian, (708) 555-1212, xian@example.com")
        self.assertEqual(self.inlines.process("{{ user:nonexistant_variant 1 }}"), "Xian")


class BadInputModelInlineTestCase(TestCase):

    fixtures = ['users']

    def setUp(self):
        inlines = Registry()
        inlines.register('user', UserInline)
        self.inlines = inlines

    def tearDown(self):
        settings.INLINE_DEBUG = False

    def testAgainstNonexistentObject(self):
        self.assertEqual(self.inlines.process("{{ user 111 }}"), "")

    def testAgainstCrapInput(self):
        self.assertEqual(self.inlines.process("{{ user asdf }}"), "")

    def testErrorRaising(self):
        settings.INLINE_DEBUG = True
        process = self.inlines.process
        self.assertRaises(InlineInputError, process, "{{ user 111 }}",)
        self.assertRaises(InlineInputError, process, "{{ user asdf }}",)

class InlineForModelTestCase(TestCase):

    fixtures = ['users']

    def setUp(self):
        inlines = Registry()
        self.inlines = inlines

    def testInlineForModel(self):
        self.inlines.register('user', inline_for_model(User))
        self.assertEqual(self.inlines.process("{{ user 1 }}"), "Xian")
        self.assertEqual(self.inlines.process("{{ user 1 }} vs {{ user 2 }}"), "Xian vs Evil Xian")

    def testInlineForModelBadInput(self):
        self.assertRaises(ValueError, inline_for_model, "User")
