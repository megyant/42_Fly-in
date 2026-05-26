import pygame
from src.render.simulation import WorldState, SimulationState
import sys


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

        node_radius = max(10, int(scale * 0.3))

        return positions, scale, node_radius

    def load_world(self,) -> None:
        self.positions, self.scale, self.node_radius = self.compute_layout(
            self.world)

    def draw(self, simulation: SimulationState):
        self.simulation = simulation

        self.screen.fill((0, 0, 0))
        self._draw_connections(self.world)
        self._draw_hubs(self.world, self.simulation)
        self._draw_labels(self.world)
        self._draw_drones(self.world, self.simulation)
        pygame.display.update()
        self.clock.tick(60)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def _draw_connections(self) -> None:
        pass

    def _draw_hubs(self) -> None:
        pass

    def _draw_labels(self) -> None:
        pass

    def _draw_drones(self) -> None:
        pass
