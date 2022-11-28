"""
Tests for the ingredients API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

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
