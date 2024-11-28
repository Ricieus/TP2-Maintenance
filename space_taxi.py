"""
  Tribute to Space Taxi!

  Ce programme rend hommage au jeu Space Taxi écrit par John Kutcher et publié pour le
  Commodore 64 en 1984.  Il s'agit  d'une interprétation libre inspirée  de la version
  originale. Aucune ressource originale (son, image, code) n'a été réutilisée.

  Le code propose un nombre important  d'opportunités de refactorisation.  Il contient
  également plusieurs erreurs à corriger. Il a été conçu pour un travail pratique dans
  le cadre du cours de Maintenance logicielle (420-5GP-BB) du programme de  Techniques
  de l'informatique au Collège de Bois-de-Boulogne, à Montréal.  L'usage en est permis
  à des fins pédagogiques seulement.

  Eric Drouin
  Novembre 2024
"""
import os

from black_scene import BlackScene
from game_over_scene import GameOver

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys

from game_settings import GameSettings
from level_loading_scene import LevelLoadingScene
from level_scene import LevelScene
from scene_manager import SceneManager
from splash_scene import SplashScene


def main() -> None:
    """ Programme principal. """
    pygame.init()
    pygame.mixer.init()

    settings = GameSettings()
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
    pygame.display.set_caption("Tribute to Space Taxi!")
    window_icon = pygame.image.load('img/space_taxi_icon.ico')
    pygame.display.set_icon(window_icon)


    clock = pygame.time.Clock()

    show_fps = False

    if show_fps:
        fps_font = pygame.font.Font(None, 36)

    scene_manager = SceneManager()
    print("Début de construction")
    scene_manager.add_scene("black", BlackScene())
    scene_manager.add_scene("splash", SplashScene())
    scene_manager.add_scene("level1_load", LevelLoadingScene(1))
    scene_manager.add_scene("level1", LevelScene(1))
    scene_manager.add_scene("level2_load", LevelLoadingScene(2))
    scene_manager.add_scene("game_over", GameOver())
    print("Fin de construction")

    scene_manager.set_scene("black")

    fade_time = 1500 #temps pour l'effet de fondu noir (1.5 secondes)
    scene_manager.change_scene("splash", fade_time)

    try:
        while True:

            delta_time = clock.tick(settings.FPS) / 1000  # en secondes

            scene_manager.update(delta_time)

            scene_manager.render(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                scene_manager.handle_event(event)

            if show_fps:
                fps = clock.get_fps()
                fps_text = fps_font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
                screen.blit(fps_text, (10, 10))

            pygame.display.flip()

    except KeyboardInterrupt:
        quit_game()


def quit_game() -> None:
    """ Quitte le programme. """
    pygame.mixer.music.stop()
    pygame.quit()
    sys.exit(0)


if __name__ == '__main__':
    main()
