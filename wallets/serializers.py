import decimal

from rest_framework import serializers
from rest_framework.exceptions import NotFound

from . import services
from .models import DEFAULT_COMMISSION, WALLET_NAME_LENGTH, Transaction, Wallet


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


class TransactionSerializer(serializers.ModelSerializer):

    receiver = serializers.CharField(
        source="receiver.name", max_length=WALLET_NAME_LENGTH
    )
    sender = serializers.CharField(
        source="sender.name", max_length=WALLET_NAME_LENGTH
    )
    transfer_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, default=0.10
    )
    
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ("id", "status", "commission")

    def validate(self, data):
 
        receiver = services.get_specific_wallet(data["receiver"]["name"])
        sender = services.get_specific_wallet(data["sender"]["name"])

        if not receiver:
            raise NotFound(detail="Receiver wallet doesn't exist", code=404)
        if not sender:
            raise NotFound(detail="Sender wallet doesn't exist", code=404)

        if sender.currency != receiver.currency:
            raise serializers.ValidationError("Currencies of wallets are not equal")

        ratio = round(decimal.Decimal(1.00 + DEFAULT_COMMISSION), 2)
        text_exep = "Sender wallet doesn't have enough funds for transaction"

        if sender.user == receiver.user:
            if sender.balance < data["transfer_amount"]:
                raise serializers.ValidationError(text_exep)
        else:
            if sender.balance < data["transfer_amount"] * ratio:
                raise serializers.ValidationError(text_exep)

        data["receiver"] = receiver
        data["sender"] = sender

        return data
