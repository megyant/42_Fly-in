import pygame
from src.render.render_arguments import WorldState, SimulationState
from sys import exit


class Render:
    def __init__(self, world: WorldState, simulation: SimulationState):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("mbotelho's Fly-in")
        self.clock = pygame.time.Clock()
        self.world = world
        self.simulation = simulation

    def render(self):
        