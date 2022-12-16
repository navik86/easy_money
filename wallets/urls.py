from django.urls import path

from wallets.views import (TransactionDetailView, TransactionListCreateView,
                           WalletDetailView, WalletListCreateView,
                           WalletTransactionsView)

urlpatterns = [
    path("wallets/", WalletListCreateView.as_view(), name="wallets_list"),
    path("wallets/<str:name>/", WalletDetailView.as_view(), name="specific_wallet"),
    path("transactions/", TransactionListCreateView.as_view()),
    path("transactions/<int:transaction_id>/", TransactionDetailView.as_view()),
    path("transactions/<str:wallet_name>/", WalletTransactionsView.as_view()),
]
