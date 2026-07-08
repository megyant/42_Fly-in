from pydantic.dataclasses import dataclass
from src.parser.pydantic_validation import HubModel, ConnectionModel


@dataclass
class WorldState:
    """
    Represents the static layout and structure of the simulation world
    environment.

    Args:
        nb_drones: Total number of drones operating in the simulation.
        hubs: Dictionary mapping unique names to their respective HubModel
        configurations.
        connections: Dictionary mapping unique keys to their respective
        ConnectionModel paths.
        neighbours: Adjacency list mapping each hub name to its list of
        reachable neighboring hubs.
        start: Name of the origin starting hub.
        end: Name of the destination target hub.
    """
    nb_drones: int
    hubs: dict[str, HubModel]
    connections: dict[str, ConnectionModel]
    neighbours: dict[str, list[str]]
    start: str
    end: str


@dataclass
class SimulationState:
    """
    Represents the dynamic, real-time snapshot status of an active simulation
    turn.

    Args:
        turn: The current step or chronological turn count of the simulation.
        drone_positions: Dictionary tracking the current location (hub or
        connection key) of each drone.
        hub_occupancy: Dictionary tracking the current quantity of drones
        stationed at each hub.
        connection_occupancy: Dictionary tracking the current quantity of
        drones traveling on each connection.
        in_transit: Dictionary mapping moving drones to a tuple containing
        their source and destination hubs.
        drone_paths: Dictionary mapping the path of each drone
    """
    turn: int
    drone_positions: dict[str, str]
    hub_occupancy: dict[str, int]
    connection_occupancy: dict[str, int]
    in_transit: dict[str, tuple[str, str]]
    drone_paths: dict[str, list[str]]
