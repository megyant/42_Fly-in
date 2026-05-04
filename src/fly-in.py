import sys
from parser.parser import Parser


def main():
    if len(sys.argv) != 2:
        print("Error: Enter filepath.\n"
              "Usage: python3 fly-in.py filepath/file.txt")
        sys.exit(1)
    try:
        file = Parser()
        file.parse_file(sys.argv[1])
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
