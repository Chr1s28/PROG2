import importlib.util
from datetime import datetime, timedelta
from enum import Enum, auto

# Defines a basic person class with some basic properties, calculated properties and methods
# Also added an optional speak method which uses a really small llm to reply to the users prompt
# It only works if the transformers package is installed and also note that it will download a ~140mb model file if you want to try it out.
# LLM inference runs always on cpu


class Color(Enum):
    BROWN = auto()
    GINGER = auto()
    BLONDE = auto()
    BLACK = auto()
    GREY = auto()


class Person:
    def __init__(self, given_name: str, last_name: str, haircolor: Color, birthday: datetime, shoe_size: int):
        self.given_name = given_name
        self.last_name = last_name
        self.haircolor = haircolor
        self.birthday = birthday
        self.shoe_size = shoe_size

    def speak(self, text) -> str:
        """
        Parrots given text or use an small llm to reply to the given text.
        Automatically detects wether transformers, which is needed for inference is installed, it's optional :)
        Source: https://huggingface.co/HuggingFaceTB/SmolLM-135M-Instruct
        """
        spec = importlib.util.find_spec("transformers")

        if spec is None:
            print(text)

        else:
            from transformers import AutoModelForCausalLM, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM-135M-Instruct")
            model = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM-135M-Instruct").to("cpu")

            messages = [
                {
                    "role": "system",
                    "content": f"Your name is {self.given_name} {self.last_name} and you're {self.age_in_years} years old",
                },
                {"role": "user", "content": text},
            ]
            input_text = tokenizer.apply_chat_template(messages, tokenize=False)
            inputs = tokenizer.encode(input_text, return_tensors="pt").to("cpu")
            outputs = model.generate(inputs, max_new_tokens=50, temperature=0.2, top_p=0.9, do_sample=True)
            print(tokenizer.decode(outputs[0]).split("<|im_start|>assistant")[1].strip("<|im_end|>"))

    @property
    def age(self) -> timedelta:
        """Calculates age of person based on birthday"""
        return datetime.today() - self.birthday

    @property
    def age_in_years(self) -> int:
        """
        Returns age in rounded down years.
        Note: This isn't really robust as it assumes every year is 365 days, for a better version we should use something like dateutil
        """
        return int(self.age.days / 365)


if __name__ == "__main__":
    myself = Person("Christian", "Bosshard", Color.BLACK, datetime(2001, 6, 28, 16, 00), 42)
    myself.speak("What's your name?")
    print(myself.age)
    print(myself.age_in_years)
