from src.models import WorldState, SimulationState
from queue import PriorityQueue


class Algorithm:
    def __init__(self, world: WorldState, simulation: SimulationState) -> None:
        self.world = world
        self.simulation = simulation
        self.neighbours = self.world.neighbours

    def is_closed(self) -> None:
        pass
