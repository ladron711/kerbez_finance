from  django.utils import timezone
from datetime import timedelta
from django.db.models import Sum

from core.models import Category, Transaction


async def _get_summary(transaction_type: str, period: timedelta) -> dict:
    start_date = timezone.now()- period

    total = (
        await Transaction.objects.filter(category__type=transaction_type,
                                         created_at__gte=start_date,
                                         ).aaggregate(total=Sum("amount")
                                                      ))["total"] or 0
    
    rows = [
        row async for row in Transaction.objects.filter(
            category__type=transaction_type,
            created_at__gte=start_date,
        )
        .values("category__name")
        .annotate(total=Sum("amount"))
    ]

    by_category = {row["category__name"]:row["total"] for row in rows}

    return {
        "total": total,
        "by_category": by_category,
    }


async def get_worker_summary(period: timedelta) -> dict:
    start_date = timezone.now() - period

    rows = [
        row 
        async for row in Transaction.objects.filter(
            worker__isnull=False,
            created_at__gte=start_date,
        )
        .values("worker__name")
        .annotate(total=Sum("amount"))
    ]
    return {row["worker__name"]: row["total"] for row in rows}


async def get_expense_summary(period: timedelta) -> dict:
    return await _get_summary(Category.Type.EXPENSE, period)


async def get_income_summary(period: timedelta) -> dict:
    return await _get_summary(Category.Type.INCOME, period)


def format_categories(by_category: dict) -> str:
    if not by_category:
        return "—"
    return "\n".join(f"  {name}: {total}" for name, total in by_category.items())