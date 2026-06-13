# expenses/models.py

from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name          = models.CharField(max_length=100,)
    description   = models.CharField(max_length=255, blank=True)
    user          = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    monthly_limit = models.DecimalField(
                        max_digits=10,
                        decimal_places=2,
                        null=True,
                        blank=True,
                        help_text="Monthly budget limit in USD",
                    )
    created_at    = models.DateTimeField(auto_now_add=True, null=True)


    def __str__(self):
        return self.name


class Expense(models.Model):

    CURRENCY_CHOICES = [
        ("USD", "USD"), ("EUR", "EUR"), ("GBP", "GBP"),
        ("NPR", "NPR"), ("INR", "INR"), ("AUD", "AUD"),
    ]

    title      = models.CharField(max_length=200)
    amount     = models.DecimalField(max_digits=10, decimal_places=2)  # removed decimal_places=5 — unnecessary precision
    currency   = models.CharField(
                     max_length=3,
                     default="USD",
                     choices=CURRENCY_CHOICES,
                 )
    category   = models.ForeignKey(
                     Category,
                     on_delete=models.CASCADE,
                     related_name="expenses",
                 )
    date       = models.DateField()
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.amount} {self.currency})"