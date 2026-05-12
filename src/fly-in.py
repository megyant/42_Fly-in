import sys
from pydantic import ValidationError
from src.parser.validation_parse import ValidationParser


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
        file = ValidationParser()
        file.parse_file(args)
        hubs_data = file.init_hubs()
        connections_data = file.init_connections()
        print()
        print(hubs_data)
        print()
        print(connections_data)
    except (ValueError, FileNotFoundError, ValidationError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
