from src.simulation.models import WorldState
from src.parser.pydantic_validation import Zone
import heapq


class Algorithm:
    """ Pathfinding algorithm management class. """
    def __init__(self, world: WorldState) -> None:
        """
        Initialize the Algorithm class.

        Args:
            world: Current state of the simulation world containing hubs and
            connections.
            processed: Set of nodes that have already been evaluated.
            zone_costs: Dictionary mapping hub names to their respective
            traversal costs.
            costs: Dictionary keeping track of the shortest distance from
            start to each hub.
            parents: Dictionary tracking node lineages to reconstruct the
            final path.
            graph: Adjacency list representation of the unblocked world
            network.
        """
        self.world = world
        self.processed: set[str] = set()
        self.zone_costs: dict[str, int] = {}
        self.costs: dict[str, float] = {}
        self.parents: dict[str, str] = {}
        self.graph: dict[str, dict[str, int]] = {}

    def zonecost_table(self) -> None:
        """
        Populate the zone costs table based on the classification zone of each
        hub.
        """
        hub_cost = 0
        for hub in self.world.hubs.values():
            if hub.processed_meta is None:
                continue
            elif (hub.processed_meta.zone == Zone.normal or
                  hub.processed_meta.zone == Zone.priority):
                hub_cost = 1
                self.zone_costs[hub.name] = hub_cost

            elif hub.processed_meta.zone == Zone.restricted:
                hub_cost = 2
                self.zone_costs[hub.name] = hub_cost

    def cost_table(self) -> None:
        """
        Initialize the tracking costs table for all hubs, setting the start
        hub to zero and all others to infinity.
        """
        for hub in self.world.hubs.values():
            if hub.name == self.world.start:
                self.costs[hub.name] = 0

            else:
                self.costs[hub.name] = float("inf")

    def graph_table(self) -> None:
        """
        Build the bidirectional graph network, filtering out any connections
        associated with blocked zones.
        """
        self.graph = {}

        for hub in self.world.connections.values():
            start_meta = self.world.hubs[hub.start].processed_meta
            end_meta = self.world.hubs[hub.end].processed_meta
            if (start_meta is None or end_meta is None):
                continue
            if (end_meta.zone == Zone.blocked or
               start_meta.zone == Zone.blocked):
                continue
            if hub.start not in self.graph:
                self.graph[hub.start] = {}
            if hub.end not in self.graph:
                self.graph[hub.end] = {}
            self.graph[hub.start][hub.end] = self.zone_costs[hub.end]
            self.graph[hub.end][hub.start] = self.zone_costs[hub.start]

    def dijkstra(self) -> None:
        """
        Execute Dijkstra's algorithm using a priority queue to determine the
        shortest valid route to the destination.
        """
        heap = [(0, self.world.start)]
        while heap:
            cost, node = heapq.heappop(heap)
            if node == self.world.end:
                break
            if node in self.processed:
                continue
            self.processed.add(node)
            for neigbour, weight in self.graph[node].items():
                new_cost = cost + weight
                if new_cost < self.costs[neigbour]:
                    self.costs[neigbour] = new_cost
                    self.parents[neigbour] = node
                    heap.append((new_cost, neigbour))

    def reconstruct_path(self) -> list[str]:
        """
        Backtrack through parent associations to build the correct directional
        path.

        Returns:
            A list of hub names representing the calculated sequence from
            start to end.
        """
        self.final_path: list[str] = []
        current = self.world.end
        while current != self.world.start:
            self.final_path.append(current)
            current = self.parents[current]
        self.final_path.append(current)

        self.final_path = self.final_path[::-1]

        return self.final_path
