"""Top-level URL configuration for the Expense Tracker project."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("expenses.urls")),
]
