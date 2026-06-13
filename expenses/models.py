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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="expenses"
    )
    date = models.DateField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.amount})"
