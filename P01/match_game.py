import random
from enum import Enum, auto


class Strategy(Enum):
    RANDOM = auto()
    SMART = auto()


class MatchGame:
    def __init__(self, strategy=Strategy.RANDOM):
        self.stack = random.randint(10, 20)
        self.user_first = bool(random.randint(0, 1))
        self.strategy = strategy
         
        if self.user_first:
            self.turn = "user"
        else:
            self.turn = "computer"
        
        print(f"Starting with {self.stack} matches.")
        print(f"{'You' if self.user_first else 'Computer'} go first.")

    def display_progress(self):
        print(f"\nMatches left: {self.stack}")
        print("========O\n" * self.stack)

    def user_draw(self):
        while True:
            try:
                user_input = int(input("How many matches do you want to draw (1-3)? "))
                if 1 <= user_input <= 3 and user_input <= self.stack:
                    self.draw(user_input)
                    print(f"You drew {user_input} matches.")
                    break
                else:
                    print("Input needs to be between 1 and 3 and not bigger than current stack!")
            except ValueError:
                print("Please enter a valid number.")
    
    def computer_draw(self):
        if self.strategy == Strategy.RANDOM:
            # Random strategy - just pick 1-3 randomly
            com_input = min(random.randint(1, 3), self.stack)
        elif self.strategy == Strategy.SMART:
            # Smart strategy based on modular arithmetic
            remainder = self.stack % 4
            if remainder == 0:
                com_input = min(3, self.stack)
            elif remainder == 3:
                com_input = min(2, self.stack)
            else:  # remainder is 1 or 2
                com_input = min(1, self.stack)
        
        self.draw(com_input)
        print(f"Computer drew {com_input} matches.")

    def validate_outcome(self):
        if self.stack <= 0:
            if self.turn == "user":
                print("\nYou drew the last match. You lost!")
            elif self.turn == "computer":
                print("\nComputer drew the last match. You won!")
            return True
        return False

    def draw(self, input):
        self.stack -= input

    def play(self):
        while self.stack > 0:
            self.display_progress()
            
            if self.turn == "user":
                self.user_draw()
                if self.validate_outcome():
                    break
                self.turn = "computer"
            else:
                self.computer_draw()
                if self.validate_outcome():
                    break
                self.turn = "user"

if __name__ == '__main__':    
    game = MatchGame(strategy=Strategy.RANDOM)
    game.play()
