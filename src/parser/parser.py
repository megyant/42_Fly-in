import os
import re
from typing import Dict, List, Any


class Parser:
    """
    Base configuration parser responsible for raw text stream segmentation,
    line-by-line syntax validation, and basic field extraction.
    """
    def __init__(self) -> None:
        """
        Initialize the Parser class.

        Args:
            nb_drones: Number of drones in the simulation.
            start_hub: Starting hub for the simulation.
            hubs: List of hubs inputed in the configuration file.
            end_hub: Ending hub for the simulation.
            connections: 'Roads' between hubs.
        """
        self.nb_drones: int = 0
        self.start_hub: Dict[str, Any] = {}
        self.hubs: List[Dict[str, Any]] = []
        self.end_hub: Dict[str, Any] = {}
        self.connections: List[Dict[str, Any]] = []
        self.line_number: int = 0
        self.seen_connections: set[str] = set()

    def parse_file(self, filepath: str) -> None:
        """
        Initial parsing of the file. Here the file is opened,
        lines are stripped and we divide the text into the initialized
        variables.

        Args:
            filepath: Path of the file to open
        """
        # check if file path exists
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found {filepath}.")

        lines: List[str] = []  # to save the lines read

        try:
            # open the file and copy the lines to the list
            with open(filepath, 'r') as f:
                lines = f.readlines()
        except IOError as e:
            raise IOError(f"Error: Could not read file - {e}")

        for self.line_number, line in enumerate(lines, start=1):
            # clean lines from leading and trailing spaces and ignore comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # parse nb_drones
            if line.startswith('nb_drones'):
                if self.nb_drones != 0:
                    raise ValueError("Duplicated 'number of drones' "
                                     "variable.\n"
                                     f"Line: {self.line_number}")
                try:
                    # split line at ':' and get 2nd argument turned into int
                    self.nb_drones = int(line.split(':')[1])
                    if self.nb_drones < 0:
                        raise ValueError("Number of drones must be positive")
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'number of drones' - "
                                     f"{e}.")

            # parse start_hub
            elif line.startswith('start_hub'):
                # if there is already a start hub it means there was a
                # duplication
                if self.start_hub != {}:
                    raise ValueError("Duplicated 'start_hub' "
                                     "variable\n"
                                     f"Line: {self.line_number}")
                try:
                    # split line at ':' and get 2nd argument,
                    # then split on spaces
                    info = line.split(':')[1]
                    parts = info.split()

                    meta_match = re.search(r'\[([^\]]*)\]', line)
                    metadata = (meta_match.group(1).split()
                                if meta_match else None)

                    # save the final dictionary
                    self.start_hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": metadata,
                        "line": self.line_number
                    }
                except (ValueError, IndexError):
                    raise ValueError("Could not compute 'start_hub'\n"
                                     f"Line: {self.line_number}.\n")

            # parse end_hub
            elif line.startswith('end_hub'):
                # same as start_hub
                if self.end_hub != {}:
                    raise ValueError("Duplicated 'end_hub' "
                                     "variable"
                                     f"Line: {self.line_number}")
                try:
                    info = line.split(':')[1]
                    parts = info.split()

                    meta_match = re.search(r'\[([^\]]*)\]', line)
                    metadata = (meta_match.group(1).split()
                                if meta_match else None)

                    self.end_hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": metadata,
                        "line": self.line_number
                    }
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'end_hub' - "
                                     f"{e}.")

            # parse hubs
            elif line.startswith('hub'):
                # same as start_hub
                try:
                    info = line.split(':')[1]
                    parts = info.split()

                    name = parts[0]

                    x = int(parts[1])
                    y = int(parts[2])
                except (ValueError, IndexError) as e:
                    raise ValueError(f"Could not compute 'hub' - {e}.\n"
                                     f"Line: {self.line_number}")

                # check if there is already a hub with the same name
                full_hubs = list(self.hubs)
                if self.start_hub:
                    full_hubs.append(self.start_hub)
                if self.end_hub:
                    full_hubs.append(self.end_hub)
                if any(h['name'] == name for h in full_hubs):
                    raise ValueError("Duplicate hub: "
                                     f"{name}.\n"
                                     f"Line: {self.line_number}")

                meta_match = re.search(r'\[([^\]]*)\]', info)
                metadata = (meta_match.group(1).split()
                            if meta_match else None)

                hub = {
                    "name": parts[0],
                    "x": x,
                    "y": y,
                    "metadata": metadata,
                    "line": self.line_number
                }
                self.hubs.append(hub)

            # parse connections
            elif line.startswith('connection'):
                if not self.start_hub:
                    raise ValueError("'start_hub' is missing\n"
                                     f"Line: {self.line_number}")
                if not self.end_hub:
                    raise ValueError("'end_hub' is missing\n"
                                     f"Line: {self.line_number}")
                try:
                    info = line.split(':')[1]. strip()
                    parts = info.split()

                    if not parts:
                        continue

                    connect = parts[0]
                    if connect.count("-") != 1:
                        raise ValueError("Connection not in waypoint-waypoint "
                                         "format\n"
                                         f"Line: {self.line_number}")

                    nodes = connect.split('-')

                    # Connections must link only previously defined zones
                    all_names = set()
                    if self.start_hub:
                        all_names.add(self.start_hub['name'])
                    if self.end_hub:
                        all_names.add(self.end_hub['name'])
                    for hub in self.hubs:
                        all_names.add(hub['name'])

                    for node in nodes:
                        if node not in all_names:
                            raise ValueError("Connections must link only "
                                             "previously defined zones\n"
                                             f"Line: {self.line_number}")

                    # Self-connections and duplicate connections not allowed
                    if nodes[0] == nodes[1]:
                        raise ValueError("Self-connection not allowed\n"
                                         f"Line: {self.line_number}")
                    sorted_nodes = sorted(nodes)
                    normalized = "-".join(sorted_nodes)

                    if (hasattr(self, 'seen_connections') and normalized in
                            self.seen_connections):
                        raise ValueError(f"Duplicate connection {nodes}\n"
                                         f"Line: {self.line_number}")

                    self.seen_connections.add(normalized)

                    metadata = parts[1:] if len(parts) > 1 else None

                    self.connections.append(
                        {
                            "connection": connect,
                            "metadata": metadata,
                            "line": self.line_number
                        }
                    )
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'connection' - "
                                     f"{e}.")
            else:
                raise ValueError("Found no corresponding parameter.\n"
                                 f"Line: {self.line_number}")
