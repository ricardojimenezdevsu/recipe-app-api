"""
Tests for the ingredients API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Recipe,
)

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Return ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='exampleuser@example.com', password='superpass123'):
    """Create and return an user"""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientAPITests(TestCase):
    """Test unauthenticated API requests."""
    def setUp(self) -> None:
        self.client = APIClient()

    def tes_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientAPITests(TestCase):
    """Test authenticated API requests."""
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Carrot')
        Ingredient.objects.create(user=self.user, name='Tomatoe')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_should_retrive_ingredients_limited_to_user(self):
        """Test should retrive ingredients limited to user"""
        user2 = create_user(email='user4@example.com')
        Ingredient.objects.create(user=user2, name='Onion')
        ingredient = Ingredient.objects.create(user=self.user, name='Garlic')

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
        self.assertEqual(res.data[0]['id'], ingredient.id)

    def test_should_update_an_ingredient(self):
        """Should update an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Chicken')

        payload = {'name': 'Meat'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(payload['name'], ingredient.name)

    def test_should_delete_an_ingredient(self):
        """Should delete an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Ingredient'
        )
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(id=ingredient.id).exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes"""
        in1 = Ingredient.objects.create(user=self.user, name='Meat')
        in2 = Ingredient.objects.create(user=self.user, name='Oil')
        recipe = Recipe.objects.create(
            user=self.user,
            title='Machaca de pescado',
            time_minutes=30,
            price=Decimal('15.15'),
            description='Mojarra'
        )
        recipe.ingredients.add(in1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        s1 = IngredientSerializer(in1)
        s2 = IngredientSerializer(in2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filter_ingredients_uinique(self):
        """Test filtering unique ingredients"""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentinls')
        recipe1 = Recipe.objects.create(
            user=self.user,
            title='Eggs Benedict',
            time_minutes=60,
            price=Decimal('7.00')
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title='Machaca de pescado',
            time_minutes=30,
            price=Decimal('15.15'),
        )
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
