
# Expense Tracker API

A robust RESTful API for managing personal expenses, featuring JWT authentication, multi-currency support, automated budget alerts, and advanced filtering capabilities.
## end point collection
* ** http://127.0.0.1:8000/swagger/ 
## 🚀 Features added 

### 1. Authentication
* **Overview:** Secure user registration and session management using JWT.
* **Design Decisions:** Implemented `rest_framework_simplejwt` for stateless, token-based authentication.
* **API Changes:** `POST /register/`, `POST /login/`.

### 2. Currency Conversion
* **Overview:** Dynamically convert expense totals into various base currencies.
* **Design Decisions:** Centralized `currency.py` utility for decoupling conversion logic.
* **API Changes:** `GET /expenses/summary/?base_currency=EUR`.

### 3. Automated Email Alerts instead of telegram bot 
* **Overview:** Professional notifications sent to users when they exceed their monthly category budget.
* **Assumptions:** User email is captured during registration.

### 4. Favorite Categories
* **Overview:** Allows users to mark frequently used categories as "Favorites."
* **Design Decisions:** Added `is_favorite` boolean field to the `Category` model.
* **API Changes:** `PATCH /categories/{id}/` to toggle status.

### 5. Advanced Search & Filtering
* **Overview:** Granular control over expense queries using date ranges and keyword searches.
* **Design Decisions:** Implemented custom filtering within the `ExpenseViewSet` query construction.
* **API Changes:** `GET /expenses/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&search=keyword`.

---

## 🐛 Bugs Found and Fixed

| Description | Root Cause | Fix | Commit Hash |
| :--- | :--- | :--- | :--- |
| **Sum Function Import Error** | `Sum` was not imported from `django.db.models`. | Added missing import statement in `views.py`. | `fix001` |
| **Search Field Logic** | Search queries were not correctly filtering the queryset. | Refactored `get_queryset` to properly handle query parameters. | `fix002` |
| **Date Query Filter** | Incorrect filter lookups (e.g., `date__gte` usage). | Corrected field lookups for date range filtering. | `fix003` |
| **Category Serializer Typo** | Field name typo caused serialization failures. | Corrected the field mapping in `CategorySerializer`. | `fix004` |
| **Incomplete CRUD** | Missing `ViewSet` actions for specific model operations. | Implemented full `ModelViewSet` methods for standard CRUD. | `fix005` |

---

## 🛠 Tech Stack
* **Framework:** Django REST Framework
* **Auth:** SimpleJWT
* **Database:** SQLite
* **Mail:** Django Core Mail

## 🛠 Getting Started

Follow these steps to set up the project on your local machine.

### Prerequisites
* Ensure you have [uv](https://github.com/astral-sh/uv) installed on your system.
* Ensure you have Python 3.12 or higher installed.

### Setup Steps
```bash
# Clone the repository
git clone [https://github.com/suyog123-hub/expense-tracker-api.git](https://github.com/suyog123-hub/expense-tracker-api.git)
cd expense-tracker-api

# Create virtual environment and install dependencies
uv sync

# Configure environment variables
cp .env.example .env
# Edit the .env file and update your SECRET_KEY and email settings

# Run database migrations
uv run python manage.py migrate

# Start the development server
uv run python manage.py runserver
