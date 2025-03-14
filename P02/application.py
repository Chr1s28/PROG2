from rich import print
from rich.prompt import Prompt
from rich.console import Console
from rich.table import Table as RichTable
import bcrypt
from datetime import datetime, date
from decimal import Decimal

from saving_account import SavingAccount
from youth_account import YouthAccount

salt = b'$2b$12$lshujjHFpMf4uNenohn2tOjbvMkZeWzNniwEfeI0yjdCGqw29zvc.'

class ClientAccounts:
    def __init__(self):
        self.accounts = {}
        self.current_account = None
        self.console = Console()
        self.account_owners = {}  # Dictionary to track account owners/mandataries

        password = Prompt.ask("Set password", password=True)
        self.password_hash = bcrypt.hashpw(bytes(password, encoding="utf-8"), salt)
    
    def __check_password(self, password: str) -> bool:
        return bcrypt.checkpw(bytes(password, encoding="utf-8"), self.password_hash)

    def __display_accounts(self):
        """Display all accounts in a table format"""
        if not self.accounts:
            print("[yellow]No accounts available.[/yellow]")
            return
            
        table = RichTable(title="Your Accounts")
        table.add_column("Account Name")
        table.add_column("Account Type")
        table.add_column("IBAN")
        table.add_column("Balance")
        table.add_column("Status")
        table.add_column("Owners/Mandataries")
        
        for name, account in self.accounts.items():
            account_type = "Saving Account" if isinstance(account, SavingAccount) else "Youth Account"
            status = "Open" if account.opened else "Closed"
            owners = ", ".join(self.account_owners.get(name, ["Primary Owner"]))
            
            table.add_row(
                name,
                account_type,
                account.iban,
                f"{account.balance:.2f} {account.currency}",
                status,
                owners
            )
            
        self.console.print(table)

    def __manage_account(self):
        """Manage a selected account with various operations"""
        if not self.accounts:
            print("[red]No accounts available to manage.[/red]")
            return
            
        self.__display_accounts()
        account_name = Prompt.ask("Choose an account", choices=list(self.accounts.keys()))
        self.current_account = self.accounts[account_name]
        
        while True:
            print(f"\n[bold]Managing: {account_name}[/bold]")
            print(f"Balance: {self.current_account.balance:.2f} {self.current_account.currency}")
            
            options = ["Deposit", "Withdraw", "Check Balance", "Account Details"]
            
            # Add account-specific options
            if isinstance(self.current_account, SavingAccount) or isinstance(self.current_account, YouthAccount):
                options.append("Change Interest Rate")
                options.append("Apply Monthly Interest")
                
            if self.current_account.opened:
                options.append("Close Account")
            else:
                options.append("Reopen Account")
                
            options.append("Add Owner/Mandatary")
            options.append("Back to Main Menu")
            
            action = Prompt.ask("What would you like to do", choices=options)
            
            match action:
                case "Deposit":
                    try:
                        amount = Prompt.ask("Enter amount to deposit")
                        self.current_account.deposit(amount)
                        print(f"[green]Successfully deposited {amount} {self.current_account.currency}[/green]")
                    except ValueError as e:
                        print(f"[red]Error: {e}[/red]")
                        
                case "Withdraw":
                    try:
                        amount = Prompt.ask("Enter amount to withdraw")
                        self.current_account.withdraw(amount)
                        print(f"[green]Successfully withdrew {amount} {self.current_account.currency}[/green]")
                    except ValueError as e:
                        print(f"[red]Error: {e}[/red]")
                        
                case "Check Balance":
                    print(f"[blue]Current balance: {self.current_account.balance:.2f} {self.current_account.currency}[/blue]")
                    
                case "Account Details":
                    self.__display_account_details(account_name)
                    
                case "Change Interest Rate":
                    try:
                        new_rate = Prompt.ask("Enter new interest rate (e.g., 0.01 for 1%)")
                        self.current_account.set_interest_rate(new_rate)
                        print(f"[green]Interest rate changed to {self.current_account.interest_rate}[/green]")
                    except ValueError as e:
                        print(f"[red]Error: {e}[/red]")
                        
                case "Apply Monthly Interest":
                    self.current_account.apply_monthly_interest()
                    print(f"[green]Monthly interest applied. New balance: {self.current_account.balance:.2f} {self.current_account.currency}[/green]")
                    
                case "Close Account":
                    confirm = Prompt.ask("Are you sure you want to close this account?", choices=["yes", "no"])
                    if confirm == "yes":
                        self.current_account.close()
                        print(f"[yellow]Account {account_name} has been closed.[/yellow]")
                        
                case "Reopen Account":
                    self.current_account.open()
                    print(f"[green]Account {account_name} has been reopened.[/green]")
                    
                case "Add Owner/Mandatary":
                    self.__add_account_owner(account_name)
                    
                case "Back to Main Menu":
                    self.current_account = None
                    break

    def __display_account_details(self, account_name):
        """Display detailed information about an account"""
        account = self.accounts[account_name]
        
        print(f"\n[bold]Account Details for {account_name}[/bold]")
        print(f"IBAN: {account.iban}")
        print(f"Currency: {account.currency}")
        print(f"Balance: {account.balance:.2f}")
        print(f"Status: {'Open' if account.opened else 'Closed'}")
        
        if isinstance(account, SavingAccount):
            print(f"Account Type: Saving Account")
            print(f"Interest Rate: {account.interest_rate}")
            print(f"Minimum Balance: {account.min_balance}")
            
        elif isinstance(account, YouthAccount):
            print(f"Account Type: Youth Account")
            print(f"Interest Rate: {account.interest_rate}")
            print(f"Monthly Withdrawal Limit: {account.monthly_withdraw_limit}")
            print(f"Withdrawn This Month: {account.withdraw_this_month}")
            
        print(f"Owners/Mandataries: {', '.join(self.account_owners.get(account_name, ['Primary Owner']))}")

    def __add_account_owner(self, account_name):
        """Add an additional owner or mandatary to an account"""
        new_owner = Prompt.ask("Enter name of additional owner/mandatary")
        
        if account_name not in self.account_owners:
            self.account_owners[account_name] = ["Primary Owner"]
            
        self.account_owners[account_name].append(new_owner)
        print(f"[green]{new_owner} added as owner/mandatary to account {account_name}[/green]")

    def __add_account(self):
        """Add a new bank account"""
        option = Prompt.ask("Which type of account?", choices=["Saving account", "Youth account"])
        
        iban = Prompt.ask("Enter IBAN for the account")
        
        try:
            match option:
                case "Saving account":
                    new_account = SavingAccount(iban)
                    print("[green]Saving account created successfully[/green]")
                    
                case "Youth account":
                    # Get birth date for youth account
                    year = int(Prompt.ask("Enter birth year"))
                    month = int(Prompt.ask("Enter birth month (1-12)"))
                    day = int(Prompt.ask("Enter birth day (1-31)"))
                    
                    try:
                        birth_date = date(year, month, day)
                        new_account = YouthAccount(iban, birth_date)
                        print("[green]Youth account created successfully[/green]")
                    except ValueError as e:
                        print(f"[red]Error creating youth account: {e}[/red]")
                        return
            
            name_option = Prompt.ask("Name of account")
            if name_option in self.accounts:
                print("[red]An account with this name already exists. Please choose a different name.[/red]")
                return
                
            self.accounts[name_option] = new_account
            
            # Initialize deposit
            initial_deposit = Prompt.ask("Enter initial deposit amount (or 0 for no deposit)")
            if initial_deposit != "0":
                try:
                    new_account.deposit(initial_deposit)
                    print(f"[green]Successfully deposited {initial_deposit} {new_account.currency}[/green]")
                except ValueError as e:
                    print(f"[red]Error with initial deposit: {e}[/red]")
                    
        except Exception as e:
            print(f"[red]Error creating account: {e}[/red]")
    
    def run(self) -> None:
        """Run the bank account management application"""
        password = Prompt.ask("Enter password", password=True)
        if self.__check_password(password):
            exit = False
            print("[green]Authentication successful![/green]")
        else:
            print("[red]Authentication failed![/red]")
            exit = True

        while not exit:
            print("\n[bold]Bank Account Management System[/bold]")
            if self.accounts:
                print(f"You have {len(self.accounts)} account(s)")
            else:
                print("You have no accounts yet")
                
            option = Prompt.ask("What would you like to do", 
                               choices=["Manage account", "Add account", "List accounts", "Exit"])
            
            match option:
                case "Manage account":
                    self.__manage_account()
                case "Add account":
                    self.__add_account()
                case "List accounts":
                    self.__display_accounts()
                case "Exit":
                    print("[yellow]Thank you for using the Bank Account Management System![/yellow]")
                    exit = True


if __name__ == "__main__":
    print("[bold blue]Welcome to the Bank Account Management System[/bold blue]")
    client = ClientAccounts()
    client.run()
