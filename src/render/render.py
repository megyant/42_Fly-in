import pygame
from src.models import WorldState, SimulationState
import sys


class Render:
    def __init__(self, world: WorldState):
        pygame.init()
        self.screen_width = 1920
        self.screen_height = 1080
        self.screen = pygame.display.set_mode((self.screen_width,
                                               self.screen_height),
                                              pygame.FULLSCREEN)
        pygame.display.set_caption("mbotelho's Fly-in")
        self.clock = pygame.time.Clock()
        self.positions: dict[str, tuple[int, int]] = {}
        self.world = world

        self.color_map = {
                    'black': (0, 0, 0),
                    'white': (255, 255, 255),
                    'red': (255, 0, 0),
                    'green': (0, 128, 0),
                    'blue': (0, 0, 255),
                    'yellow': (255, 255, 0),
                    'maroon': (128, 0, 0),
                    'orange': (255, 165, 0),
                    'purple': (128, 0, 128),
                    'gray': (128, 128, 128),
                    'cyan': (0, 255, 255),
                    'brown': (165, 42, 42),
                    'lime': (0, 255, 0),
                    'magenta': (255, 0, 255),
                    'gold': (255, 215, 0),
                    'darkred': (139, 0, 0),
                    'crimson': (220, 20, 60),
                    'violet': (238, 130, 238)
                    }

        self.rainbow_colors = [
                            'red',
                            'orange',
                            'yellow',
                            'lime',
                            'blue',
                            'purple'
                        ]

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

        scale_x = min(usable_w / range_x, 150)
        scale_y = min(usable_h / range_y, 150)

        actual_w = range_x * scale_x
        actual_h = range_y * scale_y

        offset_x = (self.screen_width - actual_w) / 2
        offset_y = (self.screen_height - actual_h) / 2

        positions = {}
        for name, hub in self.world.hubs.items():
            sx = offset_x + (hub.x - min_x) * scale_x
            sy = offset_y + (max_y - hub.y) * scale_y
            positions[name] = (sx, sy)

        max_radius = int(scale_x * 0.3)
        node_radius = max(10, min(max_radius, int(scale_x * 0.5)))

        return positions, scale_x, scale_y, node_radius

    def load_world(self) -> None:
        layout = self.compute_layout()
        self.positions, self.scale_x, self.scale_y, self.node_radius = layout

    def draw(self, simulation: SimulationState):
        self._handle_events()

        self.simulation = simulation

        self.screen.fill((255, 255, 255))
        self._draw_connections()
        self._draw_hubs()
        self._draw_labels()
        self._draw_drones()
        pygame.display.update()
        self.clock.tick(60)

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if event.key == pygame.K_c and (event.mod & pygame.KMOD_CTRL):
                    pygame.quit()
                    sys.exit()

    def _draw_connections(self) -> None:
        for connection in self.world.connections.values():
            pygame.draw.aaline(surface=self.screen,
                               color=(0, 0, 0),
                               start_pos=self.positions[connection.start],
                               end_pos=self.positions[connection.end])

    def _draw_hubs(self) -> None:
        for hub in self.world.hubs.values():
            if hub.processed_meta.color != 'rainbow':
                color_pick = self.color_map.get(hub.processed_meta.color)
                pygame.draw.circle(surface=self.screen,
                                   color=color_pick,
                                   center=self.positions[hub.name],
                                   radius=self.node_radius)
            else:
                total_rings = len(self.rainbow_colors)
                for i, color in enumerate(self.rainbow_colors):
                    ring_factor = (total_rings - i) / total_rings
                    new_radius = self.node_radius * ring_factor
                    color_pick = self.color_map.get(color)
                    pygame.draw.circle(surface=self.screen,
                                       color=color_pick,
                                       center=self.positions[hub.name],
                                       radius=max(1, int(new_radius)))

    def _draw_labels(self) -> None:
        pass

    def _draw_drones(self) -> None:
        pass
