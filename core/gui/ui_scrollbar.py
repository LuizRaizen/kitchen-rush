"""Módulo que armazena a classe para criar uma barra de rolagem."""

import pygame


class UIScrollbar:
    """
    Componente reutilizável de interface gráfica que representa uma barra de rolagem vertical com animação,
    personalização visual e suporte a LERP.

    Pode ser usada em diversas interfaces (menus, listas, painéis, inventários, etc).

    Args:
        x (int): Posição horizontal da barra.
        y (int): Posição vertical da barra.
        height (int): Altura da área visível (viewport).
        content_height (int): Altura total do conteúdo a ser rolado.
        view_height (int): Altura da área visível do conteúdo.
        width (int): Largura padrão da barra (botão).
        hover_scale (float): Multiplicador da largura ao passar o mouse (ex: 1.5).
        bar_color (tuple): Cor RGB do botão da barra, se não for usada imagem.
        bg_color (tuple): Cor RGB do fundo da barra, se não for usada imagem.
        bar_image (Surface or None): Imagem do botão da barra (opcional).
        bg_image (Surface or None): Imagem do fundo da barra (opcional).
    """

    def __init__(self, x, y, height, content_height, view_height,
                 width=8, hover_scale=1.5, bar_color=(100, 70, 40), bg_color=(180, 130, 100),
                 bar_image=None, bg_image=None):

        self.x = x
        self.y = y
        self.height = height
        self.content_height = content_height
        self.view_height = view_height

        self.bar_color = bar_color
        self.bg_color = bg_color
        self.bar_image = bar_image
        self.bg_image = bg_image

        self.default_width = width
        self.hover_width = int(width * hover_scale)
        self.current_width = width

        if content_height > view_height:
            self.bar_height = max(40, int(view_height * (view_height / content_height)))
        else:
            self.bar_height = height

        self.bar_rect = pygame.Rect(x, y, width, self.bar_height)

        self.dragging = False
        self.mouse_offset_y = 0
        self.hover_speed = 12.0

    def handle_event(self, event):
        """Lida com os eventos de clique, arrasto e liberação do mouse sobre a barra."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.bar_rect.collidepoint(event.pos):
            self.dragging = True
            self.mouse_offset_y = event.pos[1] - self.bar_rect.y
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.mouse_offset_y
            new_y = max(self.y, min(self.y + self.height - self.bar_height, new_y))
            self.bar_rect.y = new_y

    def update(self, dt):
        """Atualiza a largura do botão da barra suavemente com base no hover ou arrasto."""
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.bar_rect.collidepoint(mouse_pos)

        target_width = self.hover_width if hovered or self.dragging else self.default_width
        self.current_width += (target_width - self.current_width) * min(self.hover_speed * dt, 1)

        center_x = self.x + self.default_width // 2
        self.bar_rect.width = int(self.current_width)
        self.bar_rect.x = center_x - self.bar_rect.width // 2

    def get_scroll_offset(self):
        """Retorna o deslocamento atual do conteúdo com base na posição da barra."""
        if self.height == self.bar_height:
            return 0
        scroll_ratio = (self.bar_rect.y - self.y) / (self.height - self.bar_height)
        return int(scroll_ratio * (self.content_height - self.view_height))

    def set_scroll_offset(self, offset):
        """Define a posição da barra com base em um deslocamento do conteúdo."""
        if self.content_height <= self.view_height:
            self.bar_rect.y = self.y
        else:
            scroll_ratio = offset / (self.content_height - self.view_height)
            self.bar_rect.y = int(scroll_ratio * (self.height - self.bar_height)) + self.y

    def render(self, screen):
        """Desenha a barra de rolagem (fundo + botão), com imagens ou cores."""
        if self.bg_image:
            bg_scaled = pygame.transform.scale(self.bg_image, (self.default_width, self.height))
            screen.blit(bg_scaled, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.bg_color, (self.x, self.y, self.default_width, self.height), border_radius=6)

        if self.bar_image:
            bar_scaled = pygame.transform.scale(self.bar_image, (self.bar_rect.width, self.bar_rect.height))
            screen.blit(bar_scaled, self.bar_rect.topleft)
        else:
            pygame.draw.rect(screen, self.bar_color, self.bar_rect, border_radius=6)

    def render_at(self, screen, y_offset=0):
        """Desenha a barra com um deslocamento vertical (ex: popups animadas)."""
        if self.bg_image:
            bg_scaled = pygame.transform.scale(self.bg_image, (self.default_width, self.height))
            screen.blit(bg_scaled, (self.x, self.y + y_offset))
        else:
            pygame.draw.rect(screen, self.bg_color, (self.x, self.y + y_offset, self.default_width, self.height), border_radius=6)

        bar_rect_y = self.bar_rect.y + y_offset
        bar_rect = pygame.Rect(self.bar_rect.x, bar_rect_y, self.bar_rect.width, self.bar_rect.height)

        if self.bar_image:
            bar_scaled = pygame.transform.scale(self.bar_image, (bar_rect.width, bar_rect.height))
            screen.blit(bar_scaled, bar_rect.topleft)
        else:
            pygame.draw.rect(screen, self.bar_color, bar_rect, border_radius=6)
