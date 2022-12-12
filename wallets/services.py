import decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.http import Http404

from .models import (BONUSES, DEFAULT_COMMISSION, MAX_NUMBER_OF_WALLETS,
                     Transaction, Wallet)


def get_user_wallets(user):
    return Wallet.objects.filter(owner=user)


def create_wallet(validated_data, user):
    
    count = Wallet.objects.filter(owner=user).count()

    if count >= MAX_NUMBER_OF_WALLETS:
        raise ValidationError(
            f"You can't have more than {MAX_NUMBER_OF_WALLETS} wallets"
        )

    name = Wallet.create_wallet_name()

    wallet = Wallet.objects.create(
        name=name,
        **validated_data,
        balance=BONUSES[validated_data["currency"]],
        owner=user
    )
    return wallet


def get_specific_wallet(name):
    try:
        return Wallet.objects.get(name=name)
    except Wallet.DoesNotExist:
        raise Http404


def create_transaction(validated_data):

    sender = validated_data["sender"]
    receiver = validated_data["receiver"]

    if sender.user == receiver.user:
        commission = 0.00
    else:
        commission = DEFAULT_COMMISSION

    ratio = round(decimal.Decimal(1.00 + commission), 2)

    transfer_amount_with_fee = validated_data["transfer_amount"] * ratio

    transaction_ = Transaction.objects.create(
        sender=sender,
        receiver=receiver,
        commission=commission,
        transfer_amount=validated_data["transfer_amount"],
        status="FAILED",
    )

    with transaction.atomic():
        sender.balance = sender.balance - transfer_amount_with_fee
        sender.save()
        receiver.balance = receiver.balance + validated_data["transfer_amount"]
        receiver.save()
        transaction_.status = "PAID"
        transaction_.save()

    return transaction_


def get_user_transactions(user):
    user_wallets = user.wallet_set.all()
    user_transactions = Transaction.objects.filter(
        Q(receiver__in=user_wallets) | Q(sender__in=user_wallets)
    )
    return user_transactions


def get_specific_transaction(id):
    try:
        return Transaction.objects.get(id=id)
    except Transaction.DoesNotExist:
        raise Http404


def get_wallet_transactions(name):
    wallet = get_specific_wallet(name)
    wallet_transactions = Transaction.objects.filter(
        Q(receiver__name=wallet.name) | Q(sender__name=wallet.name)
    )
    return wallet_transactions
    