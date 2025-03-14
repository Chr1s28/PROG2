import random
import string
from datetime import date
from typing import Dict, List, Union

import bcrypt
from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table as RichTable

from .saving_account import SavingAccount
from .youth_account import YouthAccount


class ClientAccounts:
    """
    A class to manage multiple bank accounts for a client.

    This class provides functionality to create, manage, and interact with
    different types of bank accounts (SavingAccount and YouthAccount).

    :ivar accounts: Dictionary storing all client accounts
    :type accounts: Dict[str, Union[SavingAccount, YouthAccount]]
    :ivar current_account: Reference to the currently selected account
    :type current_account: Union[SavingAccount, YouthAccount, None]
    :ivar console: Rich console for formatted output
    :type console: Console
    :ivar account_owners: Dictionary mapping account names to lists of owners
    :type account_owners: Dict[str, List[str]]
    """

    def __init__(self) -> None:
        self.accounts: Dict[str, Union[SavingAccount, YouthAccount]] = {}
        self.current_account: Union[SavingAccount, YouthAccount, None] = None
        self.console: Console = Console()
        self.account_owners: Dict[str, List[str]] = {}

        password: str = Prompt.ask("Set password", password=True)
        self.password_hash: bytes = bcrypt.hashpw(
            bytes(password, encoding="utf-8"), b"$2b$12$lshujjHFpMf4uNenohn2tOjbvMkZeWzNniwEfeI0yjdCGqw29zvc."
        )

    def __check_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the stored hash.

        :param password: The password to verify
        :type password: str
        :return: True if password matches, False otherwise
        :rtype: bool
        """

        return bcrypt.checkpw(bytes(password, encoding="utf-8"), self.password_hash)

    def __display_accounts(self) -> None:
        """
        Display all accounts in a table format.

        Creates a rich table showing account details including name,
        type, IBAN, balance, status, and owners.
        """

        if not self.accounts:
            print("[yellow]No accounts available.[/yellow]")
            return

        table = RichTable(title="Your Accounts")
        table.add_column("Account Name")
        table.add_column("Account Type")
        table.add_column("IBAN")
        table.add_column("Balance")
        table.add_column("Status")
        table.add_column("Owners")

        for name, account in self.accounts.items():
            account_type = "Saving Account" if isinstance(account, SavingAccount) else "Youth Account"
            status = "Open" if account.opened else "Closed"
            owners = ", ".join(self.account_owners.get(name, ["Primary Owner"]))

            table.add_row(name, account_type, account.iban, f"{account.balance:.2f} {account.currency}", status, owners)

        self.console.print(table)

    def __manage_account(self) -> None:
        """
        Manage a selected account with various operations.

        Allows the user to perform operations on a selected account such as
        deposit, withdraw, check balance, change interest rate, etc.

        :raises ValueError: If operations fail due to account restrictions
        """

        if not self.accounts:
            print("[red]No accounts available to manage.[/red]")
            return

        self.__display_accounts()
        account_name = Prompt.ask("Choose an account", choices=list(self.accounts.keys()))
        self.current_account = self.accounts[account_name]

        while True:
            print(f"\n[bold]Managing: {account_name}[/bold]")
            print(f"Balance: {self.current_account.balance:.2f} {self.current_account.currency}")

            options = ["Deposit", "Withdraw", "Check Balance", "Change Interest Rate", "Apply Monthly Interest"]

            if self.current_account.opened:
                options.append("Close Account")
            else:
                options.append("Reopen Account")

            options.append("Add Owner")
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

                case "Check balance":
                    print(
                        f"[blue]Current balance: {self.current_account.balance:.2f} {self.current_account.currency}[/blue]"
                    )

                case "Change interest Rate":
                    try:
                        new_rate = Prompt.ask("Enter new interest rate (e.g., 0.01 for 1%)")
                        self.current_account.set_interest_rate(new_rate)
                        print(f"[green]Interest rate changed to {self.current_account.interest_rate}[/green]")
                    except ValueError as e:
                        print(f"[red]Error: {e}[/red]")

                case "Apply monthly interest":
                    self.current_account.apply_monthly_interest()
                    print(
                        f"[green]Monthly interest applied. New balance: {self.current_account.balance:.2f} {self.current_account.currency}[/green]"
                    )

                case "Close account":
                    confirm = Prompt.ask("Are you sure you want to close this account?", choices=["yes", "no"])
                    if confirm == "yes":
                        self.current_account.close()
                        print(f"[yellow]Account {account_name} has been closed.[/yellow]")

                case "Reopen account":
                    self.current_account.open()
                    print(f"[green]Account {account_name} has been reopened.[/green]")

                case "Add Owner":
                    self.__add_account_owner(account_name)

                case "Back to Main Menu":
                    self.current_account = None
                    break

    def __add_account_owner(self, account_name: str) -> None:
        """
        Add an additional owner to an account.

        :param account_name: The name of the account to add an owner to
        :type account_name: str
        """

        new_owner = Prompt.ask("Enter name of additional owner")

        if account_name not in self.account_owners:
            self.account_owners[account_name] = ["Primary Owner"]

        self.account_owners[account_name].append(new_owner)
        print(f"[green]{new_owner} added as owner to account {account_name}[/green]")

    def __add_account(self) -> None:
        """
        Add a new bank account.

        Creates either a SavingAccount or YouthAccount based on user input.
        Generates a random IBAN and prompts for necessary information.

        :raises ValueError: If account creation fails due to restrictions
        """

        option = Prompt.ask("Which type of account?", choices=["Saving account", "Youth account"])

        iban = "CH" + "".join(random.choices(string.digits, k=18)) + random.choice(string.ascii_uppercase)

        match option:
            case "Saving account":
                new_account = SavingAccount(iban)
                print("[green]Saving account created successfully[/green]")

            case "Youth account":
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

    def run(self) -> None:
        """
        Run the bank application.

        Main method that starts the application, handles authentication,
        and provides the main menu for account management.
        """

        password = Prompt.ask("Enter password", password=True)
        if self.__check_password(password):
            exit = False
        else:
            print("[red]Authentication failed![/red]")
            exit = True

        while not exit:
            print("\n[bold]Bank Application[/bold]")
            if self.accounts:
                print(f"You have {len(self.accounts)} account(s)")
            else:
                print("You have no accounts yet")

            option = Prompt.ask(
                "What would you like to do", choices=["Manage account", "Add account", "List accounts", "Exit"]
            )

            match option:
                case "Manage account":
                    self.__manage_account()
                case "Add account":
                    self.__add_account()
                case "List accounts":
                    self.__display_accounts()
                case "Exit":
                    exit = True


if __name__ == "__main__":
    client = ClientAccounts()
    client.run()
