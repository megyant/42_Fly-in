import sys
from pydantic import ValidationError
from src.parser.parser import Parser


def main():
    if len(sys.argv) != 2:
        print("Error: Enter filepath.\n"
              "Usage: python3 -m src.fly-in filepath/file.txt")
        sys.exit(1)
    try:
        file = Parser()
        file.parse_file(sys.argv[1])
        file.init_hubs()
        print(file.init_hubs())
    except (ValueError, FileNotFoundError, ValidationError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
