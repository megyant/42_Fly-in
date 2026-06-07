from src.render.render import Render
from src.models import WorldState, SimulationState
from src.algorithm.algorithm import Algorithm


class SimulationStatus:
    def __init__(self, world: WorldState,
                 renderer: Render,
                 algorithm: Algorithm) -> None:
        self.world = world
        self.renderer = renderer
        self.algorithm = algorithm
        self.state = SimulationState(
            turn=0,
            drone_positions={f"D{i}": world.start
                             for i in range(world.nb_drones)},
            hub_occupancy={name: (world.nb_drones if name == world.start
                                  else 0) for name in world.hubs},
            connection_occupancy={key: 0 for key in world.connections},
            in_transit={}
        )

    def run(self) -> None:
        while not self.finished():
            print(f"Turn {self.state.turn}")
            print(self.algorithm.final_path)
            self.step()
            print(self.planned_moves)
            self.renderer.draw(self.state)
        print(self.state.drone_positions)
        print(self.state.hub_occupancy)

    def finished(self) -> bool:
        return all(pos == self.world.end for pos in
                   self.state.drone_positions.values())

    def step(self) -> None:
        for key in self.state.connection_occupancy:
            self.state.connection_occupancy[key] = 0

        self.planned_moves = {}
        tentative_occupancy = self.state.hub_occupancy.copy()

        for drone, current_pos in self.state.drone_positions.items():
            if current_pos == self.world.end:
                continue
            current_index = self.algorithm.final_path.index(current_pos)
            if current_index + 1 >= len(self.algorithm.final_path):
                continue
            next_pos = self.algorithm.final_path[current_index + 1]
            if f"{current_pos}-{next_pos}" in self.world.connections:
                connection_key = f"{current_pos}-{next_pos}"
            else:
                connection_key = f"{next_pos}-{current_pos}"
            if (next_pos == self.world.end or
               tentative_occupancy[next_pos] < self.world.hubs[next_pos].processed_meta.max_drones):
                if self.state.connection_occupancy[connection_key] < self.world.connections[connection_key].processed_meta.max_link_capacity:
                    self.planned_moves[drone] = next_pos
                    tentative_occupancy[next_pos] += 1
                    tentative_occupancy[current_pos] -= 1

        for drone, next_pos in self.planned_moves.items():
            current_pos = self.state.drone_positions[drone]
            self.state.drone_positions[drone] = next_pos
            self.state.hub_occupancy[current_pos] -= 1
            self.state.hub_occupancy[next_pos] += 1

        self.state.turn += 1
