# expenses/bot.py

"""
Telegram Budget Alert Bot.
Sends a message when monthly spend exceeds the category budget limit.
"""

import requests
from django.conf import settings
from django.utils import timezone


def send_telegram_alert(message: str) -> bool:
    """
    Send a message to the configured Telegram chat.
    Returns True if sent successfully, False otherwise.
    """
    token   = settings.TELEGRAM_BOT_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        print("Telegram not configured — skipping alert.")
        return False

    url  = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id":    chat_id,
        "text":       message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, data=data, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Failed to send Telegram alert: {e}")
        return False


def check_budget_alert(expense) -> None:
    """
    Check if adding this expense causes the monthly total
    to exceed the category's monthly_limit.
    If yes — send a Telegram alert.

    Called after every expense is created.
    """
    category = expense.category

    # No limit set — nothing to check
    if not category.monthly_limit:
        return

    # Get current month's total for this category
    now          = timezone.now()
    monthly_total = (
        category.expenses
        .filter(
            date__year=now.year,
            date__month=now.month,
        )
        .aggregate(total=__import__("django.db.models", fromlist=["Sum"]).Sum("amount"))
        ["total"] or 0
    )

    monthly_total = float(monthly_total)
    limit         = float(category.monthly_limit)

    if monthly_total > limit:
        over_by = round(monthly_total - limit, 2)
        message = (
            f"<b>Budget Alert!</b>\n\n"
            f"Category   : <b>{category.name}</b>\n"
            f"Monthly Limit : <b>${limit}</b>\n"
            f"Total Spent   : <b>${round(monthly_total, 2)}</b>\n"
            f" Over By       : <b>${over_by}</b>\n\n"
            f"Last expense: <b>{expense.title}</b> "
            f"(${expense.amount} {expense.currency})"
        )
        send_telegram_alert(message)

    elif monthly_total >= limit * 0.9:
        # Warn at 90% of budget
        percent = round((monthly_total / limit) * 100, 1)
        message = (
            f"<b>Budget Warning!</b>\n\n"
            f"Category   : <b>{category.name}</b>\n"
            f"Monthly Limit : <b>${limit}</b>\n"
            f"Total Spent   : <b>${round(monthly_total, 2)}</b>\n"
            f" Used          : <b>{percent}%</b>\n\n"
            f"You are approaching your budget limit!"
        )
        send_telegram_alert(message)