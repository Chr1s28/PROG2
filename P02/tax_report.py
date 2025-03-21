from rich.table import Table as RichTable
from datetime import datetime


class TaxReport:
    """
    Static class to generate a tax report for the bank application.
    """

    @staticmethod
    def generate(bank_application) -> None:
        """
        Static method to generate a tax report for the bank application.
        """

        if bank_application.accounts:
            bank_application.console.print(f"\n[bold]Tax Report {datetime.now().year} for Fiscal Year {datetime.now().year - 1}[/bold]\n", style="underline")
            bank_application.display_accounts()

            currency_totals = {}
            for account in bank_application.accounts.values():
                currency_totals[account.currency] = currency_totals.get(account.currency, 0) + account.balance

            # Create a table for total wealth grouped by currency
            currency_table = RichTable(title="Total Wealth by Currency", title_justify="left")
            currency_table.add_column("Currency")
            currency_table.add_column("Total Amount")

            for currency, total in currency_totals.items():
                currency_table.add_row(currency, f"{total:.2f}")

            bank_application.console.print(currency_table)
        else:
            bank_application.console.print("[yellow]No accounts available.[/yellow]")
