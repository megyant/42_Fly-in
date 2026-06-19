from src.models import WorldState
from src.parser.pydantic_validation import Zone
import heapq


class Algorithm:
    def __init__(self, world: WorldState) -> None:
        self.world = world
        self.processed: set[str] = set()
        self.zone_costs: dict[str, int] = {}
        self.costs: dict[str, float] = {}
        self.parents: dict[str, str] = {}
        self.graph: dict[str, dict[str, int]] = {}

    def zonecost_table(self) -> None:
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
        for hub in self.world.hubs.values():
            if hub.name == self.world.start:
                self.costs[hub.name] = 0

            else:
                self.costs[hub.name] = float("inf")

    def graph_table(self) -> None:
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

    def reconstruct_path(self) -> list:
        self.final_path = []
        current = self.world.end
        while current != self.world.start:
            self.final_path.append(current)
            current = self.parents[current]
        self.final_path.append(current)

        self.final_path = self.final_path[::-1]

        return self.final_path
