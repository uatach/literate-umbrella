import numpy as np

from typing import Generator
from functools import cache
from itertools import cycle


rng = np.random.default_rng()


def _get_buffer_size(frequency: float, rate: int) -> int:
    return round(rate / frequency)


def _get_sampling_size(duration: float, rate: int) -> int:
    return round(duration * rate)


def _vibrate(buffer: np.ndarray, damping: float) -> Generator[float, None, None]:
    buffer = buffer.copy()
    size = len(buffer)

    for i in cycle(range(size)):
        yield (c := buffer[i])
        n = buffer[(i + 1) % size]
        buffer[i] = (c + n) * damping


def centralize(buffer: np.ndarray) -> np.ndarray:
    return buffer - buffer.mean()


def normalize(buffer: np.ndarray) -> np.ndarray:
    return buffer / max(np.abs(buffer))


@cache
def synthesize(
    frequency: float,
    duration: float,
    rate: int,
    damping: float,
) -> np.ndarray:

    buffer = rng.uniform(-1, 1, _get_buffer_size(frequency, rate))

    samples = np.fromiter(
        _vibrate(buffer, damping),
        np.float64,
        _get_sampling_size(duration, rate),
    )

    return normalize(centralize(samples))


def delay(buffer: np.ndarray, duration: float, rate: int) -> np.ndarray:
    zeros = np.zeros(_get_sampling_size(duration, rate))
    return np.concatenate((zeros, buffer))


def overlay(sounds: list[np.ndarray]) -> np.ndarray:
    size = max(len(x) for x in sounds)
    buffer = np.zeros(size)
    for x in sounds:
        buffer[: len(x)] += x
    return normalize(buffer)
