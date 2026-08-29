from plumb.plumb import (  # noqa: F401
    Abstain, PlumbError, Program, lex, parse, run, vif, main,
)
from plumb.plumb import __doc__ as _plumb_doc

# The package docstring IS plumb.py's, deliberately. test_plumb.py asserts the
# anti-overclaim statement is present on `plumb.__doc__`, and a bare __init__.py
# silently replaced it -- which is how adding this file broke 41 passing tests
# in the same commit that added it. The note below is appended, never
# substituted.
__doc__ = (_plumb_doc or "") + """

PACKAGING NOTE
This file exists so `plumb/` can be imported as a package (`from plumb.spec
import lint`). The suites here also import `from plumb import parse, run`, so
every name plumb.py exports is re-exported above.
"""
