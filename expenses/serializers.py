from rest_framework import serializers

from .models import Category, Expense
from django.contrib.auth.models import User

class Userserializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    class Meta: 
        model = User
        fields = ['first_name','last_name','email','username','password','password1']

    def validate_first_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("First name is required.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("First name must be at least 2 characters.")
        return value.strip()
    
    def validate_last_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Last name is required.")
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Last name must be at least 2 characters.")
        return value.strip()

    def validate(self,data):
        if data['password'] != data['password1']:
            raise serializers.ValidationError('Password and Confirm Password do not match')
        return data
  
    
    def create(self, validated_data):
        validated_data.pop('password1') 

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "title", "amount", "category", "date", "notes"]
