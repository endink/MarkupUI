"""Rebuild and reload the bilingual documentation preview on local edits."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
from pathlib import Path
import os
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
from time import sleep
from urllib.parse import urlsplit
from uuid import uuid4


ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 15861
REVISION_PATH = "/__docs_preview_revision"
WATCH_DIRS = ("docs", "docs-en", "overrides")
WATCH_FILES = ("zensical.toml", "zensical.en.toml", "scripts/build-docs.py")
RELOAD_SCRIPT = """
<script>
  setInterval(async () => {
    try {
      const response = await fetch('%s', { cache: 'no-store' });
      if (response.ok && (await response.text()) !== '%s') location.reload();
    } catch {}
  }, 1000);
</script>
"""


class PreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.revision, self.snapshot = server.preview
        super().__init__(request, client_address, server, directory=self.snapshot.name)

    def send_head(self):
        url_path = urlsplit(self.path).path
        if url_path == REVISION_PATH:
            return self.send_bytes(self.revision.encode("ascii"), "text/plain")

        path = Path(self.translate_path(self.path))
        if url_path.endswith("/"):
            path = path / "index.html"
        if path.suffix == ".html" and path.is_file():
            page = path.read_bytes()
            if b'<meta name="generator" content="zensical-' in page:
                script = (RELOAD_SCRIPT % (REVISION_PATH, self.revision)).encode("utf-8")
                page = page.replace(b"</body>", script + b"</body>", 1)
                return self.send_bytes(page, "text/html; charset=utf-8")

        return super().send_head()

    def send_bytes(self, body, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        return BytesIO(body)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_request(self, code="-", size="-"):
        if urlsplit(self.path).path != REVISION_PATH:
            super().log_request(code, size)


def source_state():
    paths = [ROOT / name for name in WATCH_FILES]
    for name in WATCH_DIRS:
        paths.extend((ROOT / name).rglob("*"))
    state = {}
    for path in paths:
        try:
            if path.is_file():
                stat = path.stat()
                state[path] = (stat.st_mtime_ns, stat.st_size)
        except FileNotFoundError:
            # Editors can briefly remove the original during an atomic save.
            continue
    return state


def rebuild():
    env = {**os.environ, "DOCS_SITE_URL": f"http://{HOST}:{PORT}/"}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/build-docs.py")], cwd=ROOT, env=env,
    )
    if result.returncode:
        return None
    # Keep the last successful preview available while the next build rewrites site/.
    snapshot = TemporaryDirectory(prefix="markup-ui-docs-", ignore_cleanup_errors=True)
    shutil.copytree(ROOT / "site", snapshot.name, dirs_exist_ok=True)
    return uuid4().hex, snapshot


def main():
    state = source_state()
    with ThreadingHTTPServer((HOST, PORT), PreviewHandler) as server:
        server.preview = rebuild()
        if server.preview is None:
            return 1
        Thread(target=server.serve_forever, daemon=True).start()
        print(f"Chinese: http://{HOST}:{PORT}/", flush=True)
        print(f"English: http://{HOST}:{PORT}/en/", flush=True)
        print("Changes reload automatically. Press Ctrl+C to stop.", flush=True)
        try:
            while True:
                sleep(0.5)
                current = source_state()
                if current == state:
                    continue
                # Wait for related file saves to settle before starting a build.
                sleep(0.5)
                state = source_state()
                print("Documentation changed. Rebuilding both editions...", flush=True)
                updated = rebuild()
                if updated is not None:
                    server.preview = updated
                else:
                    print("Build failed. Showing the last successful preview.", flush=True)
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
