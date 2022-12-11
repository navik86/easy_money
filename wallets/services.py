from .models import Wallet, WALLET_NAME_LENGTH, MAX_NUMBER_OF_WALLETS, BONUSES
from django.core.exceptions import ValidationError


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