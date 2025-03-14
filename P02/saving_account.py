from decimal import Decimal
import sys
import os

# Add the parent directory to sys.path to import from P02
from P02.bank_account import BankAccount

class SavingAccount(BankAccount):
    """
    A saving account that extends BankAccount with interest and allows negative balance.
    """
    def __init__(self, iban: str, currency: str = "CHF"):
        super().__init__(iban, currency)
        self.interest_rate = Decimal("0.001")
        self.min_balance = Decimal("-100000")
        
    def set_interest_rate(self, rate: str | Decimal) -> None:
        """
        Change the monthly interest rate.
        """
        if isinstance(rate, str):
            rate = Decimal(rate)
        if rate < 0:
            raise ValueError("Interest rate cannot be negative")
        self.interest_rate = rate
        
    def apply_monthly_interest(self) -> None:
        """Apply the monthly interest to the account balance."""
        if self.opened:
            interest = self.balance * self.interest_rate
            self.balance += interest
            
    def withdraw(self, amount: str | Decimal) -> Decimal:
        """
        Withdraw an amount from the account with all the necessary validators.
        Applies a 2% charge if balance is below zero after withdrawal.
        """
        amount = self._BankAccount__validate_transaction(amount)
        
        if self.balance - amount >= self.min_balance:
            self.balance -= amount
            
            if self.balance < 0:
                charge = abs(self.balance) * Decimal("0.02")
                self.balance -= charge
                
            return amount
        else:
            raise ValueError("Cannot withdraw, minimum balance amount would be reached")

if __name__ == "__main__":
    # Test the SavingAccount class
    saving_account = SavingAccount("CH9876543210")
    print(f"Initial balance: {saving_account.balance} {saving_account.currency}")
    
    # Deposit some money
    saving_account.deposit("1000")
    print(f"After deposit: {saving_account.balance} {saving_account.currency}")
    
    # Apply monthly interest
    saving_account.apply_monthly_interest()
    print(f"After interest: {saving_account.balance} {saving_account.currency}")
    
    # Withdraw more than the balance
    saving_account.withdraw("1100")
    print(f"After withdrawal (with negative balance): {saving_account.balance} {saving_account.currency}")
    
    # Change interest rate
    saving_account.set_interest_rate("0.002")  # Change to 0.2%
    print(f"New interest rate: {saving_account.interest_rate}")
