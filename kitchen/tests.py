from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from kitchen.models import DishType, Cook, Dish
from kitchen.forms import (CookCreationForm,
                           DishTypeSearchForm,
                           DishSearchForm,
                           CookSearchForm)


class ModelTestCase(TestCase):
    def setUp(self):
        self.dish_type = DishType.objects.create(name="Main course")
        self.cook = Cook.objects.create(
            username="john",
            first_name="John",
            last_name="Doe"
        )
        self.dish = Dish.objects.create(
            name="Spaghetti Carbonara",
            description="Pasta with bacon and eggs",
            price=9.99,
            dish_type=self.dish_type
        )
        self.dish.cooks.add(self.cook)

    def test_dish_type_str(self):
        self.assertEqual(str(self.dish_type), "Main course")

    def test_cook_str(self):
        self.assertEqual(str(self.cook), "john (John Doe)")

    def test_dish_str(self):
        self.assertEqual(str(self.dish), "Spaghetti Carbonara")


class CookCreationFormTestCase(TestCase):
    def setUp(self):
        self.url = reverse("kitchen:cook-create")

    def test_form_valid(self):
        form_data = {
            "username": "johndoe",
            "first_name": "John",
            "last_name": "Doe",
            "years_of_experience": 5,
            "password1": "user12345",
            "password2": "user12345",
        }
        form = CookCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, "johndoe")
        self.assertIsInstance(user, Cook)
        self.assertEqual(user.years_of_experience, 5)

    def test_form_invalid(self):
        form_data = {
            "username": "",
            "first_name": "",
            "last_name": "",
            "years_of_experience": "",
            "password1": "",
            "password2": "",
        }
        form = CookCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["This field is required."])
        self.assertEqual(form.errors["first_name"],
                         ["This field is required."])
        self.assertEqual(form.errors["last_name"], ["This field is required."])
        self.assertEqual(form.errors["years_of_experience"],
                         ["This field is required."])
        self.assertEqual(form.errors["password1"], ["This field is required."])
        self.assertEqual(form.errors["password2"], ["This field is required."])


class TestSearchForms(TestCase):
    def test_dish_type_search_form(self):
        form_data = {"name": "Appetizers"}
        form = DishTypeSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_dish_search_form(self):
        form_data = {"name": "Chicken Wings"}
        form = DishSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_cook_search_form(self):
        form_data = {"username": "johndoe"}
        form = CookSearchForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)


class ToggleAssignToDishTestCase(TestCase):
    def setUp(self):
        dish_type = DishType.objects.create(name='test type')
        self.user = get_user_model().objects.create_user(
            username='testuser123123',
            password='testpass123132',
        )
        self.cook1 = Cook.objects.create(
            first_name='Cook 1',
            username='cook1'
        )
        self.cook2 = Cook.objects.create(
            first_name='Cook 2',
            username='cook2'
        )
        self.dish = Dish.objects.create(
            name='test dish',
            description='test description',
            price="10.55",
            dish_type=dish_type,
        )
        self.dish.cooks.set([self.cook1, self.cook2])
        self.url = reverse('kitchen:toggle-dish-assign', args=[self.dish.pk])

    def test_toggle_assign_to_dish(self):
        self.client.login(username='testuser123123', password='testpass123132')
        self.assertFalse(self.dish in self.user.dishes.all())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.dish in self.user.dishes.all())
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.dish in self.user.dishes.all())


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            password="testpass"
        )
        self.dish_type = DishType.objects.create(name="Test Dish Type")
        self.cook = Cook.objects.create_user(
            username="testcook",
            password="testpass",
            first_name="Test",
            last_name="Cook",
            years_of_experience=5
        )
        self.dish = Dish.objects.create(
            name="Test Dish",
            description="A test dish",
            price=10.99,
            dish_type=self.dish_type
        )
        self.dish.cooks.set([self.cook])

    def test_index_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("kitchen:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "kitchen/index.html")
        self.assertContains(response, "Types of dishes")
        self.assertContains(response, "Number of dishes")
        self.assertContains(response, "Number of cooks")
