import numpy as np
import pyaudio as pa

from contextlib import contextmanager

import utils


class AudioHandler:
    def __enter__(self):
        self.handler = pa.PyAudio()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.terminate()

    def open(self, **kwargs):
        return self.handler.open(**kwargs)


@contextmanager
def _open_stream(handler: AudioHandler, rate: int):
    stream = handler.open(
        rate=rate,
        channels=1,
        format=pa.paFloat32,
        output=True,
    )

    try:
        yield stream
    finally:
        stream.close()


def play(
    handler: AudioHandler,
    buffer: np.ndarray,
    volume: float,
    rate: int,
):
    with _open_stream(handler, rate) as stream:
        data = (volume * buffer.astype(np.float32)).tobytes()
        stream.write(data)


def play_frequency(
    handler: AudioHandler,
    frequency: float,
    duration: float,
    damping: float,
    volume: float,
    rate: int,
):
    buffer = utils.synthesize(frequency, duration, rate, damping)

    play(
        handler,
        buffer,
        volume,
        rate,
    )


def play_overlay(
    handler: AudioHandler,
    frequencies: list[float],
    duration: float,
    damping: float,
    volume: float,
    speed: float,
    rate: int,
):
    buffer = utils.overlay(
        [
            utils.delay(
                utils.synthesize(x, duration, rate, damping),
                duration=speed * i,
                rate=rate,
            )
            for i, x in enumerate(frequencies)
        ]
    )

    play(
        handler,
        buffer,
        volume,
        rate,
    )
