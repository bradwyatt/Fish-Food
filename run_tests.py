#!/usr/bin/env python3
"""
run_tests.py  —  Colorized visual runner for Fish-Food's headless test suite.

Usage:
    python run_tests.py          # run all tests
    python run_tests.py -k move  # filter tests by name substring
"""
import sys
import time
import unittest

# ── ANSI colour helpers ───────────────────────────────────────────────────────
_COLOR = sys.stdout.isatty() or "--color" in sys.argv

def _c(code, text):
    return f"\033[{code}m{text}\033[0m" if _COLOR else text

def green(t):  return _c("1;32", t)
def red(t):    return _c("1;31", t)
def yellow(t): return _c("1;33", t)
def cyan(t):   return _c("1;36", t)
def grey(t):   return _c("2",    t)
def bold(t):   return _c("1",    t)

STATUS_FMT = {
    "PASS":  lambda: green(" PASS "),
    "FAIL":  lambda: red(" FAIL "),
    "ERROR": lambda: yellow(" ERR  "),
    "SKIP":  lambda: cyan(" SKIP "),
}


# ── Result collector ──────────────────────────────────────────────────────────
class _Result(unittest.TestResult):
    def __init__(self):
        super().__init__()
        self._records = []   # (test, status, detail, elapsed_ms)
        self._t0 = None

    def startTest(self, test):
        super().startTest(test)
        self._t0 = time.perf_counter()

    def _record(self, test, status, detail=""):
        ms = (time.perf_counter() - self._t0) * 1000
        self._records.append((test, status, detail, ms))

    def addSuccess(self, test):
        self._record(test, "PASS")

    def addFailure(self, test, err):
        self._record(test, "FAIL", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        self._record(test, "ERROR", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        self._record(test, "SKIP", reason)


# ── Filter helper ─────────────────────────────────────────────────────────────
def _filter_suite(suite, keyword):
    """Return a new suite containing only tests whose id matches keyword."""
    filtered = unittest.TestSuite()
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            sub = _filter_suite(item, keyword)
            if sub.countTestCases():
                filtered.addTest(sub)
        elif keyword.lower() in item.id().lower():
            filtered.addTest(item)
    return filtered


# ── Main runner ───────────────────────────────────────────────────────────────
def run(keyword=None):
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_headless.py")

    if keyword:
        suite = _filter_suite(suite, keyword)
        if not suite.countTestCases():
            print(red(f'No tests matched "{keyword}".'))
            return 1

    result = _Result()
    suite.run(result)

    # ── Print results grouped by class ───────────────────────────────────────
    print()
    print(bold("═" * 66))
    print(bold("  Fish-Food  —  Headless Test Results"))
    print(bold("═" * 66))

    last_cls = None
    for test, status, detail, ms in result._records:
        cls_name = type(test).__name__
        if cls_name != last_cls:
            print(f"\n  {bold(cyan(cls_name))}")
            last_cls = cls_name

        badge = STATUS_FMT[status]()
        name = test._testMethodName
        timing = grey(f"({ms:.0f} ms)")
        print(f"  {badge}  {name}  {timing}")

        if detail and status in ("FAIL", "ERROR"):
            # Show the last few lines of the traceback (most useful part)
            lines = [ln for ln in detail.splitlines() if ln.strip()]
            snippet = lines[-3:] if len(lines) > 3 else lines
            for ln in snippet:
                print(grey(f"             {ln}"))

    # ── Summary ──────────────────────────────────────────────────────────────
    total  = result.testsRun
    passed = sum(1 for _, s, _, _ in result._records if s == "PASS")
    failed = sum(1 for _, s, _, _ in result._records if s == "FAIL")
    errors = sum(1 for _, s, _, _ in result._records if s == "ERROR")
    skips  = sum(1 for _, s, _, _ in result._records if s == "SKIP")
    total_ms = sum(ms for _, _, _, ms in result._records)

    print()
    print(bold("─" * 66))
    parts = [green(f"{passed} passed")]
    if failed: parts.append(red(f"{failed} failed"))
    if errors: parts.append(yellow(f"{errors} errors"))
    if skips:  parts.append(cyan(f"{skips} skipped"))
    parts.append(grey(f"{total} total  ·  {total_ms:.0f} ms"))
    print("  " + "  ·  ".join(parts))
    print(bold("─" * 66))
    print()

    return 0 if (failed == 0 and errors == 0) else 1


if __name__ == "__main__":
    # Simple -k filter support: python run_tests.py -k movement
    keyword = None
    args = sys.argv[1:]
    if "-k" in args:
        idx = args.index("-k")
        if idx + 1 < len(args):
            keyword = args[idx + 1]

    sys.exit(run(keyword))
