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
        self.path_index = {hub: i for i, hub in enumerate(
            self.algorithm.final_path)}
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
            self.temp_step()
            for drone, pos in self.planned_moves.items():
                drone_num = int(drone.split('D')[1]) + 1
                print(f"D{drone_num}-{pos}", end=" ")
            print()
            self.renderer.draw(self.state)
        while True:
            self.renderer.draw(self.state)

    def finished(self) -> bool:
        return all(pos == self.world.end
                   for pos in self.state.drone_positions.values())

    def temp_step(self) -> None:
        self.planned_moves = {}
        self.resolved_transits = {}
        tentative_occupancy = self.state.hub_occupancy.copy()

        for drone, current_pos in self.state.drone_positions.items():
            if current_pos == self.world.end:
                continue

            # resolve in_transit
            if drone in self.state.in_transit:
                destination = self.state.in_transit[drone][1]
                self.state.drone_positions[drone] = destination
                self.state.hub_occupancy[destination] += 1
                self.state.in_transit.pop(drone)
                self.resolved_transits[drone] = destination
                continue

            # drone is mid-connection, not yet resolved
            if '-' in current_pos:
                continue

            current_index = self.path_index[current_pos]
            if current_index + 1 >= len(self.algorithm.final_path):
                continue
            next_pos = self.algorithm.final_path[current_index + 1]

            if f"{current_pos}-{next_pos}" in self.world.connections:
                connection_key = f"{current_pos}-{next_pos}"
            else:
                connection_key = f"{next_pos}-{current_pos}"

            # restricted zone: place drone on connection
            if self.world.hubs[next_pos].processed_meta.zone == 'restricted':
                self.state.in_transit[drone] = (current_pos, next_pos)
                self.state.drone_positions[drone] = connection_key
                self.state.hub_occupancy[current_pos] -= 1
                tentative_occupancy[current_pos] -= 1
                self.state.connection_occupancy[connection_key] += 1
                continue

            next_pos_meta = self.world.hubs[next_pos].processed_meta
            max_drones_next = next_pos_meta.max_drones
            connection = self.world.connections[connection_key].processed_meta
            max_link_capacity_conn = connection.max_link_capacity
            connection_occup = self.state.connection_occupancy[connection_key]

            hub_ok = (current_pos == self.world.start or
                      next_pos == self.world.end or
                      tentative_occupancy[next_pos] < max_drones_next)

            if hub_ok and connection_occup < max_link_capacity_conn:
                self.planned_moves[drone] = next_pos
                tentative_occupancy[next_pos] += 1
                tentative_occupancy[current_pos] -= 1
                self.state.connection_occupancy[connection_key] += 1

        # apply all planned moves
        for drone, next_pos in self.planned_moves.items():
            current_pos = self.state.drone_positions[drone]
            self.state.drone_positions[drone] = next_pos
            self.state.hub_occupancy[current_pos] -= 1
            self.state.hub_occupancy[next_pos] += 1

        # reset link usage but preserve in_transit connections
        self.state.connection_occupancy = {key: 0
                                           for key in self.world.connections}
        for drone, (origin, destination) in self.state.in_transit.items():
            if f"{origin}-{destination}" in self.world.connections:
                transit_key = f"{origin}-{destination}"
            else:
                transit_key = f"{destination}-{origin}"
            self.state.connection_occupancy[transit_key] += 1

        self.state.turn += 1

    def step(self) -> None:
        self.planned_moves = {}
        self.resolved_transits = {}
        tentative_occupancy = self.state.hub_occupancy.copy()  

        for drone, current_pos in self.state.drone_positions.items():
            if current_pos == self.world.end:
                continue

            if drone in self.state.in_transit:
                destination = self.state.in_transit[drone][1]
                self.state.drone_positions[drone] = destination
                self.state.hub_occupancy[current_pos] -= 1
                self.state.hub_occupancy[destination] += 1
                self.state.in_transit.pop(drone)
                self.resolved_transits[drone] = destination
                continue

            if '-' in current_pos:
                continue

            current_index = self.path_index[current_pos]
            if current_index + 1 >= len(self.algorithm.final_path):
                continue

            next_pos = self.algorithm.final_path[current_index + 1]

            if f"{current_pos}-{next_pos}" in self.world.connections:
                connection_key = f"{current_pos}-{next_pos}"
            else:
                connection_key = f"{next_pos}-{current_pos}"

            if self.world.hubs[next_pos].processed_meta.zone == 'restricted':
                self.state.in_transit[drone] = (current_pos, next_pos)
                self.state.drone_positions[drone] = connection_key
                self.state.hub_occupancy[current_pos] -= 1
                tentative_occupancy[current_pos] -= 1
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
