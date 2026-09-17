"""Display adapter. The ONLY place tradition vocabulary meets the measurements.

`stack/` never imports this and never contains these strings. The mapping is
recorded once in `stack/governance/declarations.md`, and a grep in
`stack/organization/test_organization.py` asserts the vocabulary's absence from
`stack/`.

Nothing here computes anything. It renames a label that has already been
measured, for a reader who expects the older word.
"""

from __future__ import annotations

#: engineering label -> display word. One direction only: a caller cannot feed
#: a tradition word back into a measurement, because nothing here parses.
DISPLAY = {
    "aligned": "Yusr",
    "misaligned": "Usr",
    "high_dissonance": "Chaos",
}

#: the older parameter names, recorded so the relocation loses nothing.
PARAMETER_HERITAGE = {
    "utility": "U",
    "d_enc": "salat",
    "d_dec": "zakat",
    "noise": "hbar",
    "dissonance": "shirk",
}

CANNOT = ("This renames a label that was already measured. It computes nothing, "
          "parses nothing, and cannot turn a display word back into a number.")


def display_label(engineering_label: str) -> str:
    if engineering_label not in DISPLAY:
        raise KeyError(
            f"{engineering_label!r} is not a measured label; this adapter "
            f"renames only {sorted(DISPLAY)}")
    return DISPLAY[engineering_label]
