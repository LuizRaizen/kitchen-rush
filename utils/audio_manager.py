import pygame


class AudioManager:
    """
    Classe responsável por gerenciar os efeitos sonoros e músicas do jogo Kitchen Rush.
    
    Essa classe centraliza o carregamento e reprodução de sons, garantindo que os mesmos
    não sejam carregados repetidamente durante o jogo.
    """

    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}         # Dicionário de efeitos sonoros
        self.musics = {}         # Dicionário de trilhas musicais
        self.current_music = None  # Nome da música atual

        # Volumes (0.0 a 1.0)
        self.music_volume = 0.6
        self.sound_volume = 0.7

    def load_sound(self, name, path):
        """
        Carrega um efeito sonoro a partir do caminho fornecido.
        
        :param name: Nome identificador do som.
        :param path: Caminho para o arquivo de som.
        """
        sound = pygame.mixer.Sound(path)
        sound.set_volume(self.sound_volume)
        self.sounds[name] = pygame.mixer.Sound(sound)

    def play_sound(self, name):
        """
        Reproduz um efeito sonoro previamente carregado.
        
        :param name: Nome do som a ser reproduzido.
        """
        if name in self.sounds:
            self.sounds[name].play()

    def load_music(self, name, path):
        """
        Registra uma trilha sonora, associando-a a um nome.
        
        :param name: Nome identificador da música.
        :param path: Caminho para o arquivo de música.
        """
        self.musics[name] = path

    def play_music(self, name, loop=True):
        """
        Inicia a reprodução de uma trilha sonora.
        Se a música já estiver tocando, não reinicia.
        
        :param name: Nome da música.
        :param loop: Se True, a música toca em loop.
        """
        if name in self.musics:
            if self.current_music == name and pygame.mixer.music.get_busy():
                return  # Música já está tocando
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.musics[name])
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music = name

    def stop_music(self):
        """
        Interrompe a música atual, se estiver tocando.
        """
        pygame.mixer.music.stop()
        self.current_music = None

    def set_music_volume(self, volume):
        """
        Define o volume da música de fundo.
        :param volume: Valor entre 0.0 e 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

    def set_sound_volume(self, volume):
        """
        Define o volume dos efeitos sonoros.
        :param volume: Valor entre 0.0 e 1.0
        """
        self.sound_volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            sound.set_volume(self.sound_volume)

    def get_music_volume(self):
        """Retorna o volume atual da música."""
        return self.music_volume

    def get_sound_volume(self):
        """Retorna o volume atual dos efeitos sonoros."""
        return self.sound_volume


# Instância global do gerenciador de áudio
audio_manager = AudioManager()

# === Carregamento inicial dos sons do jogo ===

# Efeitos sonoros
audio_manager.load_sound("hover", "audio/sounds/effects/hover_effect.wav")
audio_manager.load_sound("click", "audio/sounds/effects/ui_click.wav")
audio_manager.load_sound("swipe", "audio/sounds/effects/swipe_effect_2.wav")
#audio_manager.load_sound("open_menu", "audio/sounds/effects/open_menu.wav")
#audio_manager.load_sound("close_menu", "audio/sounds/effects/close_menu.wav")
#audio_manager.load_sound("coin", "audio/sounds/effects/coin.wav")
#audio_manager.load_sound("bell", "audio/sounds/effects/bell.wav")
#audio_manager.load_sound("error", "audio/sounds/effects/error.wav")

# Músicas de fundo
#audio_manager.load_music("menu", "sounds/bgm/menu_theme.mp3")
#audio_manager.load_music("gameplay", "sounds/bgm/gameplay_loop.mp3")
#audio_manager.load_music("victory", "sounds/bgm/victory.mp3")
#audio_manager.load_music("defeat", "sounds/bgm/defeat.mp3")
