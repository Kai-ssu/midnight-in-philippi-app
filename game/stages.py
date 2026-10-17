"""
Stage definitions and answer codes, taken from the Printable Kit's
Quick Leader Answer Key. Answers stay on the server and are never sent
to the browser.
"""

import re
from dataclasses import dataclass

GAME_MINUTES = 40


def normalize(code: str) -> str:
    """Ignore case, spaces and dashes so "2-8-4", "2 8 4" and "284" all match."""
    return re.sub(r"[^A-Z0-9]", "", code.upper())


@dataclass(frozen=True)
class Entrance:
    """The animation played once when a team first arrives on a page."""

    scene: str  # dark | songs | quake | torch | doors (see entrance.html)
    caption: str
    padlock: bool = True  # open a padlock first, since a code was just entered


@dataclass(frozen=True)
class Stage:
    number: int
    title: str
    reference: str
    code_prompt: str
    answers: tuple[str, ...]
    entrance: Entrance
    numeric: bool = True

    @property
    def template(self) -> str:
        return f"game/stages/stage_{self.number}.html"

    def accepts(self, code: str) -> bool:
        return normalize(code) in self.answers


STAGES = {
    stage.number: stage
    for stage in [
        Stage(
            1,
            "The Accusation",
            "Acts 16:16–24",
            "Enter the 3-digit code",
            ("284",),
            Entrance("dark", "Philippi, AD 50. The cell door slams shut.", padlock=False),
        ),
        Stage(
            2,
            "Songs in the Stocks",
            "Acts 16:25–26",
            "Enter the 4-letter code",
            ("JPMH", "SONG"),  # SONG is the kit's alternative word-lock answer
            Entrance("songs", "Midnight. In the darkness, a song begins…"),
            numeric=False,
        ),
        Stage(
            3,
            "The Earthquake & the Blade",
            "Acts 16:26–28",
            "Enter the 5-digit code",
            ("16425",),
            Entrance("quake", "Suddenly, a violent earthquake!"),
        ),
        Stage(
            4,
            "What Must I Do?",
            "Acts 16:29–34",
            "Enter the 4-digit code",
            ("7302",),
            Entrance("torch", "The jailer calls for lights…"),
        ),
    ]
}

FINAL_STAGE = max(STAGES)

FREEDOM_ENTRANCE = Entrance("doors", "Every door flies open.")
