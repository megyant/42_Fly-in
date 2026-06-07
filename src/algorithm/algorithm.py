from src.models import WorldState


class Algorithm:
    def __init__(self, world: WorldState) -> None:
        self.world = world
        self.processed = []
        self.zone_costs = {}
        self.costs = {}
        self.parents = {}

    def zonecost_table(self) -> dict:
        hub_cost = 0
        for hub in self.world.hubs.values():
            if (hub.processed_meta.zone == 'normal' or
               hub.processed_meta.zone == 'priority'):
                hub_cost = 1
                self.zone_costs[hub.name] = hub_cost

            elif hub.processed_meta.zone == 'restricted':
                hub_cost = 2
                self.zone_costs[hub.name] = hub_cost

    def cost_table(self):
        for hub in self.world.hubs.values():
            if hub.name == self.world.start:
                self.costs[hub.name] = 0

            else:
                self.costs[hub.name] = float("inf")

    def graph_table(self) -> None:
        self.graph = {}

        for hub in self.world.connections.values():
            if (self.world.hubs[hub.end].processed_meta.zone == 'blocked' or
               self.world.hubs[hub.start].processed_meta.zone == 'blocked'):
                continue
            if hub.start not in self.graph:
                self.graph[hub.start] = {}
            if hub.end not in self.graph:
                self.graph[hub.end] = {}
            self.graph[hub.start][hub.end] = self.zone_costs[hub.end]
            self.graph[hub.end][hub.start] = self.zone_costs[hub.start]

    def find_lowest_cost(self):
        lowest_cost = float("inf")
        lowest_cost_node = None
        for node in self.costs:
            cost = self.costs[node]
            if node not in self.processed:
                if cost < lowest_cost:
                    lowest_cost = cost
                    lowest_cost_node = node
                elif (lowest_cost_node is not None and
                      cost == lowest_cost and
                      self.world.hubs[lowest_cost_node].processed_meta.zone != 'priority' and
                      self.world.hubs[node].processed_meta.zone == 'priority'):
                    lowest_cost_node = node
        return lowest_cost_node

    def dijkstra(self) -> None:
        node = self.find_lowest_cost()

        while node is not None:
            if node == self.world.end:
                break
            cost = self.costs[node]
            neighbours = self.graph[node]

            for n in neighbours.keys():
                new_cost = cost + neighbours[n]
                if self.costs[n] > new_cost:
                    self.costs[n] = new_cost
                    self.parents[n] = node

            self.processed.append(node)
            node = self.find_lowest_cost()

    def reconstruct_path(self) -> list:
        self.final_path = []
        current = self.world.end
        while current != self.world.start:
            self.final_path.append(current)
            current = self.parents[current]
        self.final_path.append(current)

        self.final_path = self.final_path[::-1]

        return self.final_path
