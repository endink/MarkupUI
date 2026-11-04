"""Build Zensical with an optional deployment URL, leaving source config intact."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from urllib.parse import urlsplit


def main():
    root = Path(__file__).resolve().parent.parent
    config = root / "zensical.toml"
    url = os.environ.get("DOCS_SITE_URL", "").strip()
    temporary = None
    try:
        if url:
            parsed = urlsplit(url)
            if parsed.scheme not in ("http", "https") or not parsed.netloc:
                raise ValueError("DOCS_SITE_URL must be an absolute HTTP(S) URL")
            url = url.rstrip("/") + "/"
            source = config.read_text(encoding="utf-8")
            source, count = re.subn(
                r"(?m)^site_url\s*=.*$",
                lambda _: "site_url = " + json.dumps(url),
                source,
            )
            if count != 1:
                raise ValueError("Expected one project site_url setting")
            tomllib.loads(source)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".toml",
                prefix=".zensical-ci-", dir=root, delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(source)
            config = temporary
        return subprocess.call(
            [sys.executable, "-m", "zensical", "build", "--clean", "--strict", "-f", str(config)],
            cwd=root,
        )
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
