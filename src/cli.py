import click

from audio import (
    AudioHandler,
    change_pitch,
    parse_pitch,
    play_frequency,
    play_overlay,
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
        329.63,
        246.94,
        196.00,
        146.83,
        110.00,
        82.41,
    ]

    if kwargs.pop("reverse"):
        frequencies = list(reversed(frequencies))

    play_overlay(
        **ctx.obj,
        **kwargs,
        frequencies=frequencies,
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
            frequency=parse_pitch(x),
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
    ctx.invoke(play_file, path='src/songs/acoustic.yml')


if __name__ == "__main__":
    main()
