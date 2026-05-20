import pygame
from src.render.render_arguments import WorldState, SimulationState


class Render:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("mbotelho's Fly-in")
        self.clock = pygame.time.Clock()

    def load_world(self, world: WorldState) -> None:
        self.positions, self.scale = self

    def draw(self, world: WorldState, simulation: SimulationState):
        self.screen.fill((0, 0, 0))
        self._draw_connections(world)
        self._draw_hubs(world, simulation)
        self._draw_labels(world)
        self._draw_drones(world, simulation)
        pygame.display.update()
        self.clock.tick(60)

    def _draw_connections(self, world: WorldState) -> None:
        pass

    def _draw_hubs(self, world: WorldState,
                   simulation: SimulationState) -> None:
        pass

    def _draw_labels(self, world: WorldState) -> None:
        pass

    def _draw_drones(self, world: WorldState,
                     simulation: SimulationState) -> None:
        pass
