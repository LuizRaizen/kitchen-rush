"""
Módulo phase_service.

Contém a classe PhaseService, que representa a tela principal de gameplay,
onde o jogador gerencia o restaurante em tempo real, lida com clientes,
controla o tempo, acessa recursos como o calendário, cardápio e mercado.
"""

import pygame
import random

from settings import Settings
from utils.audio_manager import audio_manager
from core.states.calendar import Calendar
from core.states.menu import Menu
from core.states.supermarket import Supermarket
from core.gui.ui_button import UIButton
from core.assets.customers import CommonCustomer, ImpatientCustomer, BossCustomer
from core.assets.furniture import Table
from core.assets.hud import Money, Clock


class PhaseService:
    """
    Representa a fase de atendimento do jogo.

    Exibe o salão do restaurante, gerencia os clientes, as mesas e os botões
    laterais para acessar funcionalidades como o cardápio, mercado e calendário.
    """

    def __init__(self, game):
        """
        Inicializa a tela de atendimento com HUD, mesas, botões e imagens.

        :param game: Instância principal do jogo.
        """
        self.game = game
        self.config = Settings()
        self.screen_rect = pygame.Rect(0, 0, self.config.SCREEN['width'], self.config.SCREEN['height'])

        # Fontes usadas na HUD
        self.font = pygame.font.SysFont("arial", 24)
        self.money_font = pygame.font.Font(self.config.MONEY['font'], self.config.MONEY['font_size'])
        self.clock_font = pygame.font.Font(self.config.CLOCK['font'], self.config.CLOCK['font_size'])

        # HUD de dinheiro
        money_image = pygame.image.load(self.config.MONEY['image']).convert_alpha()
        self.player_money = Money(-20, 20, money_image, self.money_font, game=self.game)

        # HUD de relógio
        clock_image = pygame.image.load(self.config.CLOCK['image'])
        self.game.clock = Clock(
            x=self.screen_rect.width // 2 - 90,
            y=self.screen_rect.top + 10,
            clock_image=clock_image,
            font=self.clock_font
        )

        # Fundo da tela do restaurante
        self.bg_image = pygame.image.load('graphics/backgrounds/bg_1.png')

        # Sprites das cadeiras por posição
        self.chair_sprites = {
            "topleft": pygame.image.load("graphics/sprites/chair_1_topleft.png"),
            "topcenter": pygame.image.load("graphics/sprites/chair_1_topcenter.png"),
            "topright": pygame.image.load("graphics/sprites/chair_1_topright.png"),
            "bottomleft": pygame.image.load("graphics/sprites/chair_1_bottomleft.png"),
            "bottomcenter": pygame.image.load("graphics/sprites/chair_1_bottomcenter.png"),
            "bottomright": pygame.image.load("graphics/sprites/chair_1_bottomright.png"),
        }

        # Criação das mesas com posições fixas
        self.tables = [
            Table(251, 150, 2),
            Table(569, 150, 4),
            Table(223, 350, 1),
            Table(600, 350, 6)
        ]
        for table in self.tables:
            table.chair_sprites = self.chair_sprites
            table.chairs = table._generate_chairs()

        # Sistema de spawn de clientes
        self.customer_id = 1
        self.spawn_timer = 0
        self.spawn_delay = 5  # segundos

        # Carregamento dos botões laterais
        self.card_bg = pygame.image.load("graphics/sprites/card_bg.png").convert_alpha()
        self.card_icons = {
            'waiter': pygame.image.load("graphics/sprites/hire_waiter.png").convert_alpha(),
            'cook': pygame.image.load("graphics/sprites/hire_cook.png").convert_alpha(),
            'manager': pygame.image.load("graphics/sprites/acess_rh.png").convert_alpha(),
            'menu': pygame.image.load("graphics/sprites/acess_menu.png").convert_alpha(),
            'market': pygame.image.load("graphics/sprites/acess_market.png").convert_alpha(),
            'calendar': pygame.image.load("graphics/sprites/acess_calendar.png").convert_alpha()
        }

        # Criação dos botões de ação
        self.cards = {
            'waiter': UIButton(840,  30, self.card_bg, self.card_icons['waiter'],
                            hover_sound='hover', click_sound='click', enable_scale=True),
            'cook': UIButton(840, 125, self.card_bg, self.card_icons['cook'],
                            hover_sound='hover', click_sound='click', enable_scale=True),
            'manager': UIButton(840, 222, self.card_bg, self.card_icons['manager'],
                                hover_sound='hover', click_sound='click', enable_scale=True),
            'menu': UIButton(840, 318, self.card_bg, self.card_icons['menu'],
                            hover_sound='hover', click_sound='click', enable_scale=True),
            'market': UIButton(840, 415, self.card_bg, self.card_icons['market'],
                            hover_sound='hover', click_sound='click', enable_scale=True),
            'calendar': UIButton(20, 415, self.card_bg, self.card_icons['calendar'],
                                hover_sound='hover', click_sound='click', enable_scale=True),
        }

        # Flags de telas ativas (controla as janelas flutuantes)
        self.game.menu = None
        self.game.supermarket = None
        self.game.calendar = None

        # fila para abrir um overlay assim que os cards terminarem de desaparecer
        self._pending_overlay = None  # tuple (name_str, factory_callable)

        # Deixa todos os botões invisíveis ANTES de qualquer render
        for card in self.cards.values():
            card.anim_scale = 0.75
            card.anim_alpha = 0.0
            # opcional: card._visible_flag = True  # mantém como “visível” logicamente
            
        # Estado de visibilidade da UI para animar aparecer/sumir dos botões
        self._ui_was_visible = None  # força o primeiro _sync a disparar animação
        self._sync_ui_visibility(force=True)

        # Cursor do mouse
        self.cursor_image = pygame.image.load(self.config.MOUSE['image'])
        self.cursor_image = pygame.transform.scale(self.cursor_image, (57, 40))
        pygame.mouse.set_visible(False)

        # Música de fundo
        audio_manager.play_music("gameplay")

    def create_random_client(self, id):
        """
        Cria um cliente aleatório (comum, impaciente ou chefe).

        :param id: ID numérico do cliente.
        :return: Instância de cliente.
        """
        tipo = random.choices(
            [CommonCustomer, ImpatientCustomer, BossCustomer],
            weights=[0.7, 0.25, 0.05]
        )[0]
        return tipo(id, self.game.player_menu)

    def spawn_customer_group(self):
        """
        Cria e posiciona um novo grupo de clientes em uma mesa disponível.
        """
        group_size = random.choice([1, 2])
        group = [self.create_random_client(self.customer_id + i) for i in range(group_size)]
        self.customer_id += group_size

        for table in self.tables:
            if table.is_available() and table.capacity >= group_size:
                table.seat_customers(group)
                return
            
    def _ui_should_be_visible(self) -> bool:
        # Visível quando NÃO há overlays
        return not (self.game.menu or self.game.supermarket or self.game.calendar)

    def _sync_ui_visibility(self, force: bool = False):
        """
        Detecta mudança de estado (com/sem overlay) e dispara a animação
        de aparecer/sumir dos botões. Se force=True, sempre reavalia e toca.

        IMPORTANTE: se houver overlay pendente (_pending_overlay), tratamos a UI
        como "não visível" para forçar o disappear ANTES de criar o overlay.
        """
        # Estado “normal” (sem pendência): UI visível quando NÃO há overlays abertos
        ui_visible_now = self._ui_should_be_visible()

        # Se há overlay pendente, queremos esconder os cards imediatamente
        if self._pending_overlay is not None:
            ui_visible_now = False

        if force or (self._ui_was_visible is None) or (ui_visible_now != self._ui_was_visible):
            if ui_visible_now:
                # gameplay “livre”: aparecer
                for card in self.cards.values():
                    card.appear()
            else:
                # menu aberto OU pendente: sumir
                for card in self.cards.values():
                    card.disappear()

            self._ui_was_visible = ui_visible_now

    def _all_cards_hidden(self) -> bool:
        """Retorna True quando TODOS os cards concluíram o disappear (alpha ~0 e sem timeline rodando)."""
        for card in self.cards.values():
            if card.anim_alpha > 0.01 or card.is_playing():
                return False
        return True

    def _request_open_overlay(self, name: str, factory):
        """
        Agenda a abertura de um overlay (menu/market/calendar) para depois que
        os cards terminarem o disappear.
        """
        # marca a intenção
        self._pending_overlay = (name, factory)
        # dispara imediatamente o disappear dos cards
        self._sync_ui_visibility(force=True)

    def update(self, dt):
        """
        Atualiza os elementos da fase de atendimento.

        :param dt: Delta time.
        """
        # 1) Sincroniza (dispara appear/disappear quando o estado muda)
        self._sync_ui_visibility()

        # 2) Pausa global:
        #    - quando há overlay ABERTO (UI não visível)
        #    - ou quando há overlay PENDENTE (durante o disappear dos cards)
        paused = (self._pending_overlay is not None) or (not self._ui_should_be_visible())
        dt_gameplay = 0.0 if paused else dt

        # 3) Gameplay só avança quando não está pausado
        if not paused:
            self.game.clock.update(dt_gameplay)

            # Lógica de aparição automática de clientes
            self.spawn_timer += dt_gameplay
            if self.spawn_timer >= self.spawn_delay:
                self.spawn_customer_group()
                self.spawn_timer = 0

            for table in self.tables:
                table.update(dt_gameplay)

        # 4) Botões SEMPRE atualizam animação; input só quando não pausado
        for card in self.cards.values():
            card._interactive = not paused  # consumido em UIButton.update(...)
            card.update(dt)

        # 5) Se há overlay pendente, só cria quando todos os cards terminarem de desaparecer
        if self._pending_overlay and self._all_cards_hidden():
            name, factory = self._pending_overlay
            setattr(self.game, name, factory())  # cria o overlay (menu/market/calendar)
            self._pending_overlay = None
            # No próximo frame, _sync_ui_visibility perceberá overlay aberto e manterá os cards ocultos

        # 6) Atualizações das janelas sobrepostas (caso ativas)
        if self.game.menu:
            self.game.menu.update(dt)
        elif self.game.supermarket:
            self.game.supermarket.update(dt)
        elif self.game.calendar:
            self.game.calendar.update(dt)

    def render(self, screen):
        """
        Renderiza todos os elementos da tela de atendimento.

        :param screen: Surface principal onde tudo será desenhado.
        """
        screen.blit(self.bg_image, (0, 0))

        paused = not self._ui_should_be_visible()

        # HUD quando livre
        if not paused:
            self.game.clock.render(screen)
            self.player_money.render(screen)

        # SEMPRE renderizar os cards (alpha controla visibilidade/efeito)
        for card in self.cards.values():
            card.render(screen)

        # Mesas só quando livre
        if not paused:
            for table in self.tables:
                table.render(screen, self.font)

        # Renderiza sobreposições se estiverem ativas
        if self.game.menu:
            self.game.menu.render(screen)
        elif self.game.supermarket:
            self.game.supermarket.render(screen)
        elif self.game.calendar:
            self.game.calendar.render(screen)

        # Cursor customizado do mouse
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(self.cursor_image, mouse_pos)

    def handle_event(self, event):
        """
        Trata eventos de clique nos cards e janelas abertas.

        :param event: Evento capturado pelo pygame.
        """
        # Eventos nos cards apenas quando o jogo estiver livre (sem janelas abertas)
        # e sem overlay pendente (para não agendar duas vezes).
        if (not self.game.calendar and not self.game.menu and not self.game.supermarket
            and self._pending_overlay is None):
            if event.type == pygame.MOUSEBUTTONDOWN:
                for card_name, card in self.cards.items():
                    if card.rect.collidepoint(event.pos):
                        if card_name == 'waiter':
                            print("A tela de contratação de garçons foi aberta!")
                        elif card_name == 'cook':
                            print("A tela de contratação de cozinheiros foi aberta!")
                        elif card_name == 'manager':
                            print("A tela do RH foi aberta!")
                        elif card_name == 'menu':
                            # agenda abrir Menu após os cards sumirem
                            self._request_open_overlay('menu', lambda: Menu(self.game))
                        elif card_name == 'market':
                            self._request_open_overlay('supermarket', lambda: Supermarket(self.game))
                        elif card_name == 'calendar':
                            self._request_open_overlay('calendar', lambda: Calendar(self.game))

                        # Som de clique do botão
                        card.handle_event(event)

        # Encaminha os eventos para janelas abertas
        if self.game.menu:
            self.game.menu.handle_event(event)
        elif self.game.supermarket:
            self.game.supermarket.handle_event(event)
        elif self.game.calendar:
            self.game.calendar.handle_event(event)
