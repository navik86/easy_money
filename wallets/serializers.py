from rest_framework import serializers
from .models import Wallet, CARDS, CURRENCIES


class WalletSerializer(serializers.ModelSerializer):

    type = serializers.CharField(max_length=10)
    currency = serializers.CharField(max_length=3)

    class Meta:
        model = Wallet
        fields = '__all__'
        read_only_fields = ("name", "balance", "owner")

    def validate(self, data):
        if data["type"] not in ["Visa", "Mastercard"]:
            raise serializers.ValidationError(
                f"{data['type']} wrong choice for wallet type. "
                f"Please choose Visa or Mastercard."
            )
        if data["currency"] not in ["USD", "EUR", "RUB"]:
            raise serializers.ValidationError(
                f"{data['currency']} wrong choice for wallet currency. "
                f"Please choose USD, EUR or RUB."
            )
        return data

        