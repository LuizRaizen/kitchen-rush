import pygame
from pygame.math import Vector2


class CharacterPart:
    """
    Representa uma parte do corpo (ex: braço, cabeça, cabelo) com posição relativa, rotação e imagem.
    Pode ser rotacionada em torno de um ponto base (bone).
    """
    def __init__(self, image: pygame.Surface, offset: Vector2 = Vector2(0, 0)):
        self.image = image
        self.offset = offset  # posição relativa ao bone pai
        self.angle = 0.0  # ângulo atual em graus

    def draw(self, surface, parent_position: Vector2, parent_angle: float = 0.0):
        """
        Desenha a parte na tela com rotação e posição relativa ao pai.
        """
        # Combina a rotação do pai com a da parte
        total_angle = self.angle + parent_angle

        # Rotaciona a imagem
        rotated_image = pygame.transform.rotate(self.image, -total_angle)
        rotated_rect = rotated_image.get_rect(center=(parent_position + self.offset))

        surface.blit(rotated_image, rotated_rect)
