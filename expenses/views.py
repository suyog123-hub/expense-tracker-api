# views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Sum
from collections import defaultdict

from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer, Userserializer
from .currency import convert_amount, SUPPORTED_CURRENCIES 


class RegisterView(generics.CreateAPIView):   
    queryset           = User.objects.all()
    serializer_class   = Userserializer
    permission_classes = [AllowAny]


class LoginView(APIView):                       
    permission_classes     = [AllowAny]
    authentication_classes = []

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Please provide both username and password."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)

        if user is None:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "Account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh":  str(refresh),
                "access":   str(refresh.access_token),
                "user_id":  user.id,
                "username": user.username,
                "message":  "Login successful.",
            },
            status=status.HTTP_200_OK,
        )


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class       = CategorySerializer
    authentication_classes = [JWTAuthentication]   
    permission_classes     = [IsAuthenticated]     

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get user's expenses with date filtering"""
        queryset = Expense.objects.filter(category__user=self.request.user)
        
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

    @action(detail=False, methods=["get"], url_path="summary")
    def expense_summary(self, request):
        """Get total spent per category in selected currency"""
        
        base_currency = request.query_params.get("base_currency", "USD")
        expenses = self.get_queryset()
        
        if not expenses:
            return Response({
                "base_currency": base_currency,
                "categories": [],
                "total_spent": 0
            })
        category_totals = {}
        total_spent = 0
        
        for expense in expenses:
            cat_name = expense.category.name
            
            converted = convert_amount(
                float(expense.amount), 
                expense.currency, 
                base_currency
            )
            
            category_totals[cat_name] = category_totals.get(cat_name, 0) + converted
            total_spent += converted
        
        categories = [
            {"category": name, "total": round(total, 2)}
            for name, total in category_totals.items()
        ]
        
        return Response({
            "base_currency": base_currency,
            "total_spent": round(total_spent, 2),
            "categories": categories
        })