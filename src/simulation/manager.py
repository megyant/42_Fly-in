from src.parser.pydantic_validation import ValidationParser
from src.simulation.models import WorldState
from src.simulation.simulation import SimulationStatus
from src.render.render import Render
from src.algorithm.algorithm import Algorithm


class Manager:
    """
    Orchestrates the entire simulation lifecycle, from initial file parsing
    to component initialization and runtime execution.
    """
    def __init__(self, filepath: str) -> None:
        """
        Initialize the Manager class.

        Args:
            filepath: Path of the configuration file to load.
        """
        self.filepath = filepath

    def parsing(self) -> None:
        """
        Instantiate the input validator and execute the initial file parsing
        logic.
        """
        self.validation = ValidationParser()
        self.validation.parse_file(self.filepath)

    def initialize_classes(self) -> None:
        """
        Parse configuration data and structural components, extracting entities
        like hubs, connections, adjacency maps, and origin points.
        """
        self.parsing()
        result = self.validation.init_hubs()
        self.all_hubs, self.start_name, self.end_name = result
        self.connections = self.validation.init_connections()
        self.neighbours = self.validation.build_neighbours(
            self.connections)

    def initialize_world(self) -> None:
        """
        Build and configure the fundamental simulation environment using
        parsed entities.
        """
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
        """
        Instantiate the main tracking engine bound to the prepared environment
        subsystems.
        """
        self.simulation = SimulationStatus(self.world, self.render, self.algo)

    def initialize_render(self) -> None:
        """
        Construct the UI display context and load positional geometry layout
        maps.
        """
        self.render = Render(self.world)
        self.render.load_world()

    def start_algorithm(self) -> None:
        """
        Set up routing calculations and execute pathfinding routines to compute
        the optimal trajectory sequence.
        """
        self.algo = Algorithm(self.world)
        self.algo.zonecost_table()
        self.algo.cost_table()
        self.algo.graph_table()
        self.algo.dijkstra()
        self.algo.reconstruct_path()

    def start_simulation(self) -> None:
        """
        Execute the entire setup pipeline sequentially and launch the active
        simulation runtime window.
        """
        self.initialize_world()
        self.initialize_render()
        self.start_algorithm()
        self.initialize_simulation()

        self.simulation.run()
