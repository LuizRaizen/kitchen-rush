# effects/animations.py
import math
from typing import Callable, Optional, List

# -----------------------------
# EASINGS
# -----------------------------
def lerp(a, b, t): return a + (b - a) * t

def ease_out_cubic(t: float) -> float:
    t -= 1.0
    return t*t*t + 1.0

def ease_in_cubic(t: float) -> float:
    return t*t*t

def ease_out_sine(t: float) -> float:
    # saída suave
    return math.sin((t * math.pi) * 0.5)

def ease_out_back(t: float, s: float = 1.70158) -> float:
    # típico overshoot (impacto)
    t -= 1.0
    return (t * t * ((s + 1) * t + s)) + 1.0

def ease_in_back(t: float, s: float = 1.70158) -> float:
    return t * t * ((s + 1) * t - s)


# -----------------------------
# TWEEN
# -----------------------------
class Tween:
    """
    Tween simples: 0..1 ao longo de 'duration', aplicando easing.
    on_update(t_norm) é chamado a cada frame; você mapeia as props lá.
    """
    def __init__(
        self,
        duration: float,
        easing: Callable[[float], float] = ease_out_sine,
        on_update: Optional[Callable[[float], None]] = None,
        on_complete: Optional[Callable[[], None]] = None
    ):
        self.duration = max(1e-6, float(duration))
        self.easing = easing
        self.on_update = on_update
        self.on_complete = on_complete
        self.elapsed = 0.0
        self.done = False

    def reset(self):
        self.elapsed = 0.0
        self.done = False

    def update(self, dt: float):
        if self.done:
            return
        self.elapsed += max(0.0, float(dt))
        raw_t = min(1.0, self.elapsed / self.duration)
        t = self.easing(raw_t)
        if self.on_update:
            self.on_update(t)
        if raw_t >= 1.0:
            self.done = True
            if self.on_complete:
                self.on_complete()


class Sequence:
    """
    Executa uma lista de tweens em sequência.
    """
    def __init__(self, tweens: List[Tween], loop: bool = False):
        self.tweens = list(tweens)
        self.loop = loop
        self.idx = 0
        if self.tweens:
            self.tweens[0].reset()
        self.done = False

    def update(self, dt: float):
        if self.done or not self.tweens:
            return
        cur = self.tweens[self.idx]
        cur.update(dt)
        if cur.done:
            self.idx += 1
            if self.idx >= len(self.tweens):
                if self.loop:
                    self.idx = 0
                    for tw in self.tweens:
                        tw.reset()
                else:
                    self.done = True
            else:
                self.tweens[self.idx].reset()

    def is_done(self) -> bool:
        return self.done

    def restart(self):
        self.idx = 0
        self.done = False
        for tw in self.tweens:
            tw.reset()


# -----------------------------
# OBJETO ANIMÁVEL
# -----------------------------
class AnimatedObject:
    """
    Classe base: gerencia timelines nomeadas (por ex. 'appear', 'disappear', 'stand').
    """
    def __init__(self):
        self._timelines = {}   # name -> Sequence
        self._current: Optional[str] = None

    def add_timeline(self, name: str, seq: Sequence):
        self._timelines[name] = seq

    def play(self, name: str, restart: bool = True):
        if name in self._timelines:
            self._current = name
            if restart:
                self._timelines[name].restart()

    def stop(self):
        self._current = None

    def is_playing(self, name: Optional[str] = None) -> bool:
        if self._current is None:
            return False
        return name is None or self._current == name

    def update_animations(self, dt: float):
        if self._current is None: 
            return
        seq = self._timelines.get(self._current)
        if seq:
            seq.update(dt)
            if seq.is_done():
                # mantém último estado; para automaticamente
                self._current = None
