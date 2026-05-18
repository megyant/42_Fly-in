import pygame
from sys import exit


class Render:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("mbotelho's Fly-in")
        self.hub_surface = pygame.Surface((400, 400))
        self.hub_surface.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.hub_surface, (0, 255, 0),
                           [200, 200], 170)
        self.clock = pygame.time.Clock()

    def render(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            self.screen.fill((255, 255, 255))
            self.screen.blit(self.hub_surface, (300, 300))
            pygame.display.update()
            self.clock.tick(60)
