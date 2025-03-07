from datetime import date

class Person:
    def __init__(self, haircolor, age, shoe_size):
        self.haircolor = haircolor
        self.age = age
        self.shoe_size = shoe_size
    
    def speak(self, text):
        '''write text into terminal'''
        print(text)
    def ages(self, birth_date):
        '''input: birthdate in yyyymmdd -> writes remaining days till the person gets older'''
        dateT = date.today()
        dateT = dateT.strftime("%Y%m%d")
        dateT = str(dateT)
        birth_date = str(birth_date)
        if birth_date[4:4] > dateT[5:2, 8:2]:
            birth_date[4:4] = dateT[0:4] #take the actual year
        else:
             next_year = dateT[0:4]
             next_year += 1
             birth_date[4:4] = dateT[0:4]
        
        remaining_days = birth_date - dateT
        return remaining_days


myself = Person("blond", 27, 42)
myself.speak("I hope this works")
myself.ages(19970414)
