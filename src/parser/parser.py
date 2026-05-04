import os
from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Dict, List, Any, Optional

""" nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal """


class MetaModel(BaseModel):
    zone: Optional[str] = "normal"
    color: Optional[str] = None
    max_drones: Optional[int] = 1


class HubModel(BaseModel):
    name: str
    x: int
    y: int
    metadata: Optional[List[str]] = None
    processed_meta: Optional[MetaModel] = None

    @model_validator(mode='after')
    def check_metadata(self) -> 'MetaModel':
        data = {}
        for meta in self.metadata:
            clean = meta.strip('[]')

            if '=' in clean:
                k, v = clean.split("=", 1)
                data[k] = v
            else:
                raise ValidationError(f"Wrong data format in metadata: {meta}")

        self.processed_meta = MetaModel(**data)

        return self


class Parser:
    def __init__(self) -> None:
        self.nb_drones: int = 0
        self.start_hub: Dict[str, Any] = {}
        self.hubs: List[Dict[str, Any]] = []
        self.end_hub: Dict[str, Any] = {}
        self.connections: List[Dict[str, Any]] = []

    def parse_file(self, filepath: str) -> None:
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

            # nb_drones
            if line.startswith('nb_drones'):
                if self.nb_drones != 0:
                    raise ValueError("Duplicated 'number of drones' "
                                     "variable")
                try:
                    self.nb_drones = int(line.split(':')[1])
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'number of drones' - "
                                     f"{e}")

            # start_hub
            elif line.startswith('start_hub'):
                if self.start_hub != {}:
                    raise ValueError("Duplicated 'start_hub' "
                                     "variable")
                try:
                    info = line.split(':')[1]
                    parts = info.split()

                    self.start_hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": parts[3:] if len(parts) > 3 else None
                    }
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'start_hub' - "
                                     f"{e}")

            # end_hub
            elif line.startswith('end_hub'):
                if self.end_hub != {}:
                    raise ValueError("Duplicated 'end_hub' "
                                     "variable")
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
                                     f"{e}")

            # hubs
            elif line.startswith('hub'):
                try:
                    info = line.split(':')[1]
                    parts = info.split()

                    hub = {
                        "name": parts[0],
                        "x": int(parts[1]),
                        "y": int(parts[2]),
                        "metadata": parts[3:] if len(parts) > 3 else None
                    }
                    self.hubs.append(hub)
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'hub' - "
                                     f"{e}")

            elif line.startswith('connection'):
                try:
                    info = line.split(':')[1]. strip()
                    parts = info.split()

                    if not parts:
                        continue

                    connect = parts[0]
                    metadata = parts[1:] if len(parts) > 1 else None

                    self.connections.append(
                        {
                            "connection": connect,
                            "metadata": metadata
                        }
                    )
                except (ValueError, IndexError) as e:
                    raise ValueError("Could not compute 'hub' - "
                                     f"{e}")

    def init_hubs(self) -> None:
        try:
            # start hub
            start = HubModel(
                    name=self.start_hub.get("name"),
                    x=self.start_hub.get("x", 0),
                    y=self.start_hub.get("y", 0),
                    metadata=self.start_hub.get("metadata")
                    )

            # end hub
            end = HubModel(
                    name=self.end_hub.get("name"),
                    x=self.end_hub.get("x", 0),
                    y=self.end_hub.get("y", 0),
                    metadata=self.end_hub.get("metadata")
                    )

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
            raise ValueError(f"Could not process data - {e}")
