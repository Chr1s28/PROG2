from decimal import Decimal
from datetime import datetime, date, timedelta
from freezegun import freeze_time
import time

from P02.bank_account import BankAccount
from P02.saving_account import SavingAccount
from P02.youth_account import YouthAccount

class BankSimulation:
    """
    A simulation class to demonstrate the behavior of different bank accounts over time.
    """
    def __init__(self):
        # Create a regular bank account
        self.regular_account = BankAccount("CH1234567890")
        
        # Create a saving account
        self.saving_account = SavingAccount("CH9876543210")
        
        # Create a youth account for a 20-year-old person
        birth_date = date(datetime.now().year - 20, 1, 1)
        self.youth_account = YouthAccount("CH5432109876", birth_date)
        
        # Initial deposits
        self.regular_account.deposit("1000")
        self.saving_account.deposit("2000")
        self.youth_account.deposit("500")
        
        # Track simulation time
        self.start_date = datetime.now()
        self.current_date = self.start_date
        
    def print_account_status(self):
        """Print the current status of all accounts."""
        print(f"\n=== Account Status at {self.current_date.strftime('%Y-%m-%d %H:%M:%S')} ===")
        print(f"Regular Account: {self.regular_account.balance} {self.regular_account.currency}")
        print(f"Saving Account: {self.saving_account.balance} {self.saving_account.currency}")
        print(f"Youth Account: {self.youth_account.balance} {self.youth_account.currency}")
        
    def simulate_month(self):
        """Simulate the passage of one month."""
        # Move time forward by one month
        self.current_date += timedelta(days=30)
        
        # Apply monthly interest to accounts that support it
        self.saving_account.apply_monthly_interest()
        self.youth_account.apply_monthly_interest()
        
        print(f"\n>>> One month has passed. Now it's {self.current_date.strftime('%Y-%m-%d')}.")
        
    def run_simulation(self):
        """Run the bank account simulation."""
        print("Starting bank account simulation...")
        self.print_account_status()
        
        # Month 1: Just let interest accrue
        with freeze_time(self.current_date):
            self.simulate_month()
            self.print_account_status()
        
        # Month 2: Make some transactions
        with freeze_time(self.current_date):
            print("\n>>> Making some transactions...")
            self.regular_account.withdraw("200")
            self.saving_account.withdraw("2500")  # This will make the balance negative
            self.youth_account.withdraw("100")
            
            self.print_account_status()
            self.simulate_month()
            self.print_account_status()
        
        # Month 3: More transactions and interest
        with freeze_time(self.current_date):
            print("\n>>> Making more transactions...")
            self.regular_account.deposit("500")
            self.saving_account.deposit("1000")
            
            # Try to exceed youth account monthly withdrawal limit
            try:
                self.youth_account.withdraw("1900")
                self.youth_account.withdraw("200")  # This should fail
            except ValueError as e:
                print(f"Youth account error: {e}")
                
            self.print_account_status()
            self.simulate_month()
            self.print_account_status()
        
        # Month 4: Change interest rates
        with freeze_time(self.current_date):
            print("\n>>> Changing interest rates...")
            self.saving_account.set_interest_rate("0.002")  # 0.2%
            self.youth_account.set_interest_rate("0.025")   # 2.5%
            
            self.simulate_month()
            self.print_account_status()
        
        # Month 5: Final month
        with freeze_time(self.current_date):
            self.simulate_month()
            print("\n>>> Simulation complete. Final account status:")
            self.print_account_status()
            
            # Calculate total interest earned
            print("\n=== Total Interest Earned ===")
            print(f"Saving Account: {self.saving_account.balance - Decimal('500')} {self.saving_account.currency}")
            print(f"Youth Account: {self.youth_account.balance - Decimal('400')} {self.youth_account.currency}")


if __name__ == "__main__":
    simulation = BankSimulation()
    simulation.run_simulation()
