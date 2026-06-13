# expenses/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Expense


class Userserializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ["id", "username", "email", "first_name", "last_name", "password", "password1"]

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        return value.strip()

    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        return value.strip()

    def validate(self, data):
        if data.get("password") != data.get("password1"):
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password1")
        return User.objects.create_user(**validated_data)


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model  = Category
        fields = [
            "id", "name", "description",
            "monthly_limit",
            "created_at",'is_favorite',
        ]
        read_only_fields = ["created_at", ]

    def validate_name(self, value):
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            if Category.objects.filter(user=request.user, name__iexact=value).exists():
                raise serializers.ValidationError(
                    f"You already have a category named '{value}'. Please use a different name."
                )
        return value

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

    def validate_monthly_limit(self, value):
        if value is not None and value <= 0:
            raise serializers.ValidationError("Monthly limit must be greater than zero.")
        return value


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model  = Expense
        fields = [
            "id", "title", "amount", "currency",
            "category", "category_name",
            "date", "notes", "created_at",
        ]
        read_only_fields = ["created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_currency(self, value):
        allowed = ["USD", "EUR", "GBP", "NPR", "INR", "AUD"]
        if value.upper() not in allowed:
            raise serializers.ValidationError(
                f"Invalid currency. Allowed: {', '.join(allowed)}"
            )
        return value.upper()