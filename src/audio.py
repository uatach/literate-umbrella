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


def parse_note(value: str) -> float:
    if match := fullmatch(r"([A-G]#?)(-?\d+)?", value):
        note = match.group(1)
        octave = int(match.group(2) or 0)
        semitones = "C C# D D# E F F# G G# A A# B".split()
        index = octave * 12 + semitones.index(note) - 57
        return change_pitch(440, index)
    else:
        raise ValueError


def parse_notes(*notes: list[str]) -> list[float]:
    if len(notes) == 1:
        return parse_note(notes[0])
    return list(map(parse_note, reversed(notes)))


def build_chord(
    frequencies: list[float],
    duration: float,
    damping: float,
    reverse: bool,
    offset: float,
    delay: float,
    rate: int,
):
    if reverse:
        frequencies = list(reversed(frequencies))

    idx = list(sorted(frequencies)).index
    step = duration * 0.1

    buffer = utils.overlay(
        [
            utils.delay(
                utils.synthesize(x, duration - step * idx(x), rate, damping),
                duration=delay * i,
                rate=rate,
            )
            for i, x in enumerate(frequencies)
        ]
    )

    return utils.delay(utils.normalize(buffer), offset, rate)


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


def play_buffers(
    handler: AudioHandler,
    buffers: list[np.ndarray],
    volume: float,
    rate: int,
    effects: bool = False,
):
    buffer = utils.overlay(buffers)

    if effects:
        buffer = utils.effects(buffer, rate)

    _play(
        handler,
        buffer,
        volume,
        rate,
    )


def play_frequency(
    handler: AudioHandler,
    frequency: float,
    duration: float,
    damping: float,
    volume: float,
    rate: int,
):
    buffer = utils.synthesize(frequency, duration, rate, damping)

    play_buffers(
        handler,
        [buffer],
        volume,
        rate,
    )


def play_overlay(
    handler: AudioHandler,
    frequencies: list[float],
    duration: float,
    damping: float,
    reverse: bool,
    offset: float,
    volume: float,
    delay: float,
    rate: int,
):
    buffer = build_chord(
        frequencies,
        duration,
        damping,
        reverse,
        offset,
        delay,
        rate,
    )

    play_buffers(
        handler,
        [buffer],
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

    instrument = song.tracks["instrument"]
    damping = instrument.damping
    duration = instrument.vibration

    tuning = parse_notes(*instrument.tuning)

    tabs = instrument.tabs

    bpm = tabs.bpm
    signature = tabs.signature

    beat = 60 / bpm
    measure = beat * int(signature.split("/")[0])

    init = 0
    buffers = []

    for stroke in tabs.bars:
        for note in stroke.notes:

            frets = note.frets
            delay = note.arpeggio
            reverse = note.stroke == "up"
            offset = eval(note.offset) * measure

            position = init + offset

            frequencies = [
                change_pitch(x, y) for x, y in zip(tuning, frets) if y is not None
            ]

            buffers.append(
                build_chord(
                    frequencies,
                    duration,
                    damping,
                    reverse,
                    position,
                    delay,
                    rate,
                )
            )

        init += measure

    play_buffers(handler, buffers, volume, rate)
