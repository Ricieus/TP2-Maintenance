import time
import pygame
import sys

from game_settings import GameSettings

pygame.init()

import pygame
import time
import threading
import sys

class FatalError:
    def __init__(self):
        self._settings = GameSettings
        self.countdown_time = 10
        self.countdown_lock = threading.Lock()

    def countdown_thread(self):
        while self.countdown_time > 0:
            time.sleep(1)
            with self.countdown_lock:
                self.countdown_time -= 1

    def run(self, missing_file):
        try:
            raise FileNotFoundError
        except FileNotFoundError:
            screen = pygame.display.set_mode((self._settings.SCREEN_WIDTH, self._settings.SCREEN_HEIGHT))
            pygame.display.set_caption("Fatal Error")


            BLACK = (0, 0, 0)
            RED = (255, 0, 0)
            WHITE = (255, 255, 255)

            font_large = pygame.font.Font(None, 74)
            font_small = pygame.font.Font(None, 36)

            countdown_thread_instance = threading.Thread(target=self.countdown_thread)
            countdown_thread_instance.start()


            while self.countdown_time > 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                screen.fill(BLACK)

                try:
                    warning_icon = pygame.image.load("img/warningIcone.png")
                    warning_icon = pygame.transform.scale(warning_icon, (100, 100))
                    icon_rect = warning_icon.get_rect(center=(self._settings.SCREEN_WIDTH // 2, 100))
                    screen.blit(warning_icon, icon_rect)
                except pygame.error:
                    warning_icon = pygame.Surface((100, 100))
                    warning_icon.fill(RED)
                    screen.blit(warning_icon, (self._settings.SCREEN_WIDTH // 2 - 50, 100))

                error_text = font_large.render(f"FATAL ERROR loading {missing_file}.", True, RED)
                error_rect = error_text.get_rect(center=(self._settings.SCREEN_WIDTH // 2, 180))
                screen.blit(error_text, error_rect)

                with self.countdown_lock:
                    seconds_text = f"Program will be terminated in {self.countdown_time} second" + (
                        "s" if self.countdown_time > 1 else "") + " (or press ESCAPE to terminate now)."
                countdown_text = font_small.render(seconds_text, True, WHITE)
                countdown_rect = countdown_text.get_rect(center=(self._settings.SCREEN_WIDTH // 2, 300))
                screen.blit(countdown_text, countdown_rect)

                pygame.display.flip()

                pygame.time.wait(1)

            pygame.quit()
            sys.exit()

