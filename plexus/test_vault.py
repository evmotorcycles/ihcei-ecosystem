#!/usr/bin/env python3
"""The vault: on-device, offline, and honest about what cannot be recovered.

    python3 -m pytest -q plexus/test_vault.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)


@pytest.fixture(scope="module")
def v():
    try:
        out = subprocess.run(["node", os.path.join(HERE, "vault_dump.mjs")],
                             capture_output=True, text=True, timeout=300)
    except FileNotFoundError:
        pytest.skip("node is not available")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_a_forgotten_password_is_survivable(v):
    """The question this design exists to answer.

    Deriving the key from the password makes forgetting it fatal. Here the data
    is under a random DEK and the DEK is wrapped once per way in, so the
    recovery code opens the SAME data -- not a copy, not a reset.
    """
    assert v["openedWith"] == "password"
    assert v["recoveredWith"] == "recovery"
    assert v["recoveredValue"] == {"amount": 42150, "meter": "A-77"}


def test_a_handwritten_code_survives_being_typed_back_badly(v):
    """A recovery code is written on paper by a person under stress. Case,
    spacing and the 1/I and 0/O confusions must not lock them out."""
    assert v["sloppyCodeWorks"] is True


def test_changing_the_password_does_not_touch_the_data(v):
    """The reason the password is not the key. A rewrap moves 32 bytes; the
    naive design would re-encrypt every record and risk all of them."""
    assert v["recordsUntouchedByPasswordChange"] is True
    assert v["oldPasswordNowFails"] == "rejected"
    assert v["newPasswordValue"] == {"amount": 42150, "meter": "A-77"}
    assert v["recoveryStillWorksAfterChange"] == "recovery"


def test_the_stored_blob_does_not_contain_the_plaintext(v):
    """Encryption at rest, checked by looking rather than by assuming."""
    assert v["ciphertextLooksNothingLikeInput"] is True


def test_a_wrong_secret_opens_nothing(v):
    assert v["wrongPassword"] == "that does not open it"


def test_the_work_factor_is_not_quietly_weakened(v):
    """PBKDF2 iterations are the only thing between a stolen blob and an
    offline guessing run, and they are the first thing someone lowers when
    setup feels slow."""
    assert v["iterations"] >= 600000
    assert v["codeEntropyBits"] >= 128


def test_the_vault_measures_its_own_blast_radius(v):
    """A claim I got wrong and the measurement corrected.

    I wrote that two wrappings would read 0.500 each. They read 0.250:
    contracting both secrets into one ground puts two unit conductances in
    parallel, R falls 2 -> 1.5, support rises 0.5 -> 0.667, and
    1 - 0.5/0.667 = 0.25. What matters is the comparison, and it is the same
    FATHOM arithmetic the rest of the app uses rather than a security score.
    """
    one, two = v["oneWay"], v["twoWays"]
    assert one["restsOnOneThread"] is True
    assert abs(one["deepest"] - 1.0) < 1e-9
    assert two["restsOnOneThread"] is False
    assert abs(two["deepest"] - 0.25) < 1e-9
    assert two["deepest"] < one["deepest"]


def test_the_vault_is_kernel_and_reaches_nothing():
    """It holds the secrets, so it is the last file that should ever be allowed
    to dial out or touch a page."""
    src = open(os.path.join(HERE, "vault.js"), encoding="utf-8").read()
    for banned in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon",
                   "document.", "innerHTML", "localStorage"):
        assert banned not in src, f"vault.js reaches beyond itself: {banned}"


def test_the_file_says_plainly_that_losing_both_is_final():
    """No escrow, no vendor key, no third wrapping. Someone must be able to
    read that before they rely on it."""
    import re
    src = open(os.path.join(HERE, "vault.js"), encoding="utf-8").read()
    # strip the comment furniture so a wrapped sentence still reads as one
    flat = " ".join(re.sub(r"^\s*\*", "", src, flags=re.M).split())
    assert "Lose both, the data is gone, permanently, and nobody can help" in flat
    assert "there is no third wrapping, no escrow, and no vendor key" in flat
    assert ("A vault someone else can open when you forget is a vault they "
            "can open when you have not forgotten.") in flat
