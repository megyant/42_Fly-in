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
        steps = []
        print("\n=== Starting Simulation ===")
        print(f"\nNumber of drones: {self.world.nb_drones}\n")
        while not self.finished():
            self.step()

            # print planned drone moves
            for drone, pos in self.planned_moves.items():
                drone_num = int(drone.split('D')[1]) + 1
                print(f"D{drone_num}-{pos}", end=" ")

            # print drones in 2nd turn of restricted zone
            for drone, pos in self.resolved_transits.items():
                drone_num = int(drone.split('D')[1]) + 1
                print(f"D{drone_num}-{pos}", end=" ")
            print()

            # save each step to use in render
            steps.append(SimulationState(
                turn=self.state.turn,
                drone_positions=dict(self.state.drone_positions),
                hub_occupancy=dict(self.state.hub_occupancy),
                connection_occupancy=dict(self.state.connection_occupancy),
                in_transit=dict(self.state.in_transit)
            ))

        print(f"\nTotal turns: {self.state.turn}")

        for each_step in steps:
            all_arrived = False
            while not all_arrived:
                all_arrived = self.renderer.draw(each_step)

        while True:
            self.renderer.draw(self.state)

    def finished(self) -> bool:
        return all(pos == self.world.end
                   for pos in self.state.drone_positions.values())

    def step(self) -> None:
        self.planned_moves = {}
        self.resolved_transits = {}
        tentative_occupancy = self.state.hub_occupancy.copy()

        for drone, current_pos in self.state.drone_positions.items():
            # filter out drones that have reached end
            if current_pos == self.world.end:
                continue

            # solve drones that are attempting a restricted zone
            # in_transit - {drone: (start_zone, end_zone)}
            if drone in self.state.in_transit:
                destination = self.state.in_transit[drone][1]
                self.state.drone_positions[drone] = destination
                self.state.hub_occupancy[destination] += 1
                self.state.in_transit.pop(drone)
                # mark them as handled
                self.resolved_transits[drone] = destination
                continue

            # drone is mid-connection, not yet resolved
            if '-' in current_pos:
                continue

            # get current and next index
            current_index = self.path_index[current_pos]
            if current_index + 1 >= len(self.algorithm.final_path):
                continue
            next_pos = self.algorithm.final_path[current_index + 1]

            # get the connection start-end format
            if f"{current_pos}-{next_pos}" in self.world.connections:
                connection_key = f"{current_pos}-{next_pos}"
            else:
                connection_key = f"{next_pos}-{current_pos}"

            # Place drone on connection in 1st round of restricted
            if self.world.hubs[next_pos].processed_meta.zone == 'restricted':
                # get the position
                self.state.in_transit[drone] = (current_pos, next_pos)
                # get connection
                self.state.drone_positions[drone] = connection_key
                # reduce from hub
                self.state.hub_occupancy[current_pos] -= 1
                tentative_occupancy[current_pos] -= 1
                # increase in connection
                self.state.connection_occupancy[connection_key] += 1
                continue

            # get essential variables
            next_pos_meta = self.world.hubs[next_pos].processed_meta
            max_drones_next = next_pos_meta.max_drones
            connection = self.world.connections[connection_key].processed_meta
            max_link_capacity_conn = connection.max_link_capacity
            connection_occup = self.state.connection_occupancy[connection_key]

            # is the hub free
            hub_ok = (current_pos == self.world.start or
                      next_pos == self.world.end or
                      tentative_occupancy[next_pos] < max_drones_next)

            # if hub and connection free
            if hub_ok and connection_occup < max_link_capacity_conn:
                # plan the moves
                self.planned_moves[drone] = next_pos
                tentative_occupancy[next_pos] += 1
                tentative_occupancy[current_pos] -= 1
                self.state.connection_occupancy[connection_key] += 1

        # apply planned moves
        for drone, next_pos in self.planned_moves.items():
            current_pos = self.state.drone_positions[drone]
            self.state.drone_positions[drone] = next_pos
            self.state.hub_occupancy[current_pos] -= 1
            self.state.hub_occupancy[next_pos] += 1

        # reset connection usage except in_transit
        self.state.connection_occupancy = {key: 0
                                           for key in self.world.connections}
        for drone, (origin, destination) in self.state.in_transit.items():
            if f"{origin}-{destination}" in self.world.connections:
                transit_key = f"{origin}-{destination}"
            else:
                transit_key = f"{destination}-{origin}"
            self.state.connection_occupancy[transit_key] += 1

        # count turns
        self.state.turn += 1
