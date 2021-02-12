#!/usr/bin/python3
import argparse
import sys
import secrets
import json
from os import path
from string import ascii_letters, digits, punctuation


def main():
    # Init parser
    parser = argparse.ArgumentParser(description="Generate random passwords")

    # Default Variables
    PASSWORDS_TO_GENERATE = 1

    DIR = path.dirname(path.realpath(__file__))
    FILE_NAME = "output.txt"

    WORDS_MIN_LENGTH = 5
    WORDS_MAX_LENGTH = 15
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 128

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
        default=secrets.choice(
            [number for number in range(WORDS_MIN_LENGTH, WORDS_MAX_LENGTH + 1)]
        ),
        help=f"number of words to use in password with diceware",
    )

    parser.add_argument(
        "-c",
        "--characters",
        metavar="amount",
        type=int,
        default=secrets.choice(
            [number for number in range(PASSWORD_MIN_LENGTH, PASSWORD_MAX_LENGTH + 1)]
        ),
        nargs="?",
        help=f"number of characters to use in password",
    )

    parser.add_argument(
        "-s",
        "--save-to-file",
        nargs="?",
        type=str,
        const=DIR,
        metavar="path/to/file",
        dest="save_path",
        help="save password(s) to file (not recommended)",
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

    # Convert relative path into a usable absolute path if one is passed with -s argument
    if args.save_path and args.save_path.startswith("./"):
        args.save_path = path.join(DIR, args.save_path[2:])

    # Add vars to args for use in validate_args
    args.WORDS_MIN_LENGTH = WORDS_MIN_LENGTH
    args.WORDS_MAX_LENGTH = WORDS_MAX_LENGTH
    args.PASSWORD_MIN_LENGTH = PASSWORD_MIN_LENGTH
    args.PASSWORD_MAX_LENGTH = PASSWORD_MAX_LENGTH

    # Validate arguments
    validate_args(args)

    # Run script
    for _ in range(args.num_to_generate):
        password = generate_password(args)

        if args.save_path and path.exists(args.save_path):
            with open(path.join(args.save_path, FILE_NAME), 'a+') as f:
                f.write(password + '\n')
        else:
            print(password)


    sys.exit(0)


def generate_password(args):
    if args.diceware:
        try:
            with open("diceware.json") as f:
                diceware_json = json.load(f)
        except IOError:
            print("Missing diceware.json, file is needed to use the diceware algorithm")
            sys.exit(1)

        password = ""

        for _ in range(args.words):
            key = get_diceware_key()
            word = diceware_json[key]

            password += word + " "

        return password.rstrip()

    else:
        valid_characters = ascii_letters + digits + punctuation + " "

        password_length = args.characters

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


def roll_dice():
    return secrets.choice([number for number in range(1, 7)])


# Generates a 5 digit key to be used for the diceware dictionary
def get_diceware_key():
    key = ""

    for _ in range(5):
        number = roll_dice()
        key += str(number)

    return key


# This method is used for extra args validation outside the parser validations
def validate_args(args):
    # Validate character count
    if not args.diceware and args.characters is not None:
        if (
            args.characters < args.PASSWORD_MIN_LENGTH
            or args.characters > args.PASSWORD_MAX_LENGTH
        ):
            raise ValueError(
                f"Character count must be between {args.PASSWORD_MIN_LENGTH} and {args.PASSWORD_MAX_LENGTH}"
            )

    # Validate word count
    if args.diceware and args.words is not None:
        if args.words < args.WORDS_MIN_LENGTH or args.words > args.WORDS_MAX_LENGTH:
            raise ValueError(
                f"Word count must be between {args.WORDS_MIN_LENGTH} and {args.WORDS_MAX_LENGTH}"
            )


if __name__ == "__main__":
    main()