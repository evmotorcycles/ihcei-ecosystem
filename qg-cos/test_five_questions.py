"""pytest: the five RT-can't-answer questions each get a measurable telemetry answer."""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _run():
    return subprocess.run([sys.executable, os.path.join(HERE, "five_questions.py")],
                          capture_output=True, text=True)


def test_all_five_questions_answered():
    r = _run()
    assert r.returncode == 0, r.stdout + r.stderr
    assert "RESULT: 5/5 questions" in r.stdout


def test_each_question_present_and_answered():
    out = _run().stdout
    for q in ("Q1  PURPOSE", "Q2  REALMS", "Q3  STEWARDSHIP", "Q4  REFERENCE-LOCK", "Q5  PREDICTABILITY"):
        assert q in out
    assert out.count("ANSWERED") == 5
