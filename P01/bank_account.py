from decimal import Decimal

# Using floats for calculations with currencies doesn't really make sense, as they aren't exact
# as we learned in PROG1 with the 0.1 + 0.2 example.
# After googling it turns out there's a builtin module called Decimal which is perfectly suitable for this excercise


class BankAccount:
    def __init__(self, iban: str, currency: str = "CHF"):
        self.iban = iban
        self._currency = currency

        self.account_open = True
        self.balance = Decimal("0")
        self.min_balance = Decimal("0")
        self.max_balance = Decimal("100000")

    @property
    def currency(self) -> str:
        """This is to make a "private" attribute, although there is no such thing in python as self._currency can still be changed"""
        return self._currency

    def do_deposit(self, amount: str | Decimal) -> Decimal:
        """Deposit an amount into the acount with all the necessary validators. Note: We may want to abstract these validators in the future."""
        if self.account_open:
            if type(amount) is str:
                amount = Decimal(amount)
            if self.balance + amount <= self.max_balance:
                self.balance += amount
            else:
                raise ValueError("Cannot deposit, maximum balance amount would be reached")
        else:
            raise ValueError("Deposit not possible on closed account")

    def do_withdrawal(self, amount: str | Decimal) -> Decimal:
        """Withdraw an amount from the acount with all the necessary validators. Note: We may want to abstract these validators in the future."""
        if self.account_open:
            if type(amount) is str:
                amount = Decimal(amount)

            if self.balance - amount >= self.min_balance:
                self.balance -= amount
            else:
                raise ValueError("Cannot withdraw, minimum balance amount would be reached")
        else:
            raise ValueError("Withdrawal not possible on closed account")

    def close_account(self) -> None:
        """Closes the account, no method to reopen is provided as that has to be done by a bank teller"""
        if self.account_open:
            self.account_open = False


if __name__ == "__main__":
    my_account = BankAccount("CH1234567890")
    print(my_account.balance)
    print(my_account.currency)
    my_account.do_deposit("37.50")
    print(my_account.balance)
    my_account.do_withdrawal(Decimal(20))
    print(my_account.balance)
    my_account.close_account()
