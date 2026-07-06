import sys
from pydantic import ValidationError
from src.simulation.manager import Manager


def main() -> None:
    try:
        if (len(sys.argv) != 2):
            print("Error: Enter filepath.\n"
                  "Usage: python3 -m src filepath/file.txt")
            sys.exit(1)

        args = sys.argv[1]

        manager = Manager(args)

        manager.start_simulation()

    except (ValueError, FileNotFoundError, ValidationError,
            IOError) as e:
        print(f"Error: {e}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("You exited the program")
        sys.exit(1)


if __name__ == "__main__":
    main()
