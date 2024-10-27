from yaml import safe_load
from pathlib import Path
from pydantic import BaseModel


class Measure(BaseModel):
    notes: list[dict]


class Tablature(BaseModel):
    bpm: int
    signature: str
    bars: list[Measure]


class Track(BaseModel):
    tuning: list[str]
    vibration: float
    damping: float
    tabs: Tablature


class Song(BaseModel):
    title: str
    artist: str
    rate: int
    tracks: dict[str, Track]


def load(path: str):
    with Path(path).open() as fp:
        return Song(**safe_load(fp))
