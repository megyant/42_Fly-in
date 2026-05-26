import sys
from pydantic import ValidationError
from src.manager import Manager

"""
Next:

- Start working on the graphs
- Start working on the algorithm
"""


def main():
    try:
        if len(sys.argv) != 2:
            print("Error: Enter filepath.\n"
                  "Usage: python3 -m src.fly-in filepath/file.txt")
            sys.exit(1)

        args = sys.argv[1]

        manager = Manager(args)

        manager.start_simulation()

    except (ValueError, FileNotFoundError, ValidationError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("You exited the program")
        sys.exit(1)


if __name__ == "__main__":
    main()
