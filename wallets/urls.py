from django.urls import path

from wallets.views import WalletDetailView, WalletListCreateView

urlpatterns = [
    path('', WalletListCreateView.as_view(), name="wallets_list"),
    path('<str:name>/', WalletDetailView.as_view(), name="specific_wallet"),
    # path('transactions/', ),
    # path('transactions/<int:transaction_id>/', ),
    # path('transactions/<str:wallet_name>/', ),
]
