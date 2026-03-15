"""
SplashScreen (OpenCV + utils.audio_manager) com áudio extraído via FFmpeg.

Fluxo:
  pre_black (1.0s) → playing (vídeo + áudio) → post_black (1.0s) → MainMenu
Tecla/clique → pula imediatamente para o MainMenu.

Dependências:
- opencv-python
- ffmpeg instalado no sistema (acessível no PATH)
"""

import os
import sys
import hashlib
import subprocess
from pathlib import Path
import tempfile
import pygame
from core.states.main_menu import MainMenu

# === Import CORRETO do AudioManager ===
try:
    from utils.audio_manager import audio_manager  # instancia global
except Exception:
    audio_manager = None

# Ative para prints de debug (caminhos, estados etc.)
DEBUG_SPLASH = False

# ---------- Caminho robusto (dev e PyInstaller) ----------
def resource_path(*parts) -> str:
    dev_base = Path(__file__).resolve().parent.parent.parent  # .../core/states/../../.. = raiz
    base = Path(getattr(sys, "_MEIPASS", dev_base))
    return str(base.joinpath(*parts))

def _log(msg):
    if DEBUG_SPLASH:
        print(f"[SPLASH] {msg}")

def _ffmpeg_available() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def _cached_audio_path_for(video_path: str) -> str:
    """Gera um WAV em /tmp baseado em hash (path + mtime + size) para evitar re-extrair sempre."""
    p = Path(video_path)
    try:
        stat = p.stat()
        sig = f"{str(p.resolve())}|{stat.st_mtime_ns}|{stat.st_size}"
    except Exception:
        sig = str(p.resolve())
    h = hashlib.sha1(sig.encode("utf-8")).hexdigest()[:16]
    return os.path.join(tempfile.gettempdir(), f"splash_audio_{h}.wav")

def _extract_audio_to_wav(video_path: str, out_wav_path: str) -> bool:
    """Extrai áudio do MP4 para WAV 44.1kHz estéreo via ffmpeg. True se ok/existente."""
    if os.path.exists(out_wav_path) and os.path.getsize(out_wav_path) > 0:
        _log(f"WAV cache existente: {out_wav_path}")
        return True
    if not _ffmpeg_available():
        _log("FFmpeg não encontrado no PATH.")
        return False
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-ac", "2",
        "-ar", "44100",
        "-f", "wav",
        out_wav_path
    ]
    try:
        _log(f"Extraindo áudio com ffmpeg → {out_wav_path}")
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        ok = os.path.exists(out_wav_path) and os.path.getsize(out_wav_path) > 0
        _log(f"Extração: {'OK' if ok else 'FALHOU'}")
        return ok
    except Exception as e:
        _log(f"ffmpeg error: {e}")
        return False


class SplashScreen:
    def __init__(self, game):
        self.game = game
        self.config = game.config
        self.size = (self.config.SCREEN["width"], self.config.SCREEN["height"])

        # Timers de tela preta
        self.pre_black_sec = 1.0
        self.post_black_sec = 1.0

        # Estado
        self.state = "pre_black"   # "pre_black" | "playing" | "post_black" | "fallback"
        self._pre_timer = 0.0
        self._post_timer = 0.0
        self._skip_requested = False

        # Vídeo (OpenCV)
        self.video_path = resource_path("video", "splash_screen.mp4")
        self.cap = None
        self.fps = 30.0
        self.frame_interval = 1.0 / self.fps
        self._time_acc = 0.0
        self.frame_surface = None
        self.dst_size = self.size
        self.frame_pos = (0, 0)
        self._video_ok = self._open_video()

        # Áudio (via AudioManager + WAV extraído)
        self._audio_key = "splash_video_audio"
        self._audio_wav = None
        self._audio_ready = False
        self._audio_started = False
        self._prepare_and_register_audio()

        # Fallback (se não abrir vídeo)
        self.fallback_active = not self._video_ok
        if self.fallback_active:
            self.state = "fallback"
            self._setup_fallback()

        _log(f"video_ok={self._video_ok}, audio_ready={self._audio_ready}, wav={self._audio_wav}")

    # ============== Vídeo (OpenCV) ==============
    def _open_video(self) -> bool:
        try:
            import cv2
            self.cv2 = cv2
        except Exception as e:
            _log(f"cv2 import fail: {e}")
            return False

        if not os.path.exists(self.video_path):
            _log(f"MP4 não encontrado: {self.video_path}")
            return False

        cap = self.cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            _log("Falha ao abrir VideoCapture.")
            return False

        fps = float(cap.get(self.cv2.CAP_PROP_FPS) or 0.0)
        if fps <= 1e-3:
            fps = 30.0
        self.fps = fps
        self.frame_interval = 1.0 / self.fps

        vw = int(cap.get(self.cv2.CAP_PROP_FRAME_WIDTH))
        vh = int(cap.get(self.cv2.CAP_PROP_FRAME_HEIGHT))
        self.dst_size = self._calc_dst_size(vw, vh)
        self.frame_pos = self._calc_center_pos(self.dst_size)
        self.cap = cap
        _log(f"OpenCV: {vw}x{vh} @ {self.fps:.2f}fps → dst={self.dst_size}")
        return True

    def _calc_dst_size(self, vw, vh):
        sw, sh = self.size
        scale = min(sw / float(vw), sh / float(vh))
        return (int(vw * scale), int(vh * scale))

    def _calc_center_pos(self, dst_size):
        sw, sh = self.size
        dw, dh = dst_size
        return ((sw - dw) // 2, (sh - dh) // 2)

    # ============== Áudio (AudioManager + FFmpeg) ==============
    def _prepare_and_register_audio(self):
        """Extrai o áudio do MP4 (cacheado) e registra no AudioManager."""
        if audio_manager is None:
            _log("audio_manager não disponível.")
            self._audio_ready = False
            return
        if not os.path.exists(self.video_path):
            self._audio_ready = False
            return

        wav_path = _cached_audio_path_for(self.video_path)
        ok = _extract_audio_to_wav(self.video_path, wav_path)
        if not ok:
            self._audio_ready = False
            return

        try:
            audio_manager.load_music(self._audio_key, wav_path)
            self._audio_wav = wav_path
            self._audio_ready = True
        except Exception as e:
            _log(f"load_music falhou: {e}")
            self._audio_ready = False
            self._audio_wav = None

    def _start_audio(self):
        if audio_manager and self._audio_ready and not self._audio_started:
            try:
                # Garantir que qualquer música anterior pare
                audio_manager.stop_music()
                # loop=False: tocar uma vez, na duração do vídeo
                audio_manager.play_music(self._audio_key, loop=False)
                self._audio_started = True
                _log("Áudio iniciado.")
            except Exception as e:
                _log(f"play_music falhou: {e}")
                self._audio_started = False

    def _stop_audio(self):
        try:
            if audio_manager and self._audio_started:
                audio_manager.stop_music()
                _log("Áudio parado.")
        except Exception:
            pass
        self._audio_started = False
        # Mantém WAV cacheado para execuções futuras

    # ============== Ciclo ==============
    def update(self, dt):
        if self._skip_requested:
            self._go_to_menu()
            return

        if self.state == "fallback":
            self._update_fallback(dt)
            return

        if self.state == "pre_black":
            self._pre_timer += dt
            if self._pre_timer >= self.pre_black_sec:
                self._pre_timer = self.pre_black_sec
                self.state = "playing"
                self._start_audio()  # inicia áudio exatamente quando inicia o vídeo
            return

        if self.state == "playing":
            self._time_acc += dt
            while self._time_acc >= self.frame_interval:
                self._time_acc -= self.frame_interval
                ok, frame_surf = self._read_frame()
                if not ok:
                    # Fim do vídeo → 1s de preto
                    self._stop_audio()
                    self.state = "post_black"
                    self._post_timer = 0.0
                    return
                self.frame_surface = frame_surf
            return

        if self.state == "post_black":
            self._post_timer += dt
            if self._post_timer >= self.post_black_sec:
                self._go_to_menu()
            return

    def _read_frame(self):
        """Lê 1 frame do OpenCV e retorna (ok, surface)."""
        try:
            ok, frame = self.cap.read()
            if not ok:
                _log("Fim do vídeo (sem frame).")
                return False, None
            # BGR -> RGB
            frame = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
            surf = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), "RGB")
            if (surf.get_width(), surf.get_height()) != self.dst_size:
                surf = pygame.transform.smoothscale(surf, self.dst_size)
            return True, surf.convert()
        except Exception as e:
            _log(f"Erro lendo frame: {e}")
            # Em erro, encerra vídeo e segue post_black
            self._stop_audio()
            self.state = "post_black"
            self._post_timer = 0.0
            return False, None

    def render(self, screen):
        # Preto por padrão (pre_black, post_black e fundo do playing)
        screen.fill((0, 0, 0))
        if self.state == "playing" and self.frame_surface is not None:
            screen.blit(self.frame_surface, self.frame_pos)
        elif self.state == "fallback":
            screen.blit(self.white_surface, (0, 0))
            if self.logo_alpha > 0:
                screen.blit(self.logo, self.logo_rect.topleft)

    def handle_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._skip_requested = True

    # ============== Navegação / Cleanup ==============
    def _go_to_menu(self):
        self._stop_audio()
        try:
            if self.cap:
                self.cap.release()
        except Exception:
            pass
        self.game.change_state(MainMenu(self.game))

    # ============== Fallback (logo + fade) ==============
    def _setup_fallback(self):
        sw, sh = self.size
        self.white_surface = pygame.Surface((sw, sh))
        self.white_surface.fill((255, 255, 255))
        self.white_alpha = 0

        try:
            self.logo = pygame.image.load(resource_path("graphics", "images", "splash_logo.png")).convert_alpha()
        except Exception:
            self.logo = pygame.Surface((int(sw * 0.4), int(sh * 0.2)), pygame.SRCALPHA)
            pygame.draw.rect(self.logo, (30, 30, 30), self.logo.get_rect(), border_radius=16)

        self.logo_alpha = 0
        self.logo.set_alpha(0)
        self.logo_rect = self.logo.get_rect(center=(sw // 2, sh // 2))

        self.timer = 0.0
        self.stage = "fade_in_screen"

    def _update_fallback(self, dt):
        if self.stage == "fade_in_screen":
            self.white_alpha += dt * 200
            if self.white_alpha >= 255:
                self.white_alpha = 255
                self.stage = "fade_in_logo"

        elif self.stage == "fade_in_logo":
            self.logo_alpha += dt * 200
            if self.logo_alpha >= 255:
                self.logo_alpha = 255
                self.stage = "wait"
                self.timer = 0.0

        elif self.stage == "wait":
            self.timer += dt
            if self.timer >= 2.0:
                self.stage = "fade_out"

        elif self.stage == "fade_out":
            self.white_alpha -= dt * 200
            self.logo_alpha -= dt * 200
            if self.white_alpha <= 0 and self.logo_alpha <= 0:
                self.white_alpha = 0
                self.logo_alpha = 0
                self._go_to_menu()

        self.white_surface.set_alpha(int(self.white_alpha))
        self.logo.set_alpha(int(self.logo_alpha))
