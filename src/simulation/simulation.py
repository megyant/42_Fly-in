from src.render.render import Render
from src.simulation.models import WorldState, SimulationState
from src.parser.pydantic_validation import Zone
from src.algorithm.algorithm import Algorithm


class SimulationStatus:
    """
    Manages the step-by-step turn execution logic, constraints,
    and transient occupancy states of the active simulation loop.
    """
    def __init__(self, world: WorldState,
                 renderer: Render,
                 algorithm: Algorithm) -> None:
        """
        Initialize the SimulationStatus class.

        Args:
            world: Current configuration state containing static environment
            details.
            renderer: Visual interface pipeline handler for frame presentation.
            algorithm: Evaluated routing agent populated with optimal path
            vectors.
            hub_max: Threshold dictionary tracking maximum drone capacity
            allowed per hub.
            conn_max: Threshold dictionary tracking maximum simultaneous drone
            capacity per link connection.
            state: Tracking state monitoring dynamic updates for the current
            frame iteration.
        """
        self.world = world
        self.renderer = renderer
        self.algorithm = algorithm

        self.hub_max = {name: hub.processed_meta.max_drones
                        for name, hub in world.hubs.items()
                        if hub.processed_meta}
        self.conn_max = {key: conn.processed_meta.max_link_capacity
                         for key, conn in world.connections.items()
                         if conn.processed_meta}
        self.state = SimulationState(
            turn=0,
            drone_positions={f"D{i}": world.start
                             for i in range(world.nb_drones)},
            hub_occupancy={name: (world.nb_drones if name == world.start
                                  else 0) for name in world.hubs},
            connection_occupancy={key: 0 for key in world.connections},
            in_transit={},
            drone_paths={f"D{i}": list(self.algorithm.final_path[1:])
                         for i in range(world.nb_drones)}
        )

    def run(self) -> None:
        """
        Execute the simulation loop sequentially until target resolution is
        reached, then pass step records directly to the visual renderer.
        """
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
                in_transit=dict(self.state.in_transit),
                drone_paths=dict[str, list[str]](
                     {k: list(v) for k, v in self.state.drone_paths.items()})
            ))

        print(f"\nTotal turns: {self.state.turn}")

        for each_step in steps:
            all_arrived = False
            while not all_arrived:
                all_arrived = self.renderer.draw(each_step)

        while True:
            self.renderer.draw(self.state)

    def finished(self) -> bool:
        """
        Verify if all deployed drone entities have arrived at the target
        ending destination.

        Returns:
            True if all drone positions equal the end hub name, otherwise
            False.
        """
        return all(pos == self.world.end
                   for pos in self.state.drone_positions.values())

    def step(self) -> None:
        """
        Process a single discrete operational snapshot cycle, managing transit
        delay logic, occupancy capacities, and route progression updates.
        """
        self.planned_moves = {}
        self.resolved_transits = {}
        restr_free: dict[str, int] = {}
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

                if self.state.drone_paths[drone]:
                    self.state.drone_paths[drone].pop(0)
                continue

            # drone is mid-connection, not yet resolved
            if '-' in current_pos:
                continue

            # get current and next index
            remaining_path = self.state.drone_paths[drone]
            if not remaining_path:
                continue

            next_pos = remaining_path[0]

            # get the connection start-end format
            if f"{current_pos}-{next_pos}" in self.world.connections:
                connection_key = f"{current_pos}-{next_pos}"
            else:
                connection_key = f"{next_pos}-{current_pos}"

            next_hub_meta = self.world.hubs[next_pos].processed_meta

            if next_hub_meta is None:
                continue
            elif next_hub_meta.zone == Zone.restricted:
                self.state.in_transit[drone] = (current_pos, next_pos)
                self.state.drone_positions[drone] = connection_key

                restr_free[current_pos] = restr_free.get(current_pos, 0) + 1
                tentative_occupancy[current_pos] -= 1

                self.state.connection_occupancy[connection_key] += 1
                continue

            max_drones_next = self.hub_max[next_pos]
            max_link_capacity_conn = self.conn_max[connection_key]
            if max_drones_next is None or max_link_capacity_conn is None:
                continue
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

        for hub_name, count in restr_free.items():
            self.state.hub_occupancy[hub_name] -= count

        # apply regular moves
        for drone, next_pos in self.planned_moves.items():
            current_pos = self.state.drone_positions[drone]
            self.state.drone_positions[drone] = next_pos
            self.state.hub_occupancy[current_pos] -= 1
            self.state.hub_occupancy[next_pos] += 1

            if self.state.drone_paths[drone]:
                self.state.drone_paths[drone].pop(0)

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
