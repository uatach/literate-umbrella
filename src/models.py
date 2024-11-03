from yaml import safe_load
from typing import Optional
from pathlib import Path
from pydantic import BaseModel


class Note(BaseModel):
    frets: list[Optional[int]]
    arpeggio: Optional[float] = 0
    stroke: Optional[str] = "down"
    offset: Optional[str] = "0"


class Measure(BaseModel):
    notes: list[Note]


class Tablature(BaseModel):
    bpm: int
    signature: str
    bars: list[Measure]


class Instrument(BaseModel):
    tuning: list[str]
    vibration: float
    damping: Optional[float] = 0.5
    tabs: Tablature


class Song(BaseModel):
    title: str
    artist: str
    rate: int
    tracks: dict[str, Instrument]


def load(path: str):
    with Path(path).open() as fp:
        return Song(**safe_load(fp))
