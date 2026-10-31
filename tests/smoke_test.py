"""Local regression smoke entry point; not deployed service availability."""
from reality_check_harness import test_reality

if __name__ == "__main__":
    raise SystemExit(0 if test_reality() else 1)
