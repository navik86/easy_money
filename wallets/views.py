from rest_framework.generics import GenericAPIView
from .serializers import WalletSerializer
import services
from rest_framework.response import Response
from rest_framework import status


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


