import click

from audio import AudioHandler, play_frequency


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


if __name__ == "__main__":
    main()
