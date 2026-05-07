import os
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Dict, List, Any, Optional
from enum import Enum

""" nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal """


class Zone(str, Enum):
    """ Lists all available options for [zone=]. """
    normal = 'normal'
    blocked = 'blocked'
    restricted = 'restricted'
    priority = 'priority'


class MetaModelDrones(BaseModel):
    """ Class that stores all metadata for hubs. """
    model_config = {"extra": "forbid"}
    zone: Optional[Zone] = Zone.normal
    color: Optional[str] = None
    max_drones: Optional[int] = 1


class HubModel(BaseModel):
    """ Class that stores all parameters from hubs. """
    name: str
    x: int
    y: int
    metadata: Optional[List[str]] = None
    processed_meta: Optional[MetaModelDrones] = None

    @model_validator(mode='after')
    def check_metadata_drones(self) -> 'HubModel':
        """
        Validates if metadata is is apropriate format and
        stores it in its own Base Model - MetaModelDrones().
        """
        if self.metadata is None:
            self.processed_meta = MetaModelDrones()
            return self
        data = {}
        for meta in self.metadata:
            clean = meta.strip('[]')
            if '=' in clean:
                k, v = clean.split("=", 1)
                if v.strip():
                    data[k] = v
            else:
                raise ValidationError(f"Wrong data format in metadata: {meta}")

        try:
            self.processed_meta = MetaModelDrones(**data)
        except ValidationError:
            print(f"\nError: {data}: {data[k]} in {self.metadata} could not be"
                  " processed.\nUsing default values defined.\n")
            self.processed_meta = MetaModelDrones()

        return self


class MetaModelConnect(BaseModel):
    """ Class that stores all metadata for connections. """
    model_config = {"extra": "forbid"}
    max_link_capacity: Optional[int] = 1


class ConnectionModel(BaseModel):
    """ Class that stores all parameters from connections. """
    start: str
    end: str
    metadata: Optional[List[str]] = None
    processed_meta: Optional[MetaModelConnect] = None

    @model_validator(mode='after')
    def check_metadata_connect(self) -> 'ConnectionModel':
        """
        Validates if metadata is is apropriate format and
        stores it in its own Base Model - MetaModelConnect().
        """
        if self.metadata is None:
            self.processed_meta = MetaModelConnect()
            return self
        data = {}
        for meta in self.metadata:
            clean = meta.strip('[]')

            if '=' in clean:
                k, v = clean.split("=", 1)
                if v.strip():
                    data[k] = v
            else:
                raise ValidationError("Wrong data format in "
                                      f"metadata: {meta}")
        try:
            self.processed_meta = MetaModelConnect(**data)
        except ValidationError:
            print(f"\nError: {data}: {data[k]} in {self.metadata} could not be"
                  "processed.\nUsing default value defined for "
                  "max_link_capacity.\n")
            self.processed_meta = MetaModelConnect()
        return self


class Parser:
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
        except IOError:
            print("Error: Could not read file.")

        for line in lines:
            # clean lines from leading and trailing spaces and ignore comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # parse nb_drones
            if line.startswith('nb_drones'):
                if self.nb_drones != 0:
                    raise ValueError("Duplicated 'number of drones' "
                                     "variable")
                try:
                    # split line at ':' and get 2nd argument turned into int
                    self.nb_drones = int(line.split(':')[1])
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'number of drones' - "
                                     f"{e}")

            # parse start_hub
            elif line.startswith('start_hub'):
                # if there is already a start hub it means there was a
                # duplication
                if self.start_hub != {}:
                    raise ValueError("Duplicated 'start_hub' "
                                     "variable.")
                try:
                    # split line at ':' and get 2nd argument,
                    # then split on spaces
                    info = line.split(':')[1]
                    parts = info.split()

                    # save the final dictionary
                    self.start_hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": parts[3:] if len(parts) > 3 else None
                    }
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'start_hub' - "
                                     f"{e}.")

            # parse end_hub
            elif line.startswith('end_hub'):
                # same as start_hub
                if self.end_hub != {}:
                    raise ValueError("Duplicated 'end_hub' "
                                     "variable.")
                try:
                    info = line.split(':')[1]
                    parts = info.split()

                    self.end_hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": parts[3:] if len(parts) > 3 else None
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

                    # check if there is already a hub with the same name
                    if any(h['name'] == name for h in self.hubs):
                        raise ValueError("Duplicate hub: "
                                         f"{name}.")

                    hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": parts[3:] if len(parts) > 3 else None
                    }
                    self.hubs.append(hub)
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'hub' - "
                                     f"{e}.")

            # parse connections
            elif line.startswith('connection'):
                try:
                    info = line.split(':')[1]. strip()
                    parts = info.split()

                    if not parts:
                        continue

                    connect = parts[0]
                    # check if there is already a conection with the path
                    exists = any(c['connection'] == connect for c
                                 in self.connections)
                    if exists:
                        raise ValueError("Duplicate connection: "
                                         f"{connect}.")

                    metadata = parts[1:] if len(parts) > 1 else None

                    self.connections.append(
                        {
                            "connection": connect,
                            "metadata": metadata
                        }
                    )
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'connection' - "
                                     f"{e}.")
            else:
                raise ValueError("Found no corresponding parameter.")

    def init_hubs(self) -> None:
        """
            Initialize and store the parsed dictionaries into a HubModel().
        """
        try:
            # store start_hub into a HubModel()
            start = HubModel(
                    name=self.start_hub.get("name"),
                    x=self.start_hub.get("x", 0),
                    y=self.start_hub.get("y", 0),
                    metadata=self.start_hub.get("metadata")
                    )

            # store end_hub into a HubModel
            end = HubModel(
                    name=self.end_hub.get("name"),
                    x=self.end_hub.get("x", 0),
                    y=self.end_hub.get("y", 0),
                    metadata=self.end_hub.get("metadata")
                    )

            # store each hub into a HubModel
            hubs = [
                    HubModel(
                        name=hub.get("name"),
                        x=hub.get("x", 0),
                        y=hub.get("y", 0),
                        metadata=hub.get("metadata")
                        )
                    for hub in self.hubs
                ]

            return start, end, hubs

        except ValueError as e:
            raise ValueError("Could not process data - "
                             f"{e.errors()[0].get('msg')}.")

    def init_connections(self) -> None:
        """
            Initialize and store the parsed dictionaries into a
            ConnectionModel().
        """
        try:
            # store each connection into a ConnectionModel()
            connections = [ConnectionModel(
                            start=connection.get("connection").split('-')[0],
                            end=connection.get("connection").split('-')[1],
                            metadata=connection.get("metadata")
                                        )
                           for connection in self.connections
                           ]

            return connections
        except (ValueError, ValidationError)as e:
            raise ValueError(f"Could not process data - {e}.")
