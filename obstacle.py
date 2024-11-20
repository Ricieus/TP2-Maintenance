import pygame


class Obstacle(pygame.sprite.Sprite):
    """ Obstacle. """

    def __init__(self, filename: str, pos: tuple) -> None:
        super(Obstacle, self).__init__()

        self.image = pygame.image.load(filename).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
