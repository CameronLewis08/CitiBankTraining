"""
Input helpers for the Banking Domain Console Application:
    Wraps the builtin input() with the light validation/retry logic the
    console menus need (plain text, numeric amounts, restricted choices).
"""


def user_input(prompt):
    return input(prompt).strip()


def get_choice(prompt, valid_choices):
    while True:
        choice = user_input(prompt)
        if choice in valid_choices:
            return choice
        print(f"Invalid choice. Please choose one of: {', '.join(valid_choices)}")


def get_float(prompt):
    while True:
        value = user_input(prompt)
        try:
            return float(value)
        except ValueError:
            print("Please enter a valid number.")
