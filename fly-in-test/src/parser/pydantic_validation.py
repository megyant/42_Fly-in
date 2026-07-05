from src.parser.parser import Parser
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


class Zone(str, Enum):
    """ Lists all available options for [zone=]. """
    normal = 'normal'
    blocked = 'blocked'
    restricted = 'restricted'
    priority = 'priority'


class MetaModelDrones(BaseModel):
    """ Class that stores all metadata for hubs. """
    zone: Optional[Zone] = Zone.normal
    color: Optional[str] = None
    max_drones: Optional[int] = Field(default=1, ge=1)


class HubModel(BaseModel):
    """ Class that stores all parameters from hubs. """
    name: Any
    x: int = Field(ge=-100)  # Missing field
    y: int = Field(ge=-100)  # Missing field
    metadata: Optional[List[str]] = None
    processed_meta: Optional[MetaModelDrones] = None

    @model_validator(mode='after')
    def validate_hub_name(self) -> 'HubModel':
        if ' ' in self.name or '-' in self.name:
            raise ValueError(f"Invalid hub name: '{self.name}'. "
                             "Spaces and dashes are forbidden")
        return self

    @model_validator(mode='after')
    def check_metadata_drones(self) -> 'HubModel':
        """
        Validates if metadata is is apropriate format and
        stores it in its own Base Model - MetaModelDrones().
        """
        if self.metadata is None:
            self.processed_meta = MetaModelDrones()
            return self
        data: dict[str, Any] = {}
        for meta in self.metadata:
            clean = meta.strip('[]')
            if '=' in clean:
                k, v = clean.split("=", 1)
                if v.strip():
                    data[k] = v
            else:
                raise ValueError(f"Wrong data format in metadata: {meta}")

        try:
            if data.get("zone"):
                data["zone"] = Zone(data["zone"])
            self.processed_meta = MetaModelDrones(**data)
        except (ValueError, ValidationError):
            print(f"\nError: {data}: {data[k]} in {self.metadata} could not be"
                  " processed.\nUsing default values defined.\n")
            self.processed_meta = MetaModelDrones()

        return self


class MetaModelConnect(BaseModel):
    """ Class that stores all metadata for connections. """
    max_link_capacity: Optional[int] = Field(default=1, ge=1)


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
        data: dict[str, Any] = {}
        for meta in self.metadata:
            clean = meta.strip('[]')

            if '=' in clean:
                k, v = clean.split("=", 1)
                if v.strip():
                    data[k] = v
            else:
                raise ValueError("Wrong data format in "
                                 f"metadata: {meta}")
        try:
            self.processed_meta = MetaModelConnect(**data)
        except (ValueError, ValidationError):
            print(f"\nError: could not process {data} in {self.metadata}"
                  ".\nUsing default value defined for "
                  "max_link_capacity.\n")
            self.processed_meta = MetaModelConnect()
        return self


class ValidationParser(Parser):
    def __init__(self) -> None:
        """
        Initialize the ValiadionParser class.

        Args:
            nb_drones: Number of drones in the simulation.
            start_hub: Starting hub for the simulation.
            hubs: List of hubs inputed in the configuration file.
            end_hub: Ending hub for the simulation.
            connections: 'Roads' between hubs.
        """
        super().__init__()

    def init_hubs(self) -> Tuple[Dict[str, HubModel], str, str]:
        """
            Initialize and store the parsed dictionaries into a HubModel().
        """
        try:
            if not self.start_hub:
                current_line = self.hubs[0].get("line")
                raise ValueError("'start_hub' is missing from the file")
            if not self.end_hub:
                current_line = self.hubs[-1].get("line")
                raise ValueError("'end_hub' is missing from the file")
            # store start_hub into a HubModel()
            current_line = self.start_hub.get("line")
            start = HubModel(
                    name=self.start_hub.get("name"),
                    x=self.start_hub.get("x", 0),
                    y=self.start_hub.get("y", 0),
                    metadata=self.start_hub.get("metadata")
                    )

            # store end_hub into a HubModel
            current_line = self.end_hub.get("line")
            end = HubModel(
                    name=self.end_hub.get("name"),
                    x=self.end_hub.get("x", 0),
                    y=self.end_hub.get("y", 0),
                    metadata=self.end_hub.get("metadata")
                    )
            if start is None:
                raise ValueError("Could not compute end_hub.")

            # store each hub into a HubModel
            hubs = []
            for hub in self.hubs:
                current_line = hub.get("line")
                hubs.append(HubModel(
                        name=hub.get("name"),
                        x=hub.get("x", 0),
                        y=hub.get("y", 0),
                        metadata=hub.get("metadata")
                        ))

            all_hubs = {start.name: start, end.name: end}
            all_hubs.update({hub.name: hub for hub in hubs})

            return all_hubs, start.name, end.name

        except ValidationError as e:
            raise ValueError("Could not process data - "
                             f"{e.errors()[0].get('msg')}.\n"
                             f"Line: {current_line}")
        except ValueError as e:
            raise ValueError("Could not process data - "
                             f"{str(e)}.\n"
                             f"Line: {current_line}")

    def init_connections(self) -> Dict[str, ConnectionModel]:
        """
            Initialize and store the parsed dictionaries into a
            ConnectionModel().
        """
        try:
            # store each connection into a ConnectionModel()
            connections = [ConnectionModel(
                            start=conn_str.split('-')[0],
                            end=conn_str.split('-')[1],
                            metadata=connection.get("metadata")
                                        )
                           for connection in self.connections
                           if ((conn_str := connection.get("connection"))
                               is not None)
                           ]

            connect_dict: Dict[str, ConnectionModel] = {f"{c.start}-{c.end}":
                                                        c for c in connections}

            return connect_dict
        except (ValueError, ValidationError)as e:
            raise ValueError(f"Could not process data - {e}.\n"
                             f"Line: {self.line_number}")

    def build_neighbours(self,
                         conne: dict[str, ConnectionModel]) -> dict[str,
                                                                    list[str]]:
        neighbours: dict[str, list[str]] = {}

        for conn in conne.values():
            neighbours.setdefault(conn.start, []).append(conn.end)
            neighbours.setdefault(conn.end, []).append(conn.start)

        return neighbours
