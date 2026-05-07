import sys
from pydantic import ValidationError
from src.parser.parser import Parser


"""
Missing:
- Connections must link only previously defined zones using connection: <zone1>-<zone2>
[metadata].
- The same connection must not appear more than once (e.g., a-b and b-a are considered duplicates).
- Capacity values (max_drones for zones, max_link_capacity for connections) must
be positive integers.
- Any metadata block (e.g., [zone=... color=...] for zones, [max_link_capacity=...]
for connections) must be syntactically valid
- Any other parsing error must stop the program and return a clear error message
indicating the line and cause.
"""

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
