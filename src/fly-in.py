import sys
from pydantic import ValidationError
from src.parser.parser import Parser


def main():
    try:
        if len(sys.argv) > 1:
            if len(sys.argv) != 2:
                print("Error: Enter filepath.\n"
                      "Usage: python3 -m src.fly-in filepath/file.txt")
                sys.exit(1)
            else:
                args = sys.argv[1]
        else:
            args = user_interaction()
        file = Parser()
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


def user_interaction():  # TODO
    file = input("enter file: ")
    return file


if __name__ == "__main__":
    main()
