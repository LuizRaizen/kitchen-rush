"""Módulo uqe armazena as mesas e as cadeiras do jogo."""

import pygame

class Table:
    """Representa uma mesa com cadeiras e clientes associados."""
    def __init__(self, x, y, capacity):
        # Obtém a posição onde a mesa será criada
        self.x = x
        self.y = y

        # Carrega e configura a imagem da mesa
        self.image = pygame.image.load('graphics/sprites/table_2.png')

        # Cria um rect a partir da imagem da mesa
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        # Cria uma sombra para a mesa
        self.shadow = pygame.Surface((self.rect.width, self.rect.height // 2))
        self.shadow.set_colorkey((0, 255, 0))
        self.shadow.set_alpha(80)
        self.shadow_rect = self.shadow.get_rect()

        # Define a capacidade de assentos disponíveis
        self.capacity = capacity

        # Lista para armazenar as sprites das cadeiras
        self.chair_sprites = []

        # Lista para armazenar a quantidade de clientes na mesa
        self.customers = []

        # Cria as cadeiras que serão instânciadas na mesa
        self.chairs = self._generate_chairs()

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
            chair = Chair(self.rect.centerx + dx, self.rect.centery + dy, direction=dir, sprite_dict=self.chair_sprites)
            chairs.append(chair)

        return chairs
    
    def is_available(self):
        return len(self.customers) == 0
    
    def seat_customers(self, customers):
        if len(customers) <= self.capacity and self.is_available():
            self.customers = customers
            for i, customer in enumerate(customers):
                self.chairs[i].occupied = True
            return True
        return False

    def update(self, dt):
        for customer in self.customers:
            customer.update(dt)

        # Verifica se todos foram embora
        if all(c.status in ["left", "done"] for c in self.customers):
            self.clear()  # esvazia a mesa

    def clear(self):
        self.customers = []

        for chair in self.chairs:
            chair.occupied = False

    def render(self, screen, font):
        # Renderiza a sombra da mesa
        screen.blit(self.shadow, (self.rect.x, self.rect.bottom - (self.rect.height // 2) + 12))
        self.shadow.fill((0, 255, 0))
        pygame.draw.ellipse(self.shadow, (0, 0, 0), self.shadow_rect)

        # Renderiza as cadeiras da parte de trás da mesa
        for chair in self.chairs:
            if chair.direction in ('topleft', 'topcenter', 'topright'):
                chair.draw(screen)

        # Renderiza a mesa
        screen.blit(self.image, (self.x, self.y))

        # Renderiza cadeiras da parte da frente da mesa
        for chair in self.chairs:
            if chair.direction in ('bottomleft', 'bottomcenter', 'bottomright'):
                chair.draw(screen)

        # Renderiza o texto de notificação de capacidade
        text = font.render(f"{len(self.customers)}/{self.capacity}", True, (255, 255, 255))
        text_rect = text.get_rect()
        screen.blit(text, (self.rect.x + (self.rect.width // 2) - (text_rect.width // 2) , self.rect.y - 90))

        # Desenhar clientes exatamente em cima das cadeiras
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
