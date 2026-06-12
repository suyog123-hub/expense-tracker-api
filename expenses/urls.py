from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Create a router and register our viewsets
router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('expenses',ExpenseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]