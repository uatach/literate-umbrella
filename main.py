import numpy as np
import pyaudio as pa

from itertools import cycle


volume = .6
duration = .5
rate = 44100
damping = .495

samples = round(duration * rate)

rng = np.random.default_rng()


def normalize(samples):
    aux = samples - samples.mean()
    return aux / max(np.abs(aux))


def vibrate(buffer):
    size = len(buffer)

    for i in cycle(range(size)):
        yield (c := buffer[i])
        n = buffer[(i + 1) % size]
        buffer[i] = (c + n) * damping


def synthesize(freq):
    size = round(rate / freq)
    buffer = rng.uniform(-1, 1, size)
    return normalize(
        np.fromiter(
            vibrate(buffer),
            np.float64,
            samples,
        )
    )


def play(buffer, volume=volume, rate=rate):
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
    buffer = synthesize(freq)
    play(buffer, volume)
