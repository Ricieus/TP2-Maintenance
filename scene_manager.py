import pygame

from fade import Fade
from scene import Scene


class SceneManager:
    """ Singleton pour la gestion des scènes. """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SceneManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, '_initialized'):
            self._scenes = {}
            self._current_scene = None
            self._next_scene = None

            self._fade = None
            self._transitioning = False

            self._initialized = True

    def add_scene(self, name: str, scene: Scene) -> None:
        self._scenes[name] = scene

    def set_scene(self, name: str) -> None:
        self._current_scene = self._scenes.get(name, self._current_scene)

    def change_scene(self, name: str, fade_duration: int = 0) -> None:
        self._next_scene = self._scenes.get(name, self._current_scene)
        self._fade = Fade(self._current_scene, self._next_scene)
        self._fade.start(fade_duration)
        self._transitioning = True

    def update(self, delta_time: float) -> None:
        if self._current_scene:
            self._current_scene.update(delta_time)

        if self._next_scene:
            self._next_scene.update(delta_time)

        if self._transitioning:
            self._fade.update()

            if not self._fade.is_fading():
                self._current_scene, self._next_scene = self._next_scene, None
                self._transitioning = False

    def render(self, screen: pygame.Surface) -> None:
        if self._current_scene:
            self._current_scene.render(screen)
        if self._next_scene:
            self._next_scene.render(screen)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._current_scene:
            self._current_scene.handle_event(event)
