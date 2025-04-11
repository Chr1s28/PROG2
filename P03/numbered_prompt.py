from rich.prompt import Prompt, InvalidResponse


class NumberedPrompt(Prompt):
    """A prompt that allows selection by number instead of typing the full choice."""

    def pre_prompt(self) -> None:
        """Display numbered choices before the prompt."""
        if self.choices:
            for i, choice in enumerate(self.choices, 1):
                self.console.print(f"  {i}. {choice}")

    def process_response(self, value: str) -> str:
        """Handle selection by number or by name."""
        value = value.strip()

        if value.isdigit() and self.choices:
            index = int(value) - 1
            if 0 <= index < len(self.choices):
                return self.choices[index]
            raise InvalidResponse(f"Please enter a number between 1 and {len(self.choices)}")

        return super().process_response(value)
