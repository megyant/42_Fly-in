import pygame
from src.models import WorldState, SimulationState
import sys


"""
Missing:
- Zone representative border and subtitles
- Draw subtitles for hubs
- Draw the drones
- Customize it better (?)

- Obv the algo still needs to be done

- Test parsing thoroughly
"""


class Render:
    def __init__(self, world: WorldState):
        pygame.init()

        self.width = 1280
        self.heigth = 720

        self.screen = pygame.display.set_mode((self.width,
                                               self.heigth),
                                              pygame.RESIZABLE)


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
        if not hubs:
            return {}, 1.0, 1.0, 1.0

        min_x = min(h.x for h in hubs)
        max_x = max(h.x for h in hubs)
        min_y = min(h.y for h in hubs)
        max_y = max(h.y for h in hubs)

        padding = 80  # between window boudaries and drawing space

        usable_w = self.width - 2 * padding
        usable_h = self.heigth - 2 * padding

        rrange_x = max_x - min_x
        rrange_y = max_y - min_y

        range_x = rrange_x if rrange_x > 0 else 1
        range_y = rrange_y if rrange_y > 0 else 1

        # + 60 to make scale better for school
        ideal_scale_x = usable_w / range_x
        ideal_scale_y = usable_h / range_y
        scale = min(ideal_scale_x, ideal_scale_y)

        if rrange_x == 0 and rrange_y == 0:
            scale = 100
        else:
            scale = min(scale, 400)

        actual_w = rrange_x * scale
        actual_h = rrange_y * scale

        offset_x = (self.width - actual_w) / 2
        offset_y = (self.heigth - actual_h) / 2

        positions = {}
        for name, hub in self.world.hubs.items():
            sx = offset_x + (hub.x - min_x) * scale
            sy = offset_y + (max_y - hub.y) * scale
            positions[name] = (sx, sy)

        max_radius = int(scale * 0.3)
        node_radius = max(10, min(max_radius, scale * 0.2))

        return positions, scale, node_radius

    def load_world(self) -> None:
        layout = self.compute_layout()
        self.positions, self.scale, self.node_radius = layout

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

            elif event.type == pygame.VIDEORESIZE:
                self.width, self.heigth = event.w, event.h
                self.screen = pygame.display.set_mode((self.width,
                                                       self.heigth),
                                                      pygame.RESIZABLE)
                self.load_world()

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
        """ color_pick = self.color_map.get('gray')
        for drone in range(self.world.nb_drones):
            center_pos = self.positions['start_hub']
            pygame.draw.rect(surface=self.screen,
                             color=color_pick,
                             rect=) """
