import os.path as op
import urllib.request
from datetime import date
from decimal import Decimal

from currency_converter import ECB_URL, CurrencyConverter

class CustomCurrencyConverter(CurrencyConverter):
    """
    A custom currency converter that extends CurrencyConverter to simplify CHF conversions.
    
    This class automatically downloads the latest ECB exchange rates if needed
    and provides a convenient method to convert any currency to Swiss Francs (CHF).
    
    :ivar filename: The name of the downloaded currency exchange rate file
    :type filename: str
    """
    def __init__(self):
        """
        Initialize the CustomCurrencyConverter.
        
        Downloads the latest ECB exchange rates if not already present
        and configures the converter to use Decimal for precise calculations.
        """
        filename = f"ecb_{date.today():%Y%m%d}.zip"
        if not op.isfile(filename):
            urllib.request.urlretrieve(ECB_URL, filename)
        super().__init__(currency_file=filename, decimal=True)
    
    def convert_to_chf(self, amount: Decimal, source_curr: str) -> Decimal:
        """
        Convert an amount from a source currency to Swiss Francs (CHF).
        
        :param amount: The amount to convert
        :type amount: Decimal
        :param source_curr: The source currency code (e.g., 'USD', 'EUR')
        :type source_curr: str
        :return: The equivalent amount in CHF
        :rtype: Decimal
        """
        return self.convert(amount, currency=source_curr, new_currency="CHF")
    

if __name__ == "__main__":
    c = CustomCurrencyConverter()
    c.convert_to_chf(1, "USD")
