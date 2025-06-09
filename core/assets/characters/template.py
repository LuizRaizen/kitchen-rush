import pygame
from pygame.math import Vector2
from core.assets.characters.parts import CharacterPart


class CharacterTemplate:
    """
    Template base para qualquer personagem (cliente, funcionário, etc).
    Possui partes substituíveis como cabelo, cabeça, uniforme, braços, etc.
    """
    def __init__(self, parts_dict: dict):
        """
        parts_dict: dicionário com as partes (ex: 'torso': CharacterPart, 'head': CharacterPart, ...)
        """
        self.parts = parts_dict
        self.position = Vector2(0, 0)  # posição base do personagem
        self.facing_right = True       # direção que está virado

    def set_position(self, x, y):
        self.position.update(x, y)

    def update(self, dt):
        # Aqui você pode aplicar lógica de animação
        pass

    def draw(self, surface):
        """
        Renderiza todas as partes do personagem em ordem correta.
        """
        base = self.position
        p = self.parts

        # Ordem de desenho importa (traseira → frontal)
        if not self.facing_right:
            surface = pygame.transform.flip(surface, True, False)

        if 'torso' in p:
            p['torso'].draw(surface, base)
        if 'legs' in p:
            p['legs'].draw(surface, base + Vector2(0, 40))
        if 'head' in p:
            p['head'].draw(surface, base + Vector2(0, -50))
        if 'hair' in p:
            p['hair'].draw(surface, base + Vector2(0, -60))
        if 'left_arm' in p:
            p['left_arm'].draw(surface, base + Vector2(-25, -10))
        if 'right_arm' in p:
            p['right_arm'].draw(surface, base + Vector2(25, -10))
