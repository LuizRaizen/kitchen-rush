import pygame
from pygame.math import Vector2
import math
import sys

# === Setup inicial ===
pygame.init()
screen = pygame.display.set_mode((400, 400))
clock = pygame.time.Clock()


# === Classe CharacterPart ===
class CharacterPart:
    def __init__(self, image: pygame.Surface, offset: Vector2 = Vector2(0, 0)):
        self.image = image
        self.offset = offset
        self.angle = 0.0

    def draw(self, surface, parent_position: Vector2, parent_angle: float = 0.0):
        total_angle = self.angle + parent_angle
        rotated_image = pygame.transform.rotate(self.image, -total_angle)
        rotated_rect = rotated_image.get_rect(center=(parent_position + self.offset))
        surface.blit(rotated_image, rotated_rect)


# === Classe CharacterTemplate ===
class CharacterTemplate:
    def __init__(self, parts_dict: dict):
        self.parts = parts_dict
        self.position = Vector2(200, 200)
        self.facing_right = True

    def update(self, time):
        if 'left_arm' in self.parts:
            self.parts['left_arm'].angle = math.sin(time * 3) * 30
        if 'right_arm' in self.parts:
            self.parts['right_arm'].angle = math.sin(time * 3 + math.pi) * 30

    def draw(self, surface):
        base = self.position
        p = self.parts
        if 'legs' in p:
            p['legs'].draw(surface, base + Vector2(0, 40))
        if 'torso' in p:
            p['torso'].draw(surface, base)
        if 'head' in p:
            p['head'].draw(surface, base + Vector2(0, -50))
        if 'hair' in p:
            p['hair'].draw(surface, base + Vector2(0, -60))
        if 'left_arm' in p:
            p['left_arm'].draw(surface, base + Vector2(-25, -10))
        if 'right_arm' in p:
            p['right_arm'].draw(surface, base + Vector2(25, -10))


# === Criação das partes (simulando com blocos) ===
torso = pygame.image.load('graphics/sprites/characters/torso.png').convert_alpha()
head = pygame.image.load('graphics/sprites/characters/front_head.png').convert_alpha()
hair = pygame.Surface((50, 20), pygame.SRCALPHA)
hair.fill((100, 50, 20))
left_arm = pygame.image.load('graphics/sprites/characters/left_arm.png').convert_alpha()
right_arm = pygame.image.load('graphics/sprites/characters/right_arm.png').convert_alpha()
legs =  pygame.image.load('graphics/sprites/characters/left_leg.png').convert_alpha()

# === Instancia personagem ===
character = CharacterTemplate({
    'torso': CharacterPart(torso),
    'head': CharacterPart(head, Vector2(0, -50)),
    'hair': CharacterPart(hair, Vector2(0, -60)),
    'left_arm': CharacterPart(left_arm, Vector2(-25, -10)),
    'right_arm': CharacterPart(right_arm, Vector2(25, -10)),
    'legs': CharacterPart(legs, Vector2(0, 40)),
})


# === Loop principal ===
time = 0
running = True
while running:
    dt = clock.tick(60) / 1000.0
    time += dt

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))
    character.update(time)
    character.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
