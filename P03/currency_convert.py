import os.path as op
import urllib.request
from datetime import date
from decimal import Decimal

# pip install CurrencyConverter
from currency_converter import ECB_URL, CurrencyConverter


class CustomCurrencyConverter(CurrencyConverter):
    """
    Custom currency converter that extends CurrencyConverter to simplify CHF conversions.

    :ivar filename: The name of the downloaded currency exchange rate file
    :type filename: str
    """

    def __init__(self):
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
