from datetime import datetime, date, timedelta
from freezegun import freeze_time

from saving_account import SavingAccount
from youth_account import YouthAccount

class BankSimulation:
    """
    A simulation class to demonstrate the two types of bank accounts over time.
    """
    def __init__(self):
        self.saving_account = SavingAccount("CH9876543210")
        
        birth_date = date(datetime.now().year - 20, 1, 1)
        self.youth_account = YouthAccount("CH5432109876", birth_date)
        
        self.saving_account.deposit("2000")
        self.youth_account.deposit("500")
        
        self.current_date = datetime.now()
        
    def print_account_status(self):
        """Print the current status of all accounts."""
        print(f"=== Account Status at {self.current_date.strftime('%Y-%m-%d')} ===")
        print(f"Saving Account: {self.saving_account.balance} {self.saving_account.currency}")
        print(f"Youth Account: {self.youth_account.balance} {self.youth_account.currency}")
        
    def simulate_month(self):
        """Simulate the passage of one month."""
        self.current_date += timedelta(days=30)
        
        self.saving_account.apply_monthly_interest()
        self.youth_account.apply_monthly_interest()
        
        print(f"\nOne month has passed, new date: {self.current_date.strftime('%Y-%m-%d')}")
        
    def run_simulation(self):
        """Run the bank account simulation."""
        print("Starting bank account simulation...")
        self.print_account_status()
        
        # Month 1
        with freeze_time(self.current_date):
            self.simulate_month()
            self.print_account_status()
        
        # Month 2
        with freeze_time(self.current_date):
            print("\nMaking some transactions...")
            self.saving_account.withdraw("2500")
            self.youth_account.withdraw("100")
            
            self.print_account_status()
            self.simulate_month()
            self.print_account_status()
        
        # Month 3
        with freeze_time(self.current_date):
            print("\nMaking more transactions...")
            self.saving_account.deposit("1000")
            
            try:
                self.youth_account.withdraw("1900")
                self.youth_account.withdraw("200")
            except ValueError as e:
                print(f"Youth account error: {e}")
                
            self.print_account_status()
            self.simulate_month()
            self.print_account_status()
        
        # Month 4
        with freeze_time(self.current_date):
            print("\nChanging interest rates...")
            self.saving_account.set_interest_rate("0.002")
            self.youth_account.set_interest_rate("0.025")
            
            self.simulate_month()
            self.print_account_status()
        
        # Month 5
        with freeze_time(self.current_date):
            self.simulate_month()
            print("\nSimulation complete. Final account status:")
            self.print_account_status()


if __name__ == "__main__":
    simulation = BankSimulation()
    simulation.run_simulation()
