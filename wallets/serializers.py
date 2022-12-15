import decimal

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from . import services
from .models import DEFAULT_COMMISSION, WALLET_NAME_LENGTH, Transaction, Wallet


class WalletSerializer(serializers.ModelSerializer):
    """Serializer for wallet validation"""

    type = serializers.CharField(max_length=10)
    currency = serializers.CharField(max_length=3)

    class Meta:
        model = Wallet
        fields = "__all__"
        read_only_fields = ("name", "balance", "owner")

    def validate(self, attrs):
        if attrs["type"] not in ["Visa", "Mastercard"]:
            raise serializers.ValidationError(
                f"{attrs['type']} wrong choice for wallet type. "
                f"Please choose Visa or Mastercard."
            )
        if attrs["currency"] not in ["USD", "EUR", "RUB"]:
            raise serializers.ValidationError(
                f"{attrs['currency']} wrong choice for wallet currency. "
                f"Please choose USD, EUR or RUB."
            )
        return attrs


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction validation"""

    receiver = serializers.CharField(
        source="receiver.name", max_length=WALLET_NAME_LENGTH
    )
    sender = serializers.CharField(source="sender.name", max_length=WALLET_NAME_LENGTH)

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ("id", "status", "commission")

    def validate(self, attrs):
        receiver = services.get_specific_wallet(attrs["receiver"]["name"])
        sender = services.get_specific_wallet(attrs["sender"]["name"])

        if not receiver:
            raise NotFound(detail="Receiver wallet doesn't exist", code=404)
        if not sender:
            raise NotFound(detail="Sender wallet doesn't exist", code=404)

        if sender.currency != receiver.currency:
            raise serializers.ValidationError("Currencies of wallets are not equal")

        ratio = round(decimal.Decimal(1.00 + DEFAULT_COMMISSION), 2)
        text_exep = "Sender wallet doesn't have enough funds for transaction"

        if sender.owner == receiver.owner:
            if sender.balance < attrs["transfer_amount"]:
                raise serializers.ValidationError(text_exep)
        else:
            if sender.balance < attrs["transfer_amount"] * ratio:
                raise serializers.ValidationError(text_exep)

        attrs["receiver"] = receiver
        attrs["sender"] = sender

        return attrs
