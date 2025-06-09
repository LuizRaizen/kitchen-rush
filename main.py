"""Módulo main."""

import pygame

from settings import Settings
from core.game import Game


def main():
    """Função do jogo."""
    pygame.init()
    config = Settings()
    screen = pygame.display.set_mode((config.SCREEN['width'], config.SCREEN['height']))
    pygame.display.set_caption("Kitchen Rush")
    clock = pygame.time.Clock()

    game = Game()

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        # Atualiza os elementos do jogo
        game.update(dt)
        # Renderiza os elementos do jogo
        game.render(screen)
        # Atualiza a tela a cada loop
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
