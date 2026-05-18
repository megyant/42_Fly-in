import sys
from pydantic import ValidationError
from src.parser.validation_parse import ValidationParser
from src.render.render import Render

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
        all_hubs, start_name, end_name = file.init_hubs()
        start_hub = all_hubs[start_name]
        end_hub = all_hubs[end_name]
        hubs = [hub for name, hub in all_hubs.items() if name != start_name
                and name != end_name]
        connections = file.init_connections()
        game_data = file.create_dicts(hubs=hubs,
                                      start_hub=start_hub,
                                      end_hub=end_hub,
                                      connections=list(connections.values()))
        print()
        print(start_hub, end_hub, hubs)
        print()
        print(connections)
        print()
        print(game_data)
        render = Render()
        render.render()
    except (ValueError, FileNotFoundError, ValidationError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
