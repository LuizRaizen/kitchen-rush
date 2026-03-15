"""Módulo uqe armazena as mesas e as cadeiras do jogo."""

import math
import pygame

from core.assets.patience_meter import PatienceMeter


class Table:
    """Representa uma mesa com cadeiras e clientes associados."""
    def __init__(self, x, y, capacity):
        # Posição
        self.x = x
        self.y = y

        # Imagem da mesa
        self.image = pygame.image.load('graphics/sprites/table_1.png')

        # Rect da mesa
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Sombra
        self.shadow = pygame.Surface((self.rect.width, self.rect.height // 2))
        self.shadow.set_colorkey((0, 255, 0))
        self.shadow.set_alpha(80)
        self.shadow_rect = self.shadow.get_rect()

        # Capacidade
        self.capacity = capacity

        # Sprites de cadeiras
        self.chair_sprites = []

        # Clientes
        self.customers = []

        # Config da barra de paciência
        self._meter_radius = 44
        self._meter_thickness = 10
        self._meter_offset_y = 36  # distância acima da mesa

        # Cadeiras
        self.chairs = self._generate_chairs()

        # Medidor de paciência (objeto animável encapsulado)
        self.patience_meter = PatienceMeter(
            center=(self.rect.centerx, self.rect.top - self._meter_offset_y),
            radius=self._meter_radius,
            thickness=self._meter_thickness,
            aperture_deg=100,
            outline_width_px=2,
            upscale=2
        )

    def _generate_chairs(self):
        """Gera cadeiras com base na capacidade e posicionamento ao redor da mesa."""
        directions = [
            "topleft", "topcenter", "topright",
            "bottomleft", "bottomcenter", "bottomright"
        ]
        chairs = []

        offsets = {
            "topleft":      (-70, -40),
            "topcenter":    (0, -60),
            "topright":     (70, -40),
            "bottomleft":   (-70, 20),
            "bottomcenter": (0, 40),
            "bottomright":  (70, 20)
        }

        for i in range(min(self.capacity, len(directions))):
            dir = directions[i]
            dx, dy = offsets[dir]
            chair = Chair(self.rect.centerx + dx, self.rect.centery + dy,
                          direction=dir, sprite_dict=self.chair_sprites)
            chairs.append(chair)

        return chairs

    def is_available(self):
        return len(self.customers) == 0

    def seat_customers(self, group):
        if len(group) <= self.capacity and self.is_available():
            self.customers = group

            # zera timers de espera
            for c in self.customers:
                c.timer = 0.0

            # ocupa cadeiras
            for i, customer in enumerate(group):
                self.chairs[i].occupied = True

            # posiciona e anima o medidor surgindo
            self.patience_meter.center = (self.rect.centerx, self.rect.top - self._meter_offset_y)
            self.patience_meter.set_ratio(self._group_patience_ratio())
            self.patience_meter.appear()
            return True
        return False

    def _group_patience_ratio(self) -> float:
        if not self.customers:
            return 0.0
        total_max = sum(getattr(c, "max_patience", 0.0) for c in self.customers if c.status != "left")
        if total_max <= 0:
            return 0.0
        total_rem = sum(c.patience_remaining() for c in self.customers if c.status != "left")
        return max(0.0, min(1.0, total_rem / total_max))

    def update(self, dt):
        # Atualiza clientes
        for c in list(self.customers):
            c.update(dt)

        # Libera mesa quando todos saem ou a paciência zerou
        if self.customers:
            ratio = self._group_patience_ratio()
            if all(c.status == "left" for c in self.customers) or ratio <= 0.0:
                self.clear()
            else:
                # mantém o medidor vivo e atualizado
                self.patience_meter.center = (self.rect.centerx, self.rect.top - self._meter_offset_y)
                self.patience_meter.set_ratio(ratio)
        else:
            # se ficou sem clientes, inicia animação de saída (se necessário)
            if self.patience_meter.is_visible() and not self.patience_meter.is_playing("disappear"):
                self.patience_meter.disappear()

        # Atualiza animações do medidor
        self.patience_meter.update(dt)

    def clear(self):
        self.customers = []
        for chair in self.chairs:
            chair.occupied = False
        # anima a barra saindo
        if self.patience_meter.is_visible() and not self.patience_meter.is_playing("disappear"):
            self.patience_meter.disappear()

    def render(self, screen, font):
        # Sombra da mesa
        screen.blit(self.shadow, (self.rect.x, self.rect.bottom - (self.rect.height // 2) + 12))
        self.shadow.fill((0, 255, 0))
        pygame.draw.ellipse(self.shadow, (0, 0, 0), self.shadow_rect)

        # Cadeiras de trás
        for chair in self.chairs:
            if chair.direction in ('topleft', 'topcenter', 'topright'):
                chair.draw(screen)

        # Mesa
        screen.blit(self.image, (self.x, self.y))

        # Cadeiras da frente
        for chair in self.chairs:
            if chair.direction in ('bottomleft', 'bottomcenter', 'bottomright'):
                chair.draw(screen)

        # Desenha a barra de paciência (animada e encapsulada)
        self.patience_meter.center = (self.rect.centerx, self.rect.top - self._meter_offset_y)
        self.patience_meter.draw(screen)

        # Texto de capacidade
        text = font.render(f"{len(self.customers)}/{self.capacity}", True, (255, 255, 255))
        text_rect = text.get_rect()
        screen.blit(text, (self.rect.x + (self.rect.width // 2) - (text_rect.width // 2), self.rect.y - 90))

        # Clientes (sobre as cadeiras)
        for i, customer in enumerate(self.customers):
            if i < len(self.chairs):
                chair = self.chairs[i]
                customer.draw(screen, chair.x, chair.y - 25, font)


class Chair:
    """Representa uma cadeira no salão do restaurante."""
    def __init__(self, x, y, direction="bottomcenter", sprite_dict=None):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(0, 0, 80, 117)
        self.direction = direction
        self.occupied = False
        self.sprite_dict = sprite_dict or {}  # dicionário com sprites por direção

        # Cria uma sombra para a mesa
        self.shadow = pygame.Surface((self.rect.width - 20, self.rect.height // 4))
        self.shadow.set_colorkey((0, 255, 0))
        self.shadow.set_alpha(80)
        self.shadow_rect = self.shadow.get_rect()

    def draw(self, screen):
        # Renderiza a sombra da mesa
        screen.blit(self.shadow, (self.rect.x + 10, self.rect.bottom - (self.rect.height // 2) + 22))
        self.shadow.fill((0, 255, 0))
        pygame.draw.ellipse(self.shadow, (0, 0, 0), self.shadow_rect)

        # Renderiza a imagem da cadeira
        sprite = self.sprite_dict.get(self.direction)
        self.rect = sprite.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y
        if sprite:
            screen.blit(sprite, self.rect)
        else:
            # fallback visual (debug)
            color = (160, 100, 60) if not self.occupied else (100, 160, 220)
            pygame.draw.rect(screen, color, (self.x, self.y, 20, 20))
