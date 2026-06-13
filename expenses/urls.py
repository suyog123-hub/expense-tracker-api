# urls.py (app level)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ExpenseViewSet, RegisterView, LoginView

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("expenses",   ExpenseViewSet,  basename="expense")

urlpatterns = [
    path("", include(router.urls)),
    path("register/", RegisterView.as_view(), name="register"),  
    path("login/",    LoginView.as_view(),    name="login"),      
]