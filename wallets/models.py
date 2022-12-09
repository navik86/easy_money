from django.db import models
from django.conf import settings


User = settings.AUTH_USER_MODEL


CARDS = [('Visa', 'Visa'), ('Mastercard', 'Mastercard')]
CURRENCIES = [("USD", "USD"), ("EUR", "EUR"), ("RUB", "RUB")]
STATUSES = [("PAID", "PAID"), ("FAILED", "FAILED")]


class Wallet(models.Model):

    name = models.CharField(max_length=8,unique=True)
    type = models.CharField(choices=CARDS, max_length=20)
    currency = models.CharField(choices=CURRENCIES, max_length=3)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_on = models.DateField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ["modified_on"]

    def __str__(self):
        return f"Owner: {self.owner}, wallet: {self.name}"


class Transaction(models.Model):
    
    sender = models.ForeignKey(Wallet, related_name="senders", on_delete=models.RESTRICT)
    receiver = models.ForeignKey(Wallet, related_name="receivers", on_delete=models.RESTRICT)
    transfer_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.10)
    commision = models.DecimalField(max_digits=10, decimal_places=2, default=0.10)
    status = models.CharField(max_length=10, choices=STATUSES)
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Transaction: {self.pk}; sender: {self.sender}; receiver: {self.receiver}"
