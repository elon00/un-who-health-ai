"""Run actual local regressions. No production or 100/100 certification is implied."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_reality():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py", top_level_dir=str(ROOT))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.testsRun > 0 and result.wasSuccessful()


if __name__ == "__main__":
    sys.exit(0 if test_reality() else 1)
