from src.parser.pydantic_validation import ValidationParser
from src.models import WorldState
from src.render.simulation import SimulationStatus
from src.render.render import Render
from src.algorithm.algorithm import Algorithm


class Manager:
    def __init__(self, filepath: str) -> None:
        self.filepath = filepath

    def parsing(self) -> None:
        self.validation = ValidationParser()
        self.validation.parse_file(self.filepath)

    def initialize_classes(self) -> None:
        self.parsing()
        result = self.validation.init_hubs()
        self.all_hubs, self.start_name, self.end_name = result
        self.connections = self.validation.init_connections()
        self.neighbours = self.validation.build_neighbours(
            self.connections)

    def initialize_world(self) -> None:
        self.initialize_classes()
        self.world = WorldState(
            nb_drones=self.validation.nb_drones,
            hubs=self.all_hubs,
            connections=self.connections,
            neighbours=self.neighbours,
            start=self.start_name,
            end=self.end_name
        )

    def initialize_simulation(self) -> None:
        self.simulation = SimulationStatus(self.world, self.render, self.algo)

    def initialize_render(self) -> None:
        self.render = Render(self.world)
        self.render.load_world()

    def start_algorithm(self) -> None:
        self.algo = Algorithm(self.world)
        self.algo.zonecost_table()
        self.algo.cost_table()
        self.algo.graph_table()
        self.algo.dijkstra()
        self.algo.reconstruct_path()

    def start_simulation(self) -> None:
        self.initialize_world()
        self.initialize_render()
        self.start_algorithm()
        self.initialize_simulation()

        self.simulation.run()
