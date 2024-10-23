import numpy as np
import pyaudio as pa

from re import fullmatch
from itertools import cycle


rate = 88200
volume = 0.5

rng = np.random.default_rng()


def samples(duration: float, rate: int) -> int:
    return round(duration * rate)


def change_pitch(freq: float, semitones: int) -> float:
    return freq * 2 ** (semitones / 12)


def parse_pitch(notation):
    if match := fullmatch(r"([A-G]#?)(-?\d+)?", notation):
        note = match.group(1)
        octave = int(match.group(2) or 0)
        semitones = "C C# D D# E F F# G G# A A# B".split()
        index = octave * 12 + semitones.index(note) - 57
        return 440.0 * 2 ** (index / 12)
    else:
        raise ValueError


def centralize(buffer: np.ndarray) -> np.ndarray:
    return buffer - buffer.mean()


def normalize(buffer: np.ndarray) -> np.ndarray:
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
    size = round(rate / freq)  # unit here is samples per cycle
    buffer = rng.uniform(-1, 1, size)

    return normalize(
        centralize(
            np.fromiter(
                vibrate(buffer, damping),
                np.float64,
                samples(duration, rate),
            )
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


def play(audio: pa.PyAudio, buffer: np.ndarray, volume: float, rate: int):
    data = (volume * buffer.astype(np.float32)).tobytes()

    stream = audio.open(
        rate=rate,
        channels=1,
        format=pa.paFloat32,
        output=True,
    )

    stream.write(data)
    stream.close()


def play_sequence(audio):
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
        play(audio, buffer, volume, rate)


def play_chord(audio):
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

    play(audio, buffer, volume, rate)


def play_chord_reversed(audio):
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

    play(audio, buffer, volume, rate)


def play_pitches(audio):
    duration = 0.5
    damping = 0.495

    for x in sorted([-12, 12, 24] + list(range(12))):
        freq = change_pitch(110, x)
        buffer = synthesize(duration, freq, rate, damping=damping)
        play(audio, buffer, volume, rate)


def play_note(audio, note, duration, rate, damping, volume):
    freq = parse_pitch(note)
    buffer = synthesize(duration, freq, rate, damping)
    play(audio, buffer, volume, rate)


def play_notations(audio):
    duration = 1.1
    damping = 0.495

    for note in "C", "C0", "A#", "C#4", "A4":
        play_note(audio, note, duration, rate, damping, volume)

    for note in "E4", "B3", "G3", "D3", "A2", "E2":
        play_note(audio, note, duration, rate, damping, volume)


def main():
    audio = pa.PyAudio()

    play_sequence(audio)
    play_chord(audio)
    play_chord_reversed(audio)
    play_pitches(audio)
    play_notations(audio)

    audio.terminate()


main()

