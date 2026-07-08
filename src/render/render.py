import pygame
from src.simulation.models import WorldState, SimulationState
from typing import Tuple, Dict
import sys


class DroneMovement:
    def __init__(self, pos: tuple[float, float]) -> None:
        self.pos = pygame.Vector2(pos)
        self.speed = 0.08

    def update(self, target: pygame.Vector2) -> None:
        self.pos = self.pos.lerp(target, self.speed)

    def reached(self, target: pygame.Vector2) -> bool:
        return self.pos.distance_to(target) < 0.5


class Render:
    def __init__(self, world: WorldState) -> None:
        pygame.init()

        self.width = 1280
        self.heigth = 720

        self.screen = pygame.display.set_mode((self.width,
                                               self.heigth),
                                              pygame.RESIZABLE)

        pygame.display.set_caption("mbotelho's Fly-in")

        self.clock = pygame.time.Clock()
        self.positions: dict[str, tuple[float, float]] = {}

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
                    'violet': (238, 130, 238),
                    'silver': (192, 192, 192),
                    'gainsboro': (220, 220, 220),
                    'tomato': (255, 99, 71),
                    'goldenrod': (218, 165, 32),
                    'royalblue': (65, 105, 225)
                    }

        self.rainbow_colors = [
                            'red',
                            'orange',
                            'yellow',
                            'lime',
                            'blue',
                            'purple'
                        ]
        self.zone_color = {
            'normal': 'gainsboro',
            'blocked': 'goldenrod',
            'restricted': 'tomato',
            'priority': 'royalblue'
        }

        self.drone_img = pygame.image.load('src/render/assets/drone.png')
        self.drone_sprite = self.drone_img
        self.drone_movement: dict[str, DroneMovement] = {}

    def compute_layout(self) -> Tuple[Dict[str, Tuple[float, float]],
                                      float, float]:
        hubs = self.world.hubs.values()
        if not hubs:
            return {}, 1.0, 1.0

        min_x = min(h.x for h in hubs)
        max_x = max(h.x for h in hubs)
        min_y = min(h.y for h in hubs)
        max_y = max(h.y for h in hubs)

        padding = 100  # between window boudaries and drawing space

        usable_w = self.width - 2 * padding
        usable_h = self.heigth - 2 * padding

        rrange_x = max_x - min_x
        rrange_y = max_y - min_y

        range_x = rrange_x if rrange_x > 0 else 1
        range_y = rrange_y if rrange_y > 0 else 1

        scale_x = usable_w / range_x
        scale_y = usable_h / range_y
        scale = min(scale_x, scale_y)

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

        sprite_size = max(1, node_radius * 2)

        self.drone_sprite = pygame.transform.smoothscale(
            self.drone_img,
            (sprite_size, sprite_size)
        )

        return positions, scale, node_radius

    def load_world(self) -> None:
        layout = self.compute_layout()
        self.positions, self.scale, self.node_radius = layout
        start_pos = self.positions[self.world.start]
        for i in range(self.world.nb_drones):
            self.drone_movement[f"D{i}"] = DroneMovement(start_pos)

    def draw(self, simulation: SimulationState) -> bool:
        self._handle_events()

        self.simulation = simulation

        self.screen.fill((255, 255, 255))
        self._draw_connections()
        self._draw_zones()
        self._draw_zone_legend()
        self._draw_turns()
        self._draw_hubs()
        self._draw_labels()
        all_arrived = self._draw_drones(simulation=simulation)
        pygame.display.update()
        self.clock.tick(60)

        return all_arrived

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.VIDEORESIZE:
                self.width, self.heigth = event.size
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
        self.center = {}
        for key, connection in self.world.connections.items():
            pygame.draw.line(surface=self.screen,
                             color=self.color_map['silver'],
                             start_pos=self.positions[connection.start],
                             end_pos=self.positions[connection.end],
                             width=2)
            start = self.positions[connection.start]
            end = self.positions[connection.end]
            self.center[key] = ((start[0] + end[0]) / 2,
                                (start[1] + end[1]) / 2)

    def _draw_zones(self) -> None:
        for hub in self.world.hubs.values():
            if hub.processed_meta is None:
                continue
            color_pick = self.color_map['white']
            if hub.processed_meta.zone == 'normal':
                color_pick = self.color_map[self.zone_color['normal']]
            elif hub.processed_meta.zone == 'blocked':
                color_pick = self.color_map[self.zone_color['blocked']]
            elif hub.processed_meta.zone == 'restricted':
                color_pick = self.color_map[self.zone_color['restricted']]
            elif hub.processed_meta.zone == 'priority':
                color_pick = self.color_map[self.zone_color['priority']]

            pygame.draw.circle(surface=self.screen,
                               color=color_pick,
                               center=self.positions[hub.name],
                               radius=self.node_radius * 1.2)

    def _draw_hubs(self) -> None:
        for hub in self.world.hubs.values():
            if hub.processed_meta is None:
                continue
            if hub.processed_meta.color != 'rainbow':
                color_name = hub.processed_meta.color
                color_pick: Tuple[int, int, int] | pygame.Color
                if color_name in self.color_map:
                    color_pick = self.color_map[color_name]
                else:
                    color_pick = pygame.Color(color_name or 'blue')

                pygame.draw.circle(surface=self.screen,
                                   color=color_pick,
                                   center=self.positions[hub.name],
                                   radius=self.node_radius)
            else:
                total_rings = len(self.rainbow_colors)
                for i, color in enumerate(self.rainbow_colors):
                    ring_factor = (total_rings - i) / total_rings
                    new_radius = self.node_radius * ring_factor
                    color_pick = self.color_map[color]
                    pygame.draw.circle(surface=self.screen,
                                       color=color_pick,
                                       center=self.positions[hub.name],
                                       radius=max(1, int(new_radius)))

    def _draw_labels(self) -> None:
        self.font = pygame.font.SysFont("Arial", round(self.scale * 0.11),
                                        bold=True)
        for name in self.world.hubs:
            pos = self.positions[name]

            text_surface = self.font.render(name,
                                            True,
                                            self.color_map['black'])

            text_w = text_surface.get_width()

            render_x = pos[0] - (text_w // 2)

            render_y = pos[1] + (self.node_radius * 1.2)

            self.screen.blit(text_surface, (render_x, render_y))

    def _draw_zone_legend(self) -> None:
        font_size = 14

        self.zone_font = pygame.font.SysFont("Arial", font_size,
                                             bold=False)

        text1 = 'zones:'
        text_surface = self.zone_font.render(text1,
                                             True,
                                             self.color_map['black'])
        self.screen.blit(text_surface, (20, self.heigth-100 - 10))

        texts = ['priority',
                 'restricted',
                 'blocked',
                 'normal']
        for i, text in enumerate(texts):
            color = self.color_map[self.zone_color[text]]

            text_surface2 = self.zone_font.render(text,
                                                  True,
                                                  self.color_map['black'])

            render_x = 45

            render_y = self.heigth - 20 - i * 20 - 10

            circle_y = self.heigth - 10 - i * 20 - 10

            self.screen.blit(text_surface2, (render_x, render_y))

            pygame.draw.circle(surface=self.screen,
                               color=color,
                               center=(30, circle_y),
                               radius=5)

    def _draw_turns(self) -> None:
        text = f"Turns: {self.simulation.turn}"

        font_size = 20

        self.turns_font = pygame.font.SysFont("Arial", font_size,
                                              bold=False)

        text_surface = self.turns_font.render(text,
                                              True,
                                              self.color_map['black'])
        self.screen.blit(text_surface, (20, 10))

    def _draw_drones(self, simulation: SimulationState) -> bool:
        sprite_w = self.drone_sprite.get_width()
        sprite_h = self.drone_sprite.get_height()
        all_arrived = True

        for drone in range(self.world.nb_drones):
            drone_key = f"D{drone}"
            current_pos = simulation.drone_positions[drone_key]

            if '-' in current_pos:
                if current_pos not in self.center:
                    continue
                target = pygame.Vector2(self.center[current_pos])
            else:
                if current_pos not in self.positions:
                    continue
                target = pygame.Vector2(self.positions[current_pos])

            visual = self.drone_movement[drone_key]
            visual.update(target)

            if visual.pos.distance_to(target) > 0.5:
                all_arrived = False

            render_x = visual.pos.x - (sprite_w // 2)
            render_y = visual.pos.y - (sprite_h // 2)

            self.screen.blit(self.drone_sprite, (render_x, render_y))

        return all_arrived
