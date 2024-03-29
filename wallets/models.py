import random
import string

from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL


CARDS = [("Visa", "Visa"), ("Mastercard", "Mastercard")]
CURRENCIES = [("USD", "USD"), ("EUR", "EUR"), ("RUB", "RUB")]
STATUSES = [("PAID", "PAID"), ("FAILED", "FAILED")]
WALLET_NAME_LENGTH = 8
MAX_NUMBER_OF_WALLETS = 5
BONUSES = {"USD": 3.00, "EUR": 3.00, "RUB": 100.00}
DEFAULT_COMMISSION = 0.10


class Wallet(models.Model):
    """Wallet model"""

    name = models.CharField(max_length=8, unique=True)
    type = models.CharField(choices=CARDS, max_length=20)
    currency = models.CharField(choices=CURRENCIES, max_length=3)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["modified_on"]

    def __str__(self) -> str:
        return f"Owner: {self.owner}, wallet: {self.name}"

    @classmethod
    def create_wallet_name(cls) -> str:
        name = "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(WALLET_NAME_LENGTH)
        )
        return name


class Transaction(models.Model):
    """Transaction model"""

    sender = models.ForeignKey(Wallet, related_name="senders", on_delete=models.CASCADE)
    receiver = models.ForeignKey(
        Wallet, related_name="receivers", on_delete=models.CASCADE
    )
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.10)
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0.10)
    status = models.CharField(max_length=10, choices=STATUSES)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return (
            f"Transaction: {self.pk}; sender: {self.sender}; receiver: {self.receiver}"
        )
