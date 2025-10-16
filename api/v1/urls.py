from django.urls import include, path

urlpatterns = [
    path('accounts/', include('apps.accounts.urls')),
    path('income/', include('apps.income.urls')),
    path('expense/', include('apps.expense.urls')),
]