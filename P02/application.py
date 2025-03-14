from rich import print
from rich.prompt import Prompt
import bcrypt

from saving_account import SavingAccount
from youth_account import YouthAccount

salt = b'$2b$12$lshujjHFpMf4uNenohn2tOjbvMkZeWzNniwEfeI0yjdCGqw29zvc.'

class ClientAccounts:
    def __init__(self):
        self.accounts = {}
        self.current_account = None

        password = Prompt.ask("Set password", password=True)

        self.password_hash = bcrypt.hashpw(bytes(password, encoding="utf-8"), salt)
    
    def __check_password(self, password: str) -> bool:
        return bcrypt.checkpw(bytes(password, encoding="utf-8"), self.password_hash)

    def __manage_account(self):
        option = Prompt.ask("Choose an account", choices=self.accounts.keys())

    def __add_account(self):
        option = Prompt.ask("Which type of account?", choices=["Saving account", "Youth account"])
        match option:
            case "Saving account":
                new_account = SavingAccount()
            case "Youth account":
                new_account = YouthAccount()
        
        name_option = Prompt.ask("Name of account")
        self.accounts[name_option] = new_account
    
    def run(self) -> None:
        password = Prompt.ask("Enter password", password=True)
        if self.__check_password(password):
            exit = False
        else:
            exit = True

        while not exit:
            option = Prompt.ask("What would you like to do", choices=["Manage account", "Add account", "Exit"])
            match option:
                case "Manage account":
                    self.__manage_account()
                case "Add account":
                    self.__add_account()
                case "Exit":
                    exit = True


if __name__ == "__main__":
    client = ClientAccounts()
    client.run()