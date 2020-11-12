#!/usr/bin/python3
import argparse
import sys
import secrets
from os import path
from string import ascii_letters, digits, punctuation


def main():
    # Init parser
    parser = argparse.ArgumentParser(description="Generate random passwords")

    # Default Variables
    WORD_COUNT = 5
    CHARACTER_COUNT = None
    PASSWORDS_TO_GENERATE = 1

    DIR = path.dirname(path.realpath(__file__))
    FILE_NAME = "output.txt"
    SAVE_PATH = path.join(DIR, FILE_NAME)

    # Arguments
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s v1.0",
        help="show version information",
    )

    parser.add_argument(
        "-d",
        "--diceware",
        action="store_true",
        help="use diceware algorithm (recommended)",
    )

    parser.add_argument(
        "-w",
        "--words",
        metavar="amount",
        type=int,
        default=WORD_COUNT,
        help=f"number of words to use in password with diceware (Default: {WORD_COUNT})",
    )

    parser.add_argument(
        "-c",
        "--characters",
        metavar="amount",
        type=int,
        const=CHARACTER_COUNT,
        nargs="?",
        help=f"choose a specific number of characters to use (NOT RECOMMENDED)",
    )

    parser.add_argument(
        "-s",
        "--save-to-file",
        nargs="?",
        type=str,
        const=SAVE_PATH,
        metavar="path/to/file",
        dest="save_path",
        help="save password(s) to file (NOT RECOMMENDED)",
    )

    parser.add_argument(
        "-n",
        "--num-to-generate",
        metavar="amount",
        type=int,
        default=PASSWORDS_TO_GENERATE,
        help=f"number of passwords to generate (Default: {PASSWORDS_TO_GENERATE})",
    )

    # Parse arguments
    args = parser.parse_args()

    # Convert relative path into usable path if one is passed with -s argument
    if args.save_path and args.save_path.startswith("./"):
        args.save_path = path.join(DIR, args.save_path[2:])

    # Validate arguments
    validate_args(args)

    # Run script
    password = generate_password(args)
    print(password)

    sys.exit()


def generate_password(args):
    if args.diceware:
        print("Generating with diceware...")

    else:
        valid_characters = ascii_letters + digits + punctuation + " "

        if args.characters:
            password_length = args.characters
        else:
            # If no password length is given, choose one randomly between 10 and 20 inclusive
            password_length = secrets.choice([number for number in range(10, 21)])

        while True:
            password = "".join(
                secrets.choice(valid_characters) for _ in range(password_length)
            )

            # Criteria for a valid password is:
            #
            # Contains at least 1 uppercase letter
            # Contains at least 1 lowercase letter
            # Contains at least 1 space
            # at least X% of characters are punctuation
            # at least X% of characters are digits

            lower_check = False
            upper_check = False
            space_check = False

            found_punctuation = 0
            found_digits = 0

            MAX_PUNCTUATION_PERCENT = 0.20
            MAX_DIGIT_PERCENT = 0.10

            # Validate password meets criteria, if not keep looping until it does
            for ch in password:
                if ch.islower():
                    lower_check = True
                elif ch.isupper():
                    upper_check = True
                elif ch == " ":
                    space_check = True
                elif ch.isdigit():
                    found_digits += 1
                elif ch in punctuation:
                    found_punctuation += 1

            if (
                lower_check
                and upper_check
                and space_check
                and found_punctuation >= password_length * MAX_PUNCTUATION_PERCENT
                and found_digits >= password_length * MAX_DIGIT_PERCENT
            ):
                break

        return password


def validate_args(args):
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128

    # Validate character count
    if args.characters is not None:
        if (
            args.characters < PASSWORD_MIN_LENGTH
            or args.characters > PASSWORD_MAX_LENGTH
        ):
            raise ValueError(
                f"Character count must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH}"
            )


if __name__ == "__main__":
    main()