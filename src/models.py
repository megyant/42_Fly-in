from pydantic.dataclasses import dataclass
from src.parser.validation_parse import HubModel, ConnectionModel


@dataclass
class WorldState:
    nb_drones: int
    hubs: dict[str, HubModel]
    connections: dict[str, ConnectionModel]
    neighbours: dict[str, list[str]]
    start: str
    end: str


@dataclass
class SimulationState:
    turn: int
    drone_positions: dict[str, str]
    hub_occupancy: dict[str, int]
    connection_occupancy: dict[str, int]
    in_transit: dict[str, tuple[str, str]]
