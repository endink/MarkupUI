"""Tree-sitter parsing for markup, embedded languages and binding expressions."""

from tree_sitter import Parser, QueryCursor
from markupui_tree_sitter import language, nodes, node_text, field, CppHighlighter, CSharpHighlighter, official_roles, official_query, token_runs


ALIASES = {
    "c++": "cpp", "markupui-cpp": "cpp", "cs": "csharp", "c#": "csharp",
    "markupui-csharp": "csharp", "markupui": "html", "xml": "html",
    "js": "javascript", "yml": "yaml", "plaintext": "text", "": "text",
}
SUPPORTED = {"cpp", "csharp", "html", "css", "javascript", "json", "yaml"}


def paint(roles, start, end, role):
    roles[start:end] = [role] * (end - start)


def lexical_roles(source, kind):
    return official_roles(source, kind)


def binding_roles(source):
    """Parse expression structure with JS grammar and apply Markup UI roles.

    The surrounding HTML parser determines injection boundaries. SDK-specific
    option names, @ references and delimiters are display roles, not a second
    regular-expression lexer or a validator of the binding language.
    """
    roles, tree = lexical_roles(source, "javascript")
    options = {"converter", "parameter", "mode", "update", "modifiers", "button"}
    modes = {"oneWayToSource", "oneWay", "twoWay", "oneTime", "input", "change", "blur", "explicit"}
    for node in nodes(tree.root_node):
        start, end, typ = node.start_byte, node.end_byte, node.type
        if typ == "string" and node_text(node, source).startswith("'"):
            paint(roles, start, end, "s1")
        elif typ in {"identifier", "property_identifier", "shorthand_property_identifier", "shorthand_property_identifier_pattern"}:
            value = node_text(node, source)
            if start and source[start - 1:start] == b"@":
                paint(roles, start - 1, end, "nv")
            else:
                is_option = (node.parent is not None
                             and node.parent.type in {"assignment_expression", "object_assignment_pattern", "assignment_pattern"}
                             and field(node) == "left")
                paint(roles, start, end, "k" if is_option or value in modes or value in options else "py")
        elif not node.children and typ in {"{", "}"}:
            paint(roles, start, end, "si")
    # Colon aliases are specific binding operators, not JS labels.
    for alias in (b":lt:", b":le:", b":gt:", b":ge:", b":and:", b":or:"):
        offset = source.find(alias)
        while offset >= 0:
            if not roles[offset].startswith("s"):
                paint(roles, offset, offset + len(alias), "ow")
            offset = source.find(alias, offset + len(alias))
    return roles


def inject_bindings(source, roles, start, end, interpolation=False):
    """Find balanced SDK delimiters, respecting strings and escaped braces."""
    index = start
    while index < end:
        if source[index:index + 1] != b"{" or (interpolation and source[index:index + 2] != b"{{"):
            index += 1
            continue
        slash = index - 1
        while slash >= start and source[slash:slash + 1] == b"\\":
            slash -= 1
        if (index - slash - 1) % 2:
            index += 2 if interpolation else 1
            continue
        begin, depth, quote = index, 0, None
        while index < end:
            char = source[index]
            if quote:
                if char == 92:
                    index += 2
                    continue
                if char == quote:
                    quote = None
            elif char in (39, 34):
                quote = char
            elif char == 123:
                depth += 1
            elif char == 125:
                depth -= 1
                if depth == 0:
                    index += 1
                    break
            index += 1
        roles[begin:index] = binding_roles(source[begin:index])


class MarkupHTMLHighlighter:
    def get_tokens_unprocessed(self, text):
        source = text.encode("utf-8")
        roles, tree = official_roles(source, "html")
        injection_query = official_query("html", "injections")
        for pattern, captures in QueryCursor(injection_query).matches(tree.root_node):
            embedded = injection_query.pattern_settings(pattern).get("injection.language")
            for node in captures.get("injection.content", []):
                roles[node.start_byte:node.end_byte] = official_roles(source[node.start_byte:node.end_byte], embedded)[0]
        for node in nodes(tree.root_node):
            if node.type == "attribute_name" and node_text(node, source).startswith(("@", "mk:")):
                paint(roles, node.start_byte, node.end_byte, "nd")
        # Inject only in ordinary text or directive values, never comments,
        # script/style bodies or ordinary HTML attributes.
        for node in nodes(tree.root_node):
            if node.type == "text":
                inject_bindings(source, roles, node.start_byte, node.end_byte, True)
            elif node.type == "attribute":
                name = next((c for c in node.children if c.type == "attribute_name"), None)
                if name and node_text(name, source).startswith(("@", "mk:")):
                    for value in nodes(node):
                        if value.type == "attribute_value":
                            inject_bindings(source, roles, value.start_byte, value.end_byte)
        yield from token_runs(text, roles)


def highlight_tokens(text, kind):
    kind = ALIASES.get(kind.lower(), kind.lower())
    if kind == "cpp":
        yield from CppHighlighter().get_tokens_unprocessed(text)
    elif kind == "csharp":
        yield from CSharpHighlighter().get_tokens_unprocessed(text)
    elif kind == "html":
        yield from MarkupHTMLHighlighter().get_tokens_unprocessed(text)
    elif kind in SUPPORTED:
        yield from token_runs(text, lexical_roles(text.encode("utf-8"), kind)[0])
    elif text:
        # Unsupported and explicitly plain languages stay escaped plain text.
        yield 0, "", text
