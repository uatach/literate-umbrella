import numpy as np
import pyaudio as pa

from itertools import cycle


audio = pa.PyAudio()
rng = np.random.default_rng()


def samples(duration: float, rate: int) -> int:
    return round(duration * rate)


def normalize(buffer: np.ndarray) -> np.ndarray:
    buffer -= buffer.mean()
    return buffer / max(np.abs(buffer))


def vibrate(buffer: np.ndarray, damping: float) -> list[float]:
    buffer = buffer.copy()
    size = len(buffer)

    for i in cycle(range(size)):
        yield (c := buffer[i])
        n = buffer[(i + 1) % size]
        buffer[i] = (c + n) * damping


def synthesize(
    duration: float,
    freq: float,
    rate: int,
    damping: float,
) -> np.ndarray:
    size = round(rate / freq) # unit here is samples per cycle
    buffer = rng.uniform(-1, 1, size)

    return normalize(
        np.fromiter(
            vibrate(buffer, damping),
            np.float64,
            samples(duration, rate),
        )
    )


def delay(buffer: np.ndarray, duration: float, rate: int) -> np.ndarray:
    zeros = np.zeros(samples(duration, rate))
    return np.concatenate((zeros, buffer))


def overlay(sounds: list[np.ndarray]) -> np.ndarray:
    size = max(len(x) for x in sounds)
    buffer = np.zeros(size)
    for x in sounds:
        buffer[: len(x)] += x
    return normalize(buffer)


def play(buffer: np.ndarray, volume: float, rate: int):
    data = (volume * buffer.astype(np.float32)).tobytes()

    stream = audio.open(
        rate=rate,
        channels=1,
        format=pa.paFloat32,
        output=True,
    )

    stream.write(data)
    stream.close()


def play_sequence():
    duration = 0.5
    damping = 0.495

    frequencies = [
        261.63,
        293.66,
        329.63,
        349.23,
        392.00,
        440.00,
        493.88,
        523.25,
    ]

    for freq in frequencies:
        buffer = synthesize(duration, freq, rate, damping)
        play(buffer, volume, rate)


def play_chord():
    duration = 3.5
    damping = 0.499

    frequencies = [
        329.63,
        246.94,
        196.00,
        146.83,
        110.00,
        82.41,
    ]

    buffer = overlay(
        [
            delay(
                synthesize(duration + 0.25 * i, x, rate, damping),
                duration=i * 0.1,
                rate=rate,
            )
            for i, x in enumerate(frequencies)
        ]
    )

    play(buffer, volume, rate)


def play_chord_reversed():
    duration = 3.5
    damping = 0.499

    frequencies = [
        329.63,
        246.94,
        196.00,
        146.83,
        110.00,
        82.41,
    ]

    buffer = overlay(
        [
            delay(
                synthesize(duration + 0.25 * i, x, rate, damping),
                duration=(len(frequencies) - 1 - i) * 0.1,
                rate=rate,
            )
            for i, x in enumerate(frequencies)
        ]
    )

    play(buffer, volume, rate)


audio.terminate()
