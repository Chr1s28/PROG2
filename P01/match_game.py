import random


class MatchGame:
    def __init__(self):
        self.stack = random.randint(10, 20)

    def display_progress(self):
        print("Matches:")
        print("========O\n" * self.stack)

    def validate_input(self, user_input):
        if user_input > 3 and user_input < 1:
            return False
        else:
            return True

    def validate_outcome(self):
        if self.stack <= 0:
            return False
        else:
            return True

    def draw(self, input=None):
        if not input:
            input = random.randint(1, 3)

        self.stack -= input

    def play(self):
        while True:
            self.display_progress()
            user_input = int(input("How many do you want to draw? "))
            if not self.validate_input(user_input):
                print("Input needs to be between 1 and 3!")
                continue
            else:
                self.draw(user_input)
                if not self.validate_outcome():
                    print("You lost!")
                    break
                self.draw()
                if not self.validate_outcome():
                    print("You won!")
                    break

if __name__ == '__main__':
    game = MatchGame()
    game.play()