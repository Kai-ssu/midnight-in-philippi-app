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
    # Answer key for leaders: (part of the code, how players find it).
    key: tuple[tuple[str, str], ...]
    key_note: str = ""
    numeric: bool = True

    @property
    def template(self) -> str:
        return f"game/stages/stage_{self.number}.html"

    def accepts(self, code: str) -> bool:
        return normalize(code) in self.answers

    @property
    def display_code(self) -> str:
        """The main answer as written on a lock, e.g. "2-8-4"."""
        return "-".join(self.answers[0])


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
            key=(
                ("2", "Paul and Silas were seized and dragged into the marketplace (16:19)."),
                ("8", "The spirit left the girl in verse 18."),
                ("4", "Their feet were fastened in the stocks in verse 24."),
            ),
        ),
        Stage(
            2,
            "Songs in the Stocks",
            "Acts 16:25–26",
            "Enter the 4-letter code",
            ("JPMH",),
            Entrance("songs", "Midnight. In the darkness, a song begins…"),
            key=(
                ("J", "Nehemiah 8:10: “the joy of the LORD is your strength.”"),
                ("P", "Psalm 119:164: “Seven times a day I praise you.”"),
                ("M", "Acts 16:25: the time of night was midnight."),
                ("H", "Acts 16:25: they were singing hymns."),
            ),
            key_note="Letters go in Bible order: Nehemiah, Psalms, then Acts (time of night before what they sang).",
            numeric=False,
        ),
        Stage(
            3,
            "The Earthquake & the Blade",
            "Acts 16:26–28",
            "Enter the 5-digit code",
            ("16425",),
            Entrance("quake", "Suddenly, a violent earthquake!"),
            key=(
                ("NIV", "DON'T (I) · HARM (VI) · YOURSELF! (IV) · WE ARE ALL (II) · HERE! (V)"),
                ("NKJV", "DO (I) · YOURSELF (VI) · NO HARM (IV) · FOR WE ARE ALL (II) · HERE (V)"),
            ),
            key_note="Strips in the order of Paul's shout in Acts 16:28. Both Bibles give the same code.",
        ),
        Stage(
            4,
            "What Must I Do?",
            "Acts 16:29–34",
            "Enter the 4-digit code",
            ("7302",),
            Entrance("torch", "The jailer calls for lights…"),
            key=(
                ("7", "BELIEVE has 7 letters (16:31)."),
                ("3", "The jailer washed their wounds (NKJV: stripes) in verse 33."),
                ("0", "No prisoners fled: “We are all here” (16:28)."),
                ("2", "Faith and joy in the jailer's household (16:34)."),
            ),
        ),
    ]
}

FINAL_STAGE = max(STAGES)

FREEDOM_ENTRANCE = Entrance("doors", "Every door flies open.")
