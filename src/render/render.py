import pygame
from src.render.render_arguments import WorldState, SimulationState


class Render:
    def __init__(self, world: WorldState):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("mbotelho's Fly-in")
        self.clock = pygame.time.Clock()
        self.positions: dict[str, tuple[int, int]] = {}
        self.world = world

    def compute_layout(self) -> dict[str, tuple[int, int]]:
        hubs = self.world.hubs.values()
        min_x = min(h.x for h in hubs)
        max_x = max(h.x for h in hubs)
        min_y = min(h.y for h in hubs)
        max_y = max(h.y for h in hubs)

        padding = 80  # between window razor and draw

        usable_w = self.screen.get_width() - 2 * padding
        usable_h = self.screen.get_height() - 2 * padding

        range_x = max(max_x - min_x, 1)
        range_y = max(max_y - min_y, 1)

        scale = min(usable_w / range_x, usable_h / range_y)

        positions = {}
        for name, hub in self.world.hubs.items():
            sx = padding + (hub.x - min_x) * scale
            sy = padding + (max_y - hub.y) * scale
            positions[name] = (int(sx), int(sy))

        return positions, scale

    def load_world(self, world: WorldState) -> None:
        self.positions, self.scale = self.compute_layout(world)

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
