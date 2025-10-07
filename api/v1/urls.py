from django.urls import path, include

urlpatterns = [
    path("accounts/", include("apps.accounts.urls")),
    path("assets/", include("apps.assets.urls")),
    path("budget/", include("apps.budget.urls")),
    path("documents/", include("apps.documents.urls")),
    path("expense/", include("apps.expense.urls")),
    path("income/", include("apps.income.urls")),
    path("journal/", include("apps.journal.urls")),
    path("reports/", include("apps.reports.urls"))
]
