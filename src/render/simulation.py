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
        # print(self.state.hub_occupancy)
        while not self.finished():
            for drone in self.state.drone_positions.keys():
                if self.state.drone_positions[drone] != self.world.start:
                    print(f"{int(drone.split('D')[1]) + 1}-{self.state.drone_positions[drone]}", end=" ")
            print()
            self.step()
            self.renderer.draw(self.state)
        print(self.state.turn)
        while True:
            self.renderer.draw(self.state)

    def finished(self) -> bool:
        return all(pos == self.world.end for pos in
                   self.state.drone_positions.values())

    def step(self) -> None:

        self.planned_moves = {}
        tentative_occupancy = self.state.hub_occupancy.copy()    

        for drone, current_pos in self.state.drone_positions.items():
            if current_pos == self.world.end:
                continue

            if drone in self.state.in_transit:
                destination = self.state.in_transit[drone][1]
                if f"{current_pos}-{destination}" in self.world.connections:
                    connection_key = f"{current_pos}-{destination}"
                else:
                    connection_key = f"{destination}-{current_pos}"
                self.state.drone_positions[drone] = destination
                self.state.connection_occupancy[connection_key] = 0
                self.state.hub_occupancy[current_pos] -= 1
                self.state.hub_occupancy[destination] += 1
                self.state.in_transit.pop(drone)
                continue

            current_index = self.algorithm.final_path.index(current_pos)
            if current_index + 1 >= len(self.algorithm.final_path):
                continue

            next_pos = self.algorithm.final_path[current_index + 1]

            if f"{current_pos}-{next_pos}" in self.world.connections:
                connection_key = f"{current_pos}-{next_pos}"
            else:
                connection_key = f"{next_pos}-{current_pos}"

            if self.world.hubs[next_pos].processed_meta.zone == 'restricted':
                self.state.in_transit[drone] = (current_pos, next_pos)
                self.state.connection_occupancy[connection_key] += 1
                continue

            next_pos_meta = self.world.hubs[next_pos].processed_meta
            max_drones_next = next_pos_meta.max_drones
            connection = self.world.connections[connection_key].processed_meta
            max_link_capacity_conn = connection.max_link_capacity
            connection_occup = self.state.connection_occupancy[connection_key]

            if (next_pos == self.world.end or
               tentative_occupancy[next_pos] < max_drones_next):
                if connection_occup < max_link_capacity_conn:
                    self.planned_moves[drone] = next_pos
                    tentative_occupancy[next_pos] += 1
                    tentative_occupancy[current_pos] -= 1

        for drone, next_pos in self.planned_moves.items():
            current_pos = self.state.drone_positions[drone]
            self.state.drone_positions[drone] = next_pos
            self.state.hub_occupancy[current_pos] -= 1
            self.state.hub_occupancy[next_pos] += 1

        self.state.turn += 1
