from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        """
        Filter expenses by date range if provided in query parameters.
        """
        queryset = super().get_queryset()
        
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        return queryset

    @action(detail=False, methods=["get"], url_path="summary")
    def expense_summary(self, request):
        """
        Custom action to get total spent per category.
        GET /api/expenses/summary/
        """
        summary = (
            Expense.objects
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("category__name")
        )
        return Response(list(summary))