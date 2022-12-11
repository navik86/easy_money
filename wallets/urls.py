from django.urls import path
from wallets.views import WalletListCreateView


urlpatterns = [
    path('', WalletListCreateView.as_view(), name="wallets_list"),
    # path('<str:name>/', ),
    # path('transactions/', ),
    # path('transactions/<int:transaction_id>/', ),
    # path('transactions/<str:wallet_name>/', ),
]
