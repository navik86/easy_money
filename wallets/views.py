from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from . import services
from .serializers import TransactionSerializer, WalletSerializer


class WalletListCreateView(GenericAPIView):
    """View handle GET, POST requests to list of wallet"""

    serializer_class = WalletSerializer

    def get(self, request):
        wallets = services.get_user_wallets(request.user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = WalletSerializer(data=request.data)
        if serializer.is_valid():
            services.create_wallet(self.request.user, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletDetailView(GenericAPIView):
    """View handle GET, DELETE requests to wallet"""

    serializer_class = WalletSerializer

    def get(self, request, name):
        wallet = services.get_specific_user_wallet(request.user, name)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    def delete(self, request, name):
        wallet = services.get_specific_user_wallet(request.user, name)
        services.delete_specific_wallet(wallet)
        return Response(f"Wallet {name} deleted", status=status.HTTP_204_NO_CONTENT)


class TransactionListCreateView(GenericAPIView):
    """View handle GET, POST requests to list of transaction"""

    serializer_class = TransactionSerializer

    def get(self, request):
        transaction = services.get_user_transactions(request.user)
        serializer = TransactionSerializer(transaction, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            services.create_transaction(self.request.user, serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(GenericAPIView):
    """View handle GET requests to transaction"""

    def get(self, request, transaction_id):
        transaction = services.get_specific_transaction(request.user, transaction_id)
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)


class WalletTransactionsView(GenericAPIView):
    """View handle GET requests to list of transaction specific wallet"""

    def get(self, request, wallet_name):
        transaction = services.get_wallet_transactions(request.user, wallet_name)
        serializer = TransactionSerializer(transaction, many=True)
        return Response(serializer.data)
