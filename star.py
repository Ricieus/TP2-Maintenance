import math
import random

import pygame

from game_settings import GameSettings


class Star:
    def __init__(self, angle: int, position_initial: pygame.Vector2):
        self.position_initial = position_initial
        self.x, self.y = self.position_initial
        self.angle = math.radians(angle)
        self.speed_star = 0

    def move_direction(self):
        self.speed_star += random.randint(1, 10)

        self.x = self.position_initial[0] + self.speed_star * math.cos(self.angle)
        self.y = self.position_initial[1] + self.speed_star * math.sin(self.angle)

        if self.x < 0 or self.x > GameSettings.SCREEN_WIDTH or self.y < 0 or self.y > GameSettings.SCREEN_HEIGHT:
            self.speed_star = 0

    def draw(self, screen):
        # https://www.geeksforgeeks.org/pygame-drawing-objects-and-shapes/
        pygame.draw.line(screen, (255, 255, 0), (self.x - 2, self.y), (self.x + 2, self.y), 1)
        pygame.draw.line(screen, (255, 255, 0), (self.x, self.y - 2), (self.x, self.y + 2), 2)