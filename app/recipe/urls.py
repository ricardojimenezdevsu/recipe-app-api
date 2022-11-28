"""
URL mappings for the recipe app.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()
# include all routes/endpoints for the view
# autogenerate endpoints dependign of the enabled in the viewset
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]
