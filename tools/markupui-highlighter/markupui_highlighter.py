"""Markdown renderer using Tree-sitter for all supported code languages."""

from html import escape, unescape
from xml.etree import ElementTree as etree

from markdown.treeprocessors import Treeprocessor
from pymdownx.highlight import HighlightExtension

from markupui_languages import highlight_tokens, ALIASES


class TreeSitterRenderer:
    """Implement PyMdown's highlighter protocol without Pygments calls."""

    def __init__(self, md=None, **options):
        self.md = md
        self.options = options

    def highlight(self, src, language, css_class="highlight", hl_lines=None,
                  linestart=-1, linestep=-1, linespecial=-1, inline=False,
                  classes=None, id_value="", attrs=None, title=None,
                  code_block_count=0):
        language = language or self.options.get("default_lang", "") or "text"
        language_class = "language-" + language
        classes = [language_class, css_class] + list(classes or [])
        attributes = dict(attrs or {})
        attributes["class"] = " ".join(classes)
        if id_value:
            attributes["id"] = id_value
        lines = [""]
        for _, role, value in highlight_tokens(src, language):
            for index, piece in enumerate(value.split("\n")):
                if index:
                    lines.append("")
                if piece:
                    content = escape(piece, quote=False)
                    lines[-1] += '<span class="' + role + '">' + content + '</span>' if role else content
        if inline:
            element = etree.Element("code", attributes)
            element.text = "\n".join(lines)
            return element
        if lines and not lines[-1] and src.endswith("\n"):
            lines.pop()
        line_start = int(linestart) if linestart is not None and int(linestart) > 0 else 1
        numbered = line_start > 1 or self.options.get("linenums") is True or linestart == 1
        step = int(linestep) if linestep is not None and int(linestep) > 0 else 1
        block = max(0, code_block_count)
        output = []
        for index, content in enumerate(lines):
            number = line_start + index
            if numbered:
                label = str(number) if index % step == 0 else ""
                content = '<span class="lineno" data-linenos="' + label + ' " aria-hidden="true"></span>' + content
            if index + 1 in (hl_lines or []):
                content = '<span class="hll">' + content + '</span>'
            output.append('<span id="__span-' + str(block) + '-' + str(index + 1) + '">' + content + "\n</span>")
        attr_text = " ".join(escape(str(key), quote=True) + '="' + escape(str(value), quote=True) + '"' for key, value in attributes.items())
        heading = '<span class="filename">' + escape(title) + '</span>' if title else ""
        return '<div ' + attr_text + '>' + heading + '<pre><span></span><code>' + ''.join(output) + '</code></pre></div>'


class IndentedCode(Treeprocessor):
    def run(self, root):
        for block in list(root.iter("pre")):
            if len(block) == 1 and block[0].tag == "code":
                self.ext.pygments_code_block += 1
                rendered = TreeSitterRenderer(self.md).highlight(
                    unescape(block[0].text or "").rstrip("\n"), "text",
                    code_block_count=self.ext.pygments_code_block,
                )
                block.clear()
                block.tag = "p"
                block.text = self.md.htmlStash.store(rendered)


class MarkupHighlightExtension(HighlightExtension):
    """Replace the highlighter via PyMdown's provider protocol per instance.

    The inherited option names and counter are protocol compatibility only.
    This extension never invokes Pygments lexers, formatters or highlight().
    """

    def get_pymdownx_highlighter(self):
        return TreeSitterRenderer

    def extendMarkdown(self, md):
        self.md = md
        self.enabled = True
        self.pygments_code_block = -1
        # SuperFences/InlineHilite register a disabled default settings provider.
        # Replace it so both consistently resolve our renderer on every rebuild.
        md.registeredExtensions[:] = [ext for ext in md.registeredExtensions if not isinstance(ext, HighlightExtension)]
        md.registerExtension(self)
        processor = IndentedCode(md)
        processor.ext = self
        md.treeprocessors.register(processor, "indent-highlight", 30)


def makeExtension(**kwargs):
    return MarkupHighlightExtension(**kwargs)
