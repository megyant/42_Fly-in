from src.render.render import Render


class SimulationStatus:
    def __init__(self, world: WorldState, renderer: Render) -> None:
        self.world = world
        self.renderer = renderer
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
            self.step()
            self.renderer.draw(self.world, self.state)

    def finished(self) -> bool:
        pass

    def step(self) -> None:
        pass
