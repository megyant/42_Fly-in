import sys
from pydantic import ValidationError
from src.parser.validation_parse import ValidationParser
from src.render.render_arguments import WorldState, SimulationStatus
# from src.render.render import Render

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
        connections = file.init_connections()
        neighbours = file.build_neighbours(connections)

        world = WorldState(
            nb_drones=file.nb_drones,
            hubs=all_hubs,
            connections=connections,
            neighbours=neighbours,
            start=start_name,
            end=end_name
        )
        simulation = SimulationStatus(world)
        print(world)
        print(f"\n{simulation.state}\n")

    except (ValueError, FileNotFoundError, ValidationError) as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
