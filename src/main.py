from __future__ import annotations

import sys
from pathlib import Path

from bootstrap.app_bootstrap import run


if __name__ == "__main__":
    if "--smoke-test" in sys.argv:
        # The smoke scenario is test code; production bootstrap stays test-free.
        project_root = Path(__file__).resolve().parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from test.smoke.scenario import run_smoke_test

        raise SystemExit(run_smoke_test(sys.argv))
    raise SystemExit(run(sys.argv))
