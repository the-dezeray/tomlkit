"""Repository-level pytest configuration.

pytest-bdd 9 requires Python >= 3.10 (see pyproject.toml).  The Python 3.9
compatibility job only runs ``tests/``, but a developer on 3.9 who runs plain
``pytest`` should not get a collection error from the BDD folder.
"""

from __future__ import annotations

import sys


if sys.version_info < (3, 10):
    collect_ignore = ["tests_bdd"]
