import click

from itertools import cycle

from audio import (
    AudioHandler,
    build_chord,
    change_pitch,
    parse_notes,
    play_frequency,
    play_overlay,
    play_buffers,
    play_song,
)


@click.group
@click.pass_context
@click.option("--rate", default=44100)
@click.option("--volume", default=0.1)
def main(ctx, **kwargs):
    ctx.obj = kwargs
    ctx.obj["handler"] = ctx.with_resource(AudioHandler())


@main.command
@click.pass_context
@click.option("--frequency", default=261.63)
@click.option("--duration", default=0.5)
@click.option("--damping", default=0.495)
def play_tone(ctx, **kwargs):
    play_frequency(
        **ctx.obj,
        **kwargs,
    )


@main.command
@click.pass_context
@click.option("--duration", default=1)
@click.option("--damping", default=0.495)
def play_tones(ctx, **kwargs):
    for x in range(200, 610, 10):
        play_frequency(
            **ctx.obj,
            **kwargs,
            frequency=x,
        )


@main.command
@click.pass_context
@click.option("--duration", default=0.5)
@click.option("--damping", default=0.495)
def play_sequence(ctx, **kwargs):
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
        play_frequency(
            **ctx.obj,
            **kwargs,
            frequency=x,
        )


@main.command
@click.pass_context
@click.option("--duration", default=5)
@click.option("--damping", default=0.499)
@click.option("--delay", default=0.04)
@click.option("--reverse", default=False)
def play_chord(ctx, **kwargs):
    frequencies = [
        82.41,
        110.00,
        146.83,
        196.00,
        246.94,
        329.63,
    ]

    play_overlay(
        **ctx.obj,
        **kwargs,
        frequencies=frequencies,
        offset=0,
    )


@main.command
@click.pass_context
@click.option("--duration", default=0.5)
@click.option("--damping", default=0.495)
def play_pitches(ctx, **kwargs):
    for x in sorted([-12, 24] + list(range(13))):
        play_frequency(
            **ctx.obj,
            **kwargs,
            frequency=change_pitch(110, x),
        )


@main.command
@click.pass_context
@click.option("--duration", default=1)
@click.option("--damping", default=0.495)
def play_notes(ctx, **kwargs):
    notes = [
        "C",
        "C0",
        "A#",
        "C#4",
        "A4",
        "E4",
        "B3",
        "G3",
        "D3",
        "A2",
        "E2",
        "G2",
        "D2",
        "A1",
        "E1",
    ]

    for x in notes:
        play_frequency(
            **ctx.obj,
            **kwargs,
            frequency=parse_notes(x),
        )


@main.command
@click.pass_context
def play_instruments(ctx, **kwargs):
    frequencies = parse_notes("E2", "A2", "D3", "G3", "B3", "E4")

    play_overlay(
        **ctx.obj,
        **kwargs,
        frequencies=frequencies,
        duration=2.5,
        damping=0.498,
        reverse=True,
        delay=0.04,
        offset=0,
    )

    frequencies = parse_notes("G4", "D3", "G3", "B3", "D4")

    play_overlay(
        **ctx.obj,
        **kwargs,
        frequencies=frequencies,
        duration=2.5,
        damping=0.4965,
        reverse=True,
        delay=0.04,
        offset=0,
    )

    frequencies = parse_notes("A4", "E4", "C4", "G4")

    play_overlay(
        **ctx.obj,
        **kwargs,
        frequencies=frequencies,
        duration=2.5,
        damping=0.498,
        reverse=True,
        delay=0.04,
        offset=0,
    )


@main.command
@click.pass_context
@click.option("--effects", default=False)
def play_chorus(ctx, **kwargs):
    frequencies = parse_notes("A4", "E4", "C4", "G4")
    duration = 5
    damping = 0.498

    chords = [
        (0, 0, 0, 3),
        (0, 2, 3, 2),
        (2, 0, 0, 0),
        (2, 0, 1, 0),
    ]

    strokes = [
        (0, 0.25, 0.025),
        (0, 0.65, 0.025),
        (1, 0.45, 0.025),
        (1, 0.75, 0.01),
        (0, 0.2, 0.01),
        (1, 0.4, 0.025),
    ]

    init = 0
    buffers = []

    for chord in chords:
        for _ in range(2):
            for reverse, offset, delay in strokes:
                init += offset

                pitches = [change_pitch(x, y) for x, y in zip(frequencies, chord)]
                buffers.append(
                    build_chord(
                        pitches,
                        duration,
                        damping,
                        reverse,
                        init,
                        delay,
                        ctx.obj["rate"],
                    )
                )

    play_buffers(
        **ctx.obj,
        **kwargs,
        buffers=buffers,
    )


@main.command
@click.pass_context
@click.argument("path", type=click.Path(exists=True))
def play_file(ctx, path):
    play_song(
        **ctx.obj,
        path=path,
    )


@main.command
@click.pass_context
def test_all(ctx):
    ctx.invoke(play_tone, frequency=441)
    ctx.invoke(play_tones)
    ctx.invoke(play_sequence)
    ctx.invoke(play_chord)
    ctx.invoke(play_chord, reverse=True)
    ctx.invoke(play_pitches)
    ctx.invoke(play_notes)
    ctx.invoke(play_instruments)
    ctx.invoke(play_chorus)
    ctx.invoke(play_file, path="src/songs/acoustic.yml")
    ctx.invoke(play_file, path="src/songs/chorus.yml")


if __name__ == "__main__":
    main()
