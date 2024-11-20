import pygame
from abc import ABC, abstractmethod


class Scene(ABC):
    """ Classe abstraite de base pour les scènes. """

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    @abstractmethod
    def update(self, delta_time: float) -> None:
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        pass

    @abstractmethod
    def surface(self) -> pygame.Surface:
        pass
