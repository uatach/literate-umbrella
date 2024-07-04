import numpy as np
import pyaudio as pa

from itertools import cycle


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
    damping: float = 0.5,
) -> np.ndarray:
    size = round(rate / freq)
    buffer = rng.uniform(-1, 1, size)

    return normalize(
        np.fromiter(
            vibrate(buffer, damping),
            np.float64,
            samples(duration, rate),
        )
    )


def play(buffer: np.ndarray, volume: float, rate: int):
    data = (volume * buffer.astype(np.float32)).tobytes()

    audio = pa.PyAudio()
    stream = audio.open(
        rate=rate,
        channels=1,
        format=pa.paFloat32,
        output=True,
    )

    stream.write(data)
    stream.close()
    audio.terminate()


volume = 0.5
rate = 44100

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
