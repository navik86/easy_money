from wallets.models import Wallet
from alphabet_detector import AlphabetDetector



def test_create_wallet_name():
    """Testing wallet name with requirements"""
    wallet_name = Wallet.create_wallet_name()
    ad = AlphabetDetector()

    assert len(wallet_name) == 8
    assert any (char.isdigit() for char in wallet_name) == True
    assert ad.only_alphabet_chars(wallet_name, "LATIN") == True
    assert ad.only_alphabet_chars(wallet_name, "CYRILLIC") == False