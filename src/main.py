import numpy as np
import pyaudio as pa

from re import fullmatch

import utils

from models import load


volume = 0.1


def play(
    audio: pa.PyAudio,
    buffer: np.ndarray,
    volume: float,
    rate: int,
):
    data = (volume * buffer.astype(np.float32)).tobytes()

    stream = audio.open(
        rate=rate,
        channels=1,
        format=pa.paFloat32,
        output=True,
    )

    stream.write(data)
    stream.close()


def play_frequency(audio, frequency, duration, rate, damping):
    play(
        audio,
        utils.synthesize(frequency, duration, rate, damping),
        volume,
        rate,
    )


def play_tone(audio, rate):
    duration = 0.5
    damping = 0.495
    frequency = 441
    play_frequency(audio, frequency, duration, rate, damping)


def play_tones(audio, rate):
    duration = 1
    damping = 0.495

    frequencies = np.arange(200, 610, 10)

    for x in frequencies:
        play_frequency(audio, x, duration, rate, damping)


def play_sequence(audio, rate):
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

    for x in frequencies:
        play_frequency(audio, x, duration, rate, damping)


def play_chord(audio, rate):
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

    buffer = utils.overlay(
        [
            utils.delay(
                utils.synthesize(x, duration + 0.25 * i, rate, damping),
                duration=0.04 * i,
                rate=rate,
            )
            for i, x in enumerate(frequencies)
        ]
    )

    play(audio, buffer, volume, rate)


def play_chord_reversed(audio, rate):
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

    buffer = utils.overlay(
        [
            utils.delay(
                utils.synthesize(x, duration + 0.25 * i, rate, damping),
                duration=0.04 * (len(frequencies) - 1 - i),
                rate=rate,
            )
            for i, x in enumerate(frequencies)
        ]
    )

    play(audio, buffer, volume, rate)


def change_pitch(freq: float, semitones: int) -> float:
    return freq * 2 ** (semitones / 12)


def parse_pitch(notation) -> float:
    if match := fullmatch(r"([A-G]#?)(-?\d+)?", notation):
        note = match.group(1)
        octave = int(match.group(2) or 0)
        semitones = "C C# D D# E F F# G G# A A# B".split()
        index = octave * 12 + semitones.index(note) - 57
        return 440.0 * 2 ** (index / 12)
    else:
        raise ValueError


def play_pitches(audio, rate):
    duration = 0.5
    damping = 0.495

    for x in sorted([-12, 12, 24] + list(range(12))):
        freq = change_pitch(110, x)
        play_frequency(audio, freq, duration, rate, damping)


def play_note(audio, note, duration, rate, damping, volume):
    freq = parse_pitch(note)
    play_frequency(audio, freq, duration, rate, damping)


def play_notations(audio, rate):
    duration = 1.1
    damping = 0.495

    for note in "C", "C0", "A#", "C#4", "A4":
        play_note(audio, note, duration, rate, damping, volume)

    for note in "E4", "B3", "G3", "D3", "A2", "E2":
        play_note(audio, note, duration, rate, damping, volume)

    for note in "G2", "D2", "A1", "E1":
        play_note(audio, note, duration, rate, damping, volume)


def build_chord(rate, duration, damping, freqs, speed, reverse):
    # TODO: improve duration should be longer for lower frequencies
    sounds = [
        utils.synthesize(x, duration + 0.25 * i, rate, damping)
        for i, x in enumerate(freqs)
    ]

    if reverse:
        sounds = reversed(sounds)

    return utils.normalize(
        utils.overlay([utils.delay(x, i * speed, rate) for i, x in enumerate(sounds)])
    )


def play_acoustic(audio):
    song = load("src/songs/acoustic.yml")
    print(song)

    rate = song.rate
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

            buffer = build_chord(rate, duration, damping, freqs, speed, reverse)
            play(audio, buffer, volume, rate)


def main():
    audio = pa.PyAudio()
    rate = 44100

    play_tone(audio, rate)
    play_tones(audio, rate)
    play_sequence(audio, rate)
    play_chord(audio, rate)
    play_chord_reversed(audio, rate)
    play_pitches(audio, rate)
    play_notations(audio, rate)

    play_acoustic(audio)

    audio.terminate()


main()
