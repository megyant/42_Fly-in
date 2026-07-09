from src.render.render import Render
from src.simulation.models import WorldState, SimulationState
from src.algorithm.algorithm import Algorithm
from src.simulation.simulation_step import SimulationStep


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

        self.hub_max = {name: hub.processed_meta.max_drones or 1
                        for name, hub in world.hubs.items()
                        if hub.processed_meta}
        self.conn_max = {key: conn.processed_meta.max_link_capacity or 1
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
        self.sim_step = SimulationStep(self.state, self.world)

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
        Process a single discrete operational turn cycle by coordinating
        tracking resolution, collecting intent requests, allocating asset
        capacities, and committing final position updates.
        """
        self.resolved_transits = self.sim_step.resolve_arrivals()
        requests = self.sim_step.collect_requests(self.resolved_transits)
        admitted = self.sim_step.allocate_capacity(requests,
                                                   self.hub_max,
                                                   self.conn_max)

        self.planned_moves = {r.drone: r.dest for r in admitted
                              if not r.is_restricted}

        self.sim_step.apply_moves(admitted)
