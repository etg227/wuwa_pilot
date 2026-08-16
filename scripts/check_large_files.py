"""Fail when a large tracked file is not covered by Git LFS attributes."""

import subprocess
import sys
from pathlib import Path


MAX_BYTES = 25 * 1024 * 1024


def git(*args: str) -> str:
    return subprocess.check_output(("git", *args), text=True, encoding="utf-8").strip()


def main() -> int:
    failures = []
    for relative_path in git("ls-files").splitlines():
        path = Path(relative_path)
        if not path.is_file() or path.stat().st_size <= MAX_BYTES:
            continue
        attribute = git("check-attr", "filter", "--", relative_path)
        if not attribute.endswith(": lfs"):
            failures.append(f"{relative_path} ({path.stat().st_size / 1024 / 1024:.1f} MiB)")
    if failures:
        print("以下大文件未使用 Git LFS：", file=sys.stderr)
        print("\n".join(f"- {item}" for item in failures), file=sys.stderr)
        return 1
    print("大文件 Git LFS 检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
