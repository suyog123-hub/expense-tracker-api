# expenses/views.py
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
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter ,OrderingFilter
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer, Userserializer
from .currency import convert_amount, SUPPORTED_CURRENCIES


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = Userserializer
    permission_classes = [AllowAny]


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)
        
        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user_id": user.id,
            "username": user.username,
        })


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    fqueryset = Expense.objects.none()  
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['currency', 'category__name']
    search_fields = ['title', 'category__name', 'notes']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']

    def get_queryset(self):
        queryset = Expense.objects.filter(category__user=self.request.user)
        
        # Date range filters
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset

    @action(detail=False, methods=["get"], url_path="summary")
    def expense_summary(self, request):
        base_currency = request.query_params.get("base_currency", "USD").upper()
        
        if base_currency not in SUPPORTED_CURRENCIES:
            return Response({"error": f"Unsupported currency"}, status=400)

        expenses = self.get_queryset()
        
        if not expenses:
            return Response({"base_currency": base_currency, "categories": [], "total_spent": 0})

        # Calculate totals per category
        category_data = {}
        total_spent = 0

        for expense in expenses:
            cat_name = expense.category.name
            converted = convert_amount(float(expense.amount), expense.currency, base_currency)
            
            if cat_name not in category_data:
                category_data[cat_name] = {
                    "total": 0,
                    "monthly_limit": float(expense.category.monthly_limit) if expense.category.monthly_limit else None
                }
            
            category_data[cat_name]["total"] += converted
            total_spent += converted
# send mail directly to the user if expenses exceed 
        """
        ⚠️I encountered a minor issue while implementing the Telegram bot for over-expense notifications, so I have decided to use email notifications instead.⚠️
        """
        categories = []
        for name, data in category_data.items():
            total = round(data["total"], 2)
            limit = data["monthly_limit"]
            is_over = (total > limit) if limit else False

            if is_over and request.user.email:
                send_mail(
                    subject=f"⚠️ Budget Alert: {name}",
                message=f"""
Hi {request.user.username},

Your {name} spending has reached {total} {base_currency}.
Monthly limit: {limit} {base_currency}
Over by: {round(total - limit, 2)} {base_currency}

Regards,
Expense Tracker App
                    """,
                    from_email='ksuyog697@gmail.com',
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            
            categories.append({
                "category": name,
                "total_spent": total,
                "currency": base_currency,
                "monthly_limit": limit,
                "over_budget": is_over,
                "over_spend":round((total - limit), 2) if is_over else 0,
            })

        return Response({
            "base_currency": base_currency,
            "total_spent": round(total_spent, 2),
            "categories": categories
        })
    
    