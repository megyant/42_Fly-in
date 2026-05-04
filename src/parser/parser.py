import os
from typing import Dict, List, Any

""" nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal """

""" from pydantic import BaseModel, Field, ValidationError """

""" class File(BaseModel):
    start_hub: str
    hub: str
    end_hub: str
    connection: str """


class Parser:
    def __init__(self):
        self.nb_drones: int = 0
        self.start_hub: Dict[str, Any] = {}
        self.hubs: List[Dict[str, Any]] = []
        self.end_hub: Dict[str, Any] = {}
        self.connections: List[str] = []

    def parse_file(self, filepath: str):
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Error: File not found {filepath}")

        lines: List[str] = []

        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except IOError:
            print("Error: Could not read file")

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if line.startswith('nb_drones'):
                if self.nb_drones != 0:
                    raise ValueError("Duplicated 'number of drones' "
                                     "variable")
                try:
                    self.nb_drones = int(line.split(':')[1])
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'number of drones' - "
                                     f"{e}")
        print(self.nb_drones)