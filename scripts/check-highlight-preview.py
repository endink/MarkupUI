"""Verify highlighting survives live incremental updates in an isolated site."""

from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen


def main():
    with tempfile.TemporaryDirectory(prefix="docs-highlight-") as directory:
        root = Path(directory)
        (root / "docs").mkdir()
        with socket.socket() as listener:
            listener.bind(("127.0.0.1", 0))
            port = listener.getsockname()[1]
        config = '''[project]
site_name = "Highlight regression"
[project.theme]
variant = "modern"
[project.markdown_extensions.markupui_highlighter]
[project.markdown_extensions."pymdownx.superfences"]
[project.markdown_extensions."pymdownx.inlinehilite"]
'''
        (root / "zensical.toml").write_text(config, encoding="utf-8")
        page = root / "docs/index.md"

        def write_page(revision):
            page.write_text(f'''# Revision {revision}

```cpp
FMarkupUIElement root = Widget->GetRootElement();
MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, {revision})
```

```csharp
public class PlayerObject : INotifyPropertyChanged {{}}
```

```html
<p @if="{{IsReady}}">Ready</p>
<style>.panel {{ color: red; }}</style>
<script>const ready = true;</script>
```

`#!cpp FMarkupUIElement` and `#!csharp List<int>`

```css
.panel {{ color: red; }}
```

```json
{{"ready": true}}
```

```yaml
ready: true
```
''', encoding="utf-8")

        write_page(0)
        with (root / "preview.log").open("w+", encoding="utf-8") as log:
            process = subprocess.Popen(
                [sys.executable, "-m", "zensical", "serve", "--dev-addr", f"127.0.0.1:{port}"],
                cwd=root, stdout=log, stderr=subprocess.STDOUT,
            )
            try:
                for revision in range(4):
                    if revision:
                        write_page(revision)
                    deadline = time.monotonic() + 25
                    while time.monotonic() < deadline:
                        if process.poll() is not None:
                            log.seek(0)
                            raise RuntimeError(log.read())
                        try:
                            with urlopen(f"http://127.0.0.1:{port}/", timeout=2) as response:
                                rendered = response.read().decode("utf-8")
                            if f"Revision {revision}</h1>" not in rendered:
                                time.sleep(0.15)
                                continue
                            for token in ('class="no"', 'class="nc"', 'class="nd"', 'class="py"', 'class="kc"'):
                                assert token in rendered, f"Revision {revision} lost {token}"
                            assert 'language-text' not in rendered
                            print(f"Revision {revision}: Tree-sitter block, inline and embedded highlighting preserved", flush=True)
                            break
                        except OSError:
                            time.sleep(0.15)
                    else:
                        log.seek(0)
                        raise RuntimeError("Preview did not update:\n" + log.read())
            finally:
                if sys.platform == "win32":
                    # Zensical starts worker processes; close their inherited
                    # log handles before removing the temporary preview site.
                    subprocess.run(
                        ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        check=False,
                    )
                else:
                    process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
