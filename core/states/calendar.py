import pygame
import calendar
from datetime import datetime

from settings import Settings
from core.effects.animated_popup import AnimatedPopup
from core.gui.ui_button import UIButton
from utils.functions import render_text_with_outline


class Calendar(AnimatedPopup):
    """
    Classe responsável por exibir o calendário do jogo com sistema de transição suave entre páginas mensais.
    Herda animações de entrada/saída de AnimatedPopup.
    """

    def __init__(self, game):
        """
        Inicializa o calendário com a imagem do mês atual, botões de navegação e a grade de dias.

        :param game: Referência para o objeto principal do jogo.
        """
        self.game = game
        self.config = Settings()

        # Controle de transição entre meses
        self.current_month = datetime.now().month - 1  # Começa no mês atual
        self.current_year = datetime.now().year
        self.transitioning = False
        self.transition_direction = 0
        self.transition_progress = 0.0
        self.transition_duration = 0.4  # segundos

        # Fontes e nomes dos meses
        self.month_names = [
            "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
            "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
        ]
        font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 38)
        self.month_title = render_text_with_outline(font, self.month_names[self.current_month], (255, 255, 255), (0, 0, 0))
        self.month_title_rect = self.month_title.get_rect(center=(self.config.SCREEN['width'] // 2, 30))

        # Superfície base do calendário
        surface = pygame.image.load('graphics/images/calendar.png')
        self.pages = [surface for _ in range(12)]  # Por enquanto, usa a mesma imagem

        self.current_surface = self.pages[self.current_month]
        self.next_surface = self.current_surface
        self.current_rect = self.current_surface.get_rect(center=(self.config.SCREEN['width'] // 2,
                                                                  self.config.SCREEN['height'] // 2))
        self.next_rect = self.current_rect.copy()

        # Inicializa a popup
        super().__init__(
            screen_width=self.config.SCREEN['width'],
            screen_height=self.config.SCREEN['height'],
            content_surface=self.current_surface,
            open_sound='swipe',
            close_sound='swipe'
        )

        # Botões superiores
        button_image = pygame.image.load('graphics/sprites/go_back.png')
        self.go_back = UIButton(self.screen_width - 210, 10, button_image, enable_scale=True,)

        left_arrow = pygame.image.load('graphics/sprites/arrow_left.png')
        right_arrow = pygame.image.load('graphics/sprites/arrow_right.png')

        self.prev_button = UIButton(
            60, self.screen_height // 2 - 25,
            left_arrow,
            hover_sound='hover',
            click_sound='swipe',
            enable_scale=True,
        )
        self.next_button = UIButton(
            self.screen_width - 130, self.screen_height // 2 - 25,
            right_arrow,
            hover_sound='hover', click_sound='swipe',
            enable_scale=True,
        )

        # Cria os botões dos dias do mês
        self.day_buttons = []
        self.create_day_buttons()

    def create_day_buttons(self):
        """Cria os botões representando os dias do mês atual."""
        self.day_buttons.clear()

        # Cálculo do primeiro dia da semana e número de dias do mês
        first_weekday, num_days = calendar.monthrange(self.current_year, self.current_month + 1)

        day_image = pygame.image.load('graphics/sprites/calendar_button.png')
        day_rect = day_image.get_rect()
        font = pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 30)

        # Tamanho base de célula (7 colunas, até 6 linhas)
        cell_width = day_rect.width - 4
        cell_height = day_rect.height - 5
        start_x = 168
        start_y = 195

        for day in range(1, num_days + 1):
            col = (first_weekday + day - 1) % 7
            row = (first_weekday + day - 1) // 7

            x = start_x + col * cell_width
            y = start_y + row * cell_height

            button = UIButton(
                x, y,
                day_image,
                text=str(day),
                font=font, text_color=(0, 0, 0),
                enable_fade=True,
                fade_speed=8,
                fade_color=(255, 255, 100),
                fade_max_alpha=255
            )
            self.day_buttons.append(button)

    def update(self, dt):
        """Atualiza a animação da popup e a transição horizontal entre páginas."""
        super().update(dt)

        if self.animation_done and not self.closing:
            if self.transitioning:
                self.transition_progress += dt / self.transition_duration
                progress = min(self.transition_progress, 1.0)
                eased = 1 - (1 - progress) ** 2
                offset = self.screen_width
                direction = self.transition_direction

                self.current_rect.centerx = self.screen_width // 2 - int(offset * eased * direction)
                self.next_rect.centerx = self.screen_width // 2 + int(offset * (1 - eased) * direction)

                if progress >= 1.0:
                    self.transitioning = False
                    self.current_month = max(0, min(self.current_month + direction, 11))
                    self.current_surface = self.pages[self.current_month]
                    self.month_title = render_text_with_outline(
                        pygame.font.Font('fonts/LuckiestGuy-Regular.ttf', 38),
                        self.month_names[self.current_month], (255, 255, 255), (0, 0, 0)
                    )
                    self.create_day_buttons()
                    self.set_content_surface(self.current_surface)
                    self.current_rect = self.current_surface.get_rect(center=(self.screen_width // 2,
                                                                              self.screen_height // 2))
            else:
                self.go_back.update(dt)
                self.prev_button.update(dt)
                self.next_button.update(dt)
                for button in self.day_buttons:
                    button.update(dt)

    def render(self, screen):
        """Renderiza o calendário e os botões de navegação e dias."""
        screen.blit(self.bg_surface, (0, 0))
        y = self.rect.top

        if self.transitioning:
            screen.blit(self.current_surface, (self.current_rect.left, y))
            screen.blit(self.next_surface, (self.next_rect.left, y))
        else:
            # Fundo do calendário
            screen.blit(self.current_surface, (self.rect.left, y))

            # Título do mês
            self.month_title_rect = self.month_title.get_rect(center=(self.config.SCREEN['width'] // 2, 30))
            screen.blit(self.month_title, (self.month_title_rect.left, y + 88))

            if self.animation_done and not self.closing:
                self.go_back.render(screen)
                self.prev_button.render(screen)
                self.next_button.render(screen)

                # Primeiro renderiza todos os botões que NÃO estão em hover
                hovered_button = None
                for button in self.day_buttons:
                    if button.hovered:
                        hovered_button = button
                        button.render_at(screen, y_offset=y)
                    else:
                        button.render_at(screen, y_offset=y)

                # Depois renderiza o botão que está em hover, acima de todos
                if hovered_button:
                    hovered_button.render_at(screen, y_offset=y)

    def handle_event(self, event):
        """Processa eventos de clique nos botões do calendário."""
        if self.animation_done and not self.closing and not self.transitioning:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.go_back.rect.collidepoint(event.pos):
                    self.start_closing()
                elif self.prev_button.rect.collidepoint(event.pos):
                    self.start_transition(-1)
                elif self.next_button.rect.collidepoint(event.pos):
                    self.start_transition(1)

            for button in (self.prev_button, self.next_button):
                button.handle_event(event)

            for day_button in self.day_buttons:
                day_button.handle_event(event)

    def start_transition(self, direction):
        """Inicia a animação horizontal para o mês anterior ou próximo."""
        new_month = self.current_month + direction
        if not (0 <= new_month <= 11):
            return

        self.transitioning = True
        self.transition_direction = direction
        self.transition_progress = 0.0

        self.next_surface = self.pages[new_month]
        if direction == 1:
            self.next_rect = self.next_surface.get_rect(center=(self.screen_width + self.screen_width // 2,
                                                                self.screen_height // 2))
        else:
            self.next_rect = self.next_surface.get_rect(center=(-self.screen_width // 2,
                                                                self.screen_height // 2))

    def on_close(self):
        """Remove o calendário da instância do jogo."""
        self.game.calendar = None
