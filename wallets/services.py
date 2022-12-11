from django.core.exceptions import ValidationError
from django.http import Http404

from .models import BONUSES, MAX_NUMBER_OF_WALLETS, WALLET_NAME_LENGTH, Wallet


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
