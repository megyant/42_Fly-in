from pydantic.dataclasses import dataclass
from parser.validation_parse import HubModel, ConnectionModel, ValidationParser


@dataclass
class WorldState:
    nb_drones: int
    hubs: dict[str, HubModel]
    connections: list[ConnectionModel]
    start: str
    end: str
    turn: int
    drone_positions: dict[str, str]


@dataclass
class SimulationState:
    turn: int
    drone_positions: dict[str, str]
    connection_occupancy: dict[str, int]
    in_transit: dict[str, tuple[str, str]]


class SimulationStatus(ValidationParser):
    def __init__