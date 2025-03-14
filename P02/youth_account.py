from decimal import Decimal
from datetime import datetime, date

from bank_account import BankAccount

class YouthAccount(BankAccount):
    """
    A youth account that extends BankAccount with higher interest rate,
    age restriction and monthly withdrawal limit.
    """
    def __init__(self, iban: str, birth_date: date, currency: str = "CHF"):
        """
        Initialize a youth account with age verification.
        """
        super().__init__(iban, currency)
        
        today = datetime.now().date()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age > 25:
            raise ValueError("Youth accounts can only be opened by person aged 25 or younger")
            
        self.birth_date = birth_date
        self.interest_rate = Decimal("0.02")  # 2% monthly interest
        self.monthly_withdraw_limit = Decimal("2000")
        self.withdraw_this_month = Decimal("0")
        self.last_withdraw_month = datetime.now().month
        
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
        Withdraw an amount from the account with monthly limit check.
        """
        amount = self._BankAccount__validate_transaction(amount)
        
        current_month = datetime.now().month
        if current_month != self.last_withdraw_month:
            self.withdraw_this_month = Decimal("0")
            self.last_withdraw_month = current_month
            
        if self.withdraw_this_month + amount > self.monthly_withdraw_limit:
            raise ValueError(f"Monthly withdrawal limit of {self.monthly_withdraw_limit} {self.currency} exceeded")
            
        if self.balance - amount >= self.min_balance:
            self.balance -= amount
            self.withdraw_this_month += amount
            return amount
        else:
            raise ValueError("Cannot withdraw, minimum balance amount would be reached")

if __name__ == "__main__":
    # Test the YouthAccount class
    # Create a youth account for a 20-year-old person
    birth_date = date(datetime.now().year - 20, 1, 1)
    youth_account = YouthAccount("CH9876543210", birth_date)
    print(f"Initial balance: {youth_account.balance} {youth_account.currency}")
    
    # Deposit some money
    youth_account.deposit("5000")
    print(f"After deposit: {youth_account.balance} {youth_account.currency}")
    
    # Apply monthly interest
    youth_account.apply_monthly_interest()
    print(f"After interest: {youth_account.balance} {youth_account.currency}")
    
    # Try to withdraw within the monthly limit
    youth_account.withdraw("1500")
    print(f"After withdrawal: {youth_account.balance} {youth_account.currency}")
    print(f"Withdrawn this month: {youth_account.withdraw_this_month} {youth_account.currency}")
    
    try:
        # Try to withdraw more than the monthly limit
        youth_account.withdraw("1000")
    except ValueError as e:
        print(f"Error: {e}")
        
    # Change interest rate
    youth_account.set_interest_rate("0.025")  # Change to 2.5%
    print(f"New interest rate: {youth_account.interest_rate}")
    
    # Try to create an account for someone older than 25
    try:
        old_birth_date = date(datetime.now().year - 30, 1, 1)
        old_account = YouthAccount("CH1234567890", old_birth_date)
    except ValueError as e:
        print(f"Error: {e}")
