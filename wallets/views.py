from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from . import services
from .serializers import TransactionSerializer, WalletSerializer


class WalletListCreateView(GenericAPIView):

    serializer_class = WalletSerializer

    def get(self, request, format=None):
        wallets = services.get_user_wallets(self.request.user)
        serializer = WalletSerializer(wallets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WalletSerializer(data=request.data)
        if serializer.is_valid():
            services.create_wallet(serializer.validated_data, self.request.user)   	
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WalletDetailView(GenericAPIView):

    serializer_class = WalletSerializer

    def get(self, request, name, format=None):
        wallet = services.get_specific_wallet(name)
        serializer = WalletSerializer(wallet)
        return Response(serializer.data)

    def delete(self, request, name, format=None):
        wallet = services.get_specific_wallet(name)
        wallet.delete()
        return Response(f"Wallet {name} deleted", status=status.HTTP_204_NO_CONTENT)


class TransactionListCreateView(GenericAPIView):

    serializer_class = TransactionSerializer

    def get(self, request, format=None):
        transaction = services.get_user_transactions(self.request.user)
        serializer = TransactionSerializer(transaction, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WalletSerializer(data=request.data)
        if serializer.is_valid():
            services.create_transaction(serializer.validated_data)   	
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(GenericAPIView):
    pass


class WalletTransactionsView(GenericAPIView):
    pass