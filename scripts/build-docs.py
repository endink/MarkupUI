"""Build both language editions from the shared Zensical configuration."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent


def quote(value):
    return json.dumps(value, ensure_ascii=False)


def set_value(source, key, value):
    source, count = re.subn(
        rf"(?m)^{re.escape(key)}\s*=.*$", lambda _: f"{key} = {quote(value)}", source
    )
    if count != 1:
        raise ValueError(f"Expected one setting for {key}")
    return source


def english_nav(items, labels, pending_pages):
    entries = []
    for item in items:
        for title, value in item.items():
            if isinstance(value, list):
                body = english_nav(value, labels, pending_pages)
                if body == "[]":
                    continue
            elif Path(value) in pending_pages:
                continue
            else:
                body = quote(value)
            entries.append(f"{{ {quote(labels[title])} = {body} }}")
    return "[" + ", ".join(entries) + "]"


def build(source, root):
    tomllib.loads(source)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".toml",
        prefix=".zensical-ci-", dir=root, delete=False,
    ) as handle:
        config = Path(handle.name)
    try:
        config.write_text(source, encoding="utf-8")
        return subprocess.call(
            [sys.executable, "-m", "zensical", "build", "--clean", "--strict", "-f", str(config)],
            cwd=root,
        )
    finally:
        config.unlink(missing_ok=True)


def main():
    source = (ROOT / "zensical.toml").read_text(encoding="utf-8")
    project = tomllib.loads(source)["project"]
    localized = tomllib.loads((ROOT / "zensical.en.toml").read_text(encoding="utf-8"))
    labels = localized["navigation"]
    url = os.environ.get("DOCS_SITE_URL", "").strip() or project["site_url"]
    parsed = urlsplit(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError("DOCS_SITE_URL must be an absolute HTTP(S) URL without a query or fragment")
    url = url.rstrip("/") + "/"
    en_url = url + "en/"

    zh_docs = ROOT / project["docs_dir"]
    en_docs = ROOT / localized["docs_dir"]
    zh_pages = {p.relative_to(zh_docs) for p in zh_docs.rglob("*.md")}
    en_pages = {p.relative_to(en_docs) for p in en_docs.rglob("*.md")}
    pending_pages = {Path(page) for page in localized.get("pending_pages", [])}
    expected_en_pages = zh_pages - pending_pages
    if pending_pages - zh_pages:
        raise ValueError("Every pending English page must have a Chinese source page")
    if expected_en_pages != en_pages:
        missing = ", ".join(p.as_posix() for p in sorted(expected_en_pages - en_pages))
        extra = ", ".join(p.as_posix() for p in sorted(en_pages - expected_en_pages))
        raise ValueError(f"English page set differs from Chinese. Missing: {missing}. Extra: {extra}.")

    alternate = (
        "\n[project.extra]\n"
        f'alternate = [{{ name = "简体中文", link = {quote(url)}, lang = "zh" }}, '
        f'{{ name = "English", link = {quote(en_url)}, lang = "en" }}]\n'
    )
    zh_source = set_value(source, "site_url", url) + alternate
    en_source = set_value(source, "site_url", en_url) + alternate
    for key in ("site_name", "site_description", "language"):
        en_source = set_value(en_source, key, localized[key])
    en_source = en_source.replace("切换到浅色模式", "Switch to light mode")
    en_source = en_source.replace("切换到深色模式", "Switch to dark mode")
    en_source = re.sub(r"(?ms)^nav = \[.*?^\]", lambda _: "nav = " + english_nav(project["nav"], labels, pending_pages), en_source)
    for title in project["extra"]["navigation_icons"]:
        en_source = en_source.replace(f"{quote(title)} = ", f"{quote(labels[title])} = ")

    # Each build needs its own project root because Zensical clears the
    # previous build's cached output when configuration changes.
    with tempfile.TemporaryDirectory(prefix=".zensical-build-", dir=ROOT) as directory:
        en_root = Path(directory)
        staged = en_root / project["docs_dir"]
        shutil.copytree(zh_docs, staged, ignore=shutil.ignore_patterns("*.md"))
        shutil.copytree(en_docs, staged, dirs_exist_ok=True)
        overrides = project["theme"]["custom_dir"]
        shutil.copytree(ROOT / overrides, en_root / overrides)

        status = build(zh_source, ROOT) or build(en_source, en_root)
        if status:
            return status

        en_output = (en_root / project["site_dir"]).resolve()
        site = (ROOT / project["site_dir"]).resolve()
        target = site / "en"
        if not en_output.is_relative_to(en_root) or not site.is_relative_to(ROOT) or site == ROOT:
            raise ValueError("Build outputs must stay inside their project directories")
        if target.resolve() != target:
            raise ValueError("The English output path must not be a symbolic link or junction")
        if target.exists():
            shutil.rmtree(target)
        en_output.rename(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
