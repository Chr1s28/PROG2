from decimal import Decimal

# Using floats for calculations with currencies doesn't really make sense, as they aren't exact
# as we learned in PROG1 with the 0.1 + 0.2 example.
# After googling it turns out there's a builtin module called Decimal which is perfectly suitable for this excercise


class BankAccount:
    def __init__(self, iban: str, currency: str = "CHF"):
        self.iban = iban
        self._currency = currency
        self.opened = True
        self.balance = Decimal("0")
        self.min_balance = Decimal("0")
        self.max_balance = Decimal("100000")
    
    def __validate_transaction(self, amount: str | Decimal) -> Decimal:
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
        """This is to make a "private" attribute, although there is no such thing in python as self._currency can still be changed"""
        return self._currency

    def deposit(self, amount: str | Decimal) -> Decimal:
        """Deposit an amount into the acount with all the necessary validators."""
        amount = self.__validate_transaction(amount)
        if self.balance + amount <= self.max_balance:
            self.balance += amount
        else:
            raise ValueError("Cannot deposit, maximum balance amount would be reached")

    def withdraw(self, amount: str | Decimal) -> Decimal:
        """Withdraw an amount from the acount with all the necessary validators."""
        amount = self.__validate_transaction(amount)
        if self.balance - amount >= self.min_balance:
            self.balance -= amount
        else:
            raise ValueError("Cannot withdraw, minimum balance amount would be reached")

    def close(self) -> None:
        """Closes the account"""
        if self.opened:
            self.opened = False
    
    def open(self) -> None:
        """Opens the account"""
        if not self.opened:
            self.opened = True


if __name__ == "__main__":
    my_account = BankAccount("CH1234567890")
    print(my_account.balance)
    print(my_account.currency)
    my_account.deposit("37.50")
    print(my_account.balance)
    my_account.withdraw(Decimal(-20)) 
    print(my_account.balance)
    my_account.close()
