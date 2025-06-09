"""Funções úteis para o funcionamento do jogo."""

import pygame


def render_text_with_outline(font, text, text_color, outline_color, outline_width=2):
    # Renderiza o texto base
    base = font.render(text, True, text_color)

    # Cria uma superfície um pouco maior para o contorno
    size = (base.get_width() + 2 * outline_width, base.get_height() + 2 * outline_width)
    surface = pygame.Surface(size, pygame.SRCALPHA)

    # Desenha o contorno em várias direções
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                outline = font.render(text, True, outline_color)
                surface.blit(outline, (dx + outline_width, dy + outline_width))

    # Desenha o texto principal por cima
    surface.blit(base, (outline_width, outline_width))

    return surface
