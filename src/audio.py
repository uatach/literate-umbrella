import os
import sys

import numpy as np
import pyaudio as pa

from re import fullmatch
from pathlib import Path

import utils

from models import load


def change_pitch(pitch: float, semitones: int) -> float:
    return pitch * 2 ** (semitones / 12)


def parse_pitch(notation: str) -> float:
    if match := fullmatch(r"([A-G]#?)(-?\d+)?", notation):
        note = match.group(1)
        octave = int(match.group(2) or 0)
        semitones = "C C# D D# E F F# G G# A A# B".split()
        index = octave * 12 + semitones.index(note) - 57
        return change_pitch(440, index)
    else:
        raise ValueError


class AudioHandler:
    def __enter__(self):
        # supress warnings based on: https://stackoverflow.com/a/70467199
        devnull = os.open(os.devnull, os.O_WRONLY)
        stderr = os.dup(2)
        sys.stderr.flush()
        os.dup2(devnull, 2)
        os.close(devnull)
        self.handler = pa.PyAudio()
        os.dup2(stderr, 2)
        os.close(stderr)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.handler.terminate()

    def open(self, **kwargs):
        return self.handler.open(**kwargs)


def _play(
    handler: AudioHandler,
    buffer: np.ndarray,
    volume: float,
    rate: int,
):
    data = (volume * buffer.astype(np.float32)).tobytes()

    stream = handler.open(
        rate=rate,
        channels=1,
        format=pa.paFloat32,
        output=True,
    )

    stream.write(data)
    stream.close()


def play_frequency(
    handler: AudioHandler,
    frequency: float,
    duration: float,
    damping: float,
    volume: float,
    rate: int,
):
    buffer = utils.synthesize(frequency, duration, rate, damping)

    _play(
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

    _play(
        handler,
        utils.normalize(buffer),
        volume,
        rate,
    )


def play_song(
    handler: AudioHandler,
    volume: float,
    rate: int,
    path: Path,
):
    song = load(path)
    print(song)

    instrument = song.tracks["instrument"]
    damping = instrument.damping
    duration = instrument.vibration

    tuning = list(map(parse_pitch, reversed(instrument.tuning)))
    print(tuning)

    for stroke in instrument.tabs.bars:
        for note in stroke.notes:
            print(note)

            frets = note.frets
            speed = note.arpeggio
            reverse = note.stroke == "up"

            freqs = [change_pitch(x, y) for x, y in zip(tuning, frets) if y is not None]
            print(freqs)

            if reverse:
                freqs = list(reversed(freqs))

            play_overlay(
                handler,
                freqs,
                duration,
                damping,
                volume,
                speed,
                rate,
            )
