from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=5)
    currency = models.CharField(max_length=3, default="USD", choices=[
        ("USD", "USD"), ("EUR", "EUR"), ("GBP", "GBP"), 
        ("NPR", "NPR"), ("INR", "INR"), ("AUD", "AUD")],null=True) 
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="expenses")
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f"{self.title} ({self.amount})"
