import os.path as op
import urllib.request
from datetime import date
from decimal import Decimal

from currency_converter import ECB_URL, CurrencyConverter

class CustomCurrencyConverter(CurrencyConverter):
    def __init__(self):
        filename = f"ecb_{date.today():%Y%m%d}.zip"
        if not op.isfile(filename):
            urllib.request.urlretrieve(ECB_URL, filename)
        super().__init__(currency_file=filename, decimal=True)
    
    def convert_to_chf(self, amount: Decimal, source_curr: str) -> Decimal:
        return self.convert(amount, currency=source_curr,  new_currency="CHF")
    

if __name__ == "__main__":
    c = CustomCurrencyConverter()
    c.convert_to_chf(1, "USD")