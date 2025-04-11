from decimal import Decimal

# Using floats for calculations with currencies doesn't really make sense, as they aren't exact
# as we learned in PROG1 with the 0.1 + 0.2 example.
# After googling it turns out there's a builtin module called Decimal which is perfectly suitable for this excercise


class BankAccount:
    """
    A class to manage a bank account.

    This class provides functionality to create, manage, and interact with
    a bank account.

    :param iban: The IBAN of the bank account
    :type iban: str
    :param currency: The currency of the bank account
    :type currency: str
    :ivar _currency: The currency of the bank account
    :type _currency: str
    :ivar opened: Status of the account (open or closed)
    :type opened: bool
    :ivar balance: Current balance of the account
    :type balance: Decimal
    :ivar min_balance: Minimum balance allowed for the account
    :type min_balance: Decimal
    :ivar max_balance: Maximum balance allowed for the account
    :type max_balance: Decimal
    """

    def __init__(self, iban: str, currency: str = "CHF") -> None:

        self.iban = iban
        self._currency = currency
        self.opened = True
        self.balance = Decimal("0")
        self.min_balance = Decimal("0")
        self.max_balance = Decimal("100000")

    def __validate_transaction(self, amount: str | Decimal) -> Decimal:
        """
        Validate a transaction amount.

        :param amount: The amount to validate
        :type amount: str or Decimal
        :return: The validated amount as a Decimal
        :rtype: Decimal
        :raises ValueError: If the account is closed or the amount is not positive
        """

        if self.opened:
            if isinstance(amount, str):
                amount = Decimal(amount)
            if amount <= 0:
                raise ValueError("amount needs to be non-zero, positive number")
            return amount
        else:
            raise ValueError("Transactions not possible on closed account")

    @property
    def currency(self) -> str:
        """
        Get the currency of the bank account.

        :return: The currency of the bank account
        :rtype: str
        """

        return self._currency

    def deposit(self, amount: str | Decimal) -> None:
        """
        Deposit an amount into the account with all the necessary validators.

        :param amount: The amount to deposit
        :type amount: str or Decimal
        :raises ValueError: If the deposit would exceed the maximum balance
        """

        amount = self.__validate_transaction(amount)
        if self.balance + amount <= self.max_balance:
            self.balance += amount
        else:
            raise ValueError("Cannot deposit, maximum balance amount would be reached")

    def withdraw(self, amount: str | Decimal) -> None:
        """
        Withdraw an amount from the account with all the necessary validators.

        :param amount: The amount to withdraw
        :type amount: str or Decimal
        :raises ValueError: If the withdrawal would go below the minimum balance
        """

        amount = self.__validate_transaction(amount)
        if self.balance - amount >= self.min_balance:
            self.balance -= amount
        else:
            raise ValueError("Cannot withdraw, minimum balance amount would be reached")

    def close(self) -> None:
        """
        Close the account.
        """

        if self.opened:
            self.opened = False

    def open(self) -> None:
        """
        Open the account.
        """

        if not self.opened:
            self.opened = True
