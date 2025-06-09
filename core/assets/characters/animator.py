import math


def oscillate_angle(base_angle, speed, amplitude, time):
    """
    Gera um valor oscilante baseado em seno para animações.
    """
    return base_angle + math.sin(time * speed) * amplitude
