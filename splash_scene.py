import pygame
import pygame.freetype  # Module for font rendering

from scene import Scene
from scene_manager import SceneManager
from game_settings import GameSettings, Files


class SplashScene(Scene):
    """ Scène titre (splash). """

    _FADE_OUT_DURATION: int = 1500  # ms
    FADE_IN_DURATION: int = 1500  # ms

    def __init__(self) -> None:
        super().__init__()
        self._surface = pygame.image.load(GameSettings.FILE_NAMES[Files.IMG_SPLASH]).convert_alpha()
        self._music = pygame.mixer.Sound(GameSettings.FILE_NAMES[Files.SND_SPLASH])
        self._music.play(loops=-1, fade_ms=1000)
        self._fade_out_start_time = None

        # Load the font with a smaller size
        self._font = pygame.freetype.Font(GameSettings.FILE_NAMES[Files.FONT], 16)
        self._text_alpha = 0
        self._fade_in = True

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._fade_out_start_time = pygame.time.get_ticks()
                SceneManager().change_scene("level1_load", SplashScene._FADE_OUT_DURATION)

    def update(self) -> None:
        if self._fade_out_start_time:
            elapsed_time = pygame.time.get_ticks() - self._fade_out_start_time
            volume = max(0.0, 1.0 - (elapsed_time / SplashScene._FADE_OUT_DURATION))
            self._music.set_volume(volume)
            if volume == 0:
                self._fade_out_start_time = None

        # Animate the text
        if self._fade_in:
            self._text_alpha += 5
            if self._text_alpha >= 255:
                self._text_alpha = 255
                self._fade_in = False
        else:
            self._text_alpha -= 5
            if self._text_alpha <= 0:
                self._text_alpha = 0
                self._fade_in = True

    def render(self, screen: pygame.Surface) -> None:
        screen.blit(self._surface, (0, 0))

        # Texte à afficher
        text_parts = ["PRESS", "SPACE", "OR", "RETURN", "TO", "PLAY"]
        colors = [(255, 255, 255), (255, 255, 0), (255, 255, 255), (255, 255, 0), (255, 255, 255), (255, 255, 255)]
        outline_color = (0, 0, 255)  # Couleur bleue pour le contour

        # Rendre chaque partie avec sa couleur respective
        rendered_parts = []
        for part, color in zip(text_parts, colors):
            # Texte avec contour bleu
            outline_surface = self._font.render(part, outline_color)[0]  # Contour bleu
            # Texte principal (blanc ou jaune)
            part_surface = self._font.render(part, color)[0]  # Texte normal
            rendered_parts.append((outline_surface, part_surface))

        # Calcul de la largeur et de la hauteur du texte combiné
        total_width = sum(part_surface.get_width() for _, part_surface in rendered_parts) + 10 * (
                    len(rendered_parts) - 1)
        max_height = max(part_surface.get_height() for _, part_surface in rendered_parts)

        # Créer une surface combinée pour tout le texte
        combined_surface = pygame.Surface((total_width, max_height), pygame.SRCALPHA)

        x_offset = 0
        for outline_surface, part_surface in rendered_parts:
            # Dessiner le contour légèrement décalé
            combined_surface.blit(outline_surface, (x_offset - 2, 2))  # Décalage du contour
            # Dessiner le texte principal au-dessus
            combined_surface.blit(part_surface, (x_offset, 0))
            x_offset += part_surface.get_width() + 10  # Espacement entre les mots

        # Appliquer l'effet de fondu
        combined_surface.set_alpha(self._text_alpha)

        # Calculer la position pour centrer le texte combiné
        text_rect = combined_surface.get_rect(center=(screen.get_width() // 2, screen.get_height() - 50))

        # S'assurer que le texte ne dépasse pas du côté droit
        if text_rect.right > screen.get_width():
            text_rect.right = screen.get_width() - 10

        # Afficher le texte sur l'écran
        screen.blit(combined_surface, text_rect)

    def surface(self) -> pygame.Surface:
        return self._surface
