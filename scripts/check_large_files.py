"""Fail when a large tracked file is not covered by Git LFS attributes."""

import subprocess
import sys
from pathlib import Path


MAX_BYTES = 25 * 1024 * 1024
LEGACY_GIT_BLOBS = {"assets/echo_model/echo.onnx"}


def git(*args: str) -> str:
    return subprocess.check_output(
        ("git", "-c", "core.quotepath=false", *args), text=True, encoding="utf-8"
    ).strip()


def index_blob_size(relative_path: str) -> int:
    entry = git("ls-files", "--stage", "--", relative_path)
    if not entry:
        return 0
    blob_sha = entry.split(maxsplit=2)[1]
    return int(git("cat-file", "-s", blob_sha))


def main() -> int:
    failures = []
    legacy = []
    for relative_path in git("ls-files").splitlines():
        path = Path(relative_path)
        if not path.is_file() or path.stat().st_size <= MAX_BYTES:
            continue
        attribute = git("check-attr", "filter", "--", relative_path)
        if not attribute.endswith(": lfs"):
            failures.append(f"{relative_path} ({path.stat().st_size / 1024 / 1024:.1f} MiB)")
            continue
        if index_blob_size(relative_path) > MAX_BYTES:
            if relative_path in LEGACY_GIT_BLOBS:
                legacy.append(relative_path)
            else:
                failures.append(f"{relative_path}（属性为 LFS，但索引中仍是普通 Git blob）")
    if legacy:
        print("以下存量模型尚未迁移到 Git LFS：")
        print("\n".join(f"- {item}" for item in legacy))
    if failures:
        print("以下大文件未使用 Git LFS：", file=sys.stderr)
        print("\n".join(f"- {item}" for item in failures), file=sys.stderr)
        return 1
    print("大文件 Git LFS 属性与索引检查通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
