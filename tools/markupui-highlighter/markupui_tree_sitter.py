"""Execute unmodified upstream queries; keep only UE/Markup UI extensions."""

from functools import lru_cache
from importlib import import_module
from importlib.resources import files
import re

from tree_sitter import Language, Parser, Query, QueryCursor


@lru_cache(maxsize=8)
def language(kind):
    package = {"csharp": "c_sharp"}.get(kind, kind)
    return Language(import_module("tree_sitter_" + package).language())


@lru_cache(maxsize=16)
def official_query(kind, name="highlights"):
    root = files("markupui_queries")
    text = (root / kind / (name + ".scm")).read_text(encoding="utf-8")
    if kind == "cpp" and name == "highlights":
        text = (root / "c/highlights.scm").read_text(encoding="utf-8") + "\n" + text
    return Query(language(kind), text)


# Capture-to-CSS translation preserves the existing palette. Language syntax
# classification belongs exclusively to upstream queries, not node-name lists.
CAPTURE_STYLES = {
    "attribute": "na", "boolean": "kc", "comment": "cm",
    "constant": "no", "constant.builtin": "kc", "constructor": "nf",
    "delimiter": "p", "escape": "se", "function": "nf",
    "function.builtin": "nf", "keyword": "k", "label": "nl",
    "module": "nn", "namespace": "nn", "number": "m", "operator": "o",
    "property": "py", "punctuation": "p", "string": "s",
    "string.escape": "se", "tag": "nt", "type": "nc", "type.builtin": "kt",
    "variable": "n", "variable.builtin": "nb", "variable.parameter": "n",
}


def capture_style(name):
    if name.startswith("_"):
        return None
    while name:
        if name in CAPTURE_STYLES:
            return CAPTURE_STYLES[name]
        name = name.rpartition(".")[0]
    return None


def local_ranges(source, kind, tree):
    """Honor upstream local.scope/definition/reference query captures."""
    resource = files("markupui_queries") / kind / "locals.scm"
    if not resource.is_file():
        return set()
    captured = QueryCursor(official_query(kind, "locals")).captures(tree.root_node)
    scopes = [tree.root_node] + captured.get("local.scope", [])
    definitions = {scope.id: [] for scope in scopes}
    for definition in captured.get("local.definition", []):
        scope = min((scope for scope in scopes if scope.start_byte <= definition.start_byte and definition.end_byte <= scope.end_byte),
                    key=lambda node: node.end_byte - node.start_byte)
        definitions[scope.id].append((definition.start_byte, node_text(definition, source)))
    result = set()
    for node in captured.get("local.definition", []) + captured.get("local.reference", []):
        name = node_text(node, source)
        if any(scope.start_byte <= node.start_byte and node.end_byte <= scope.end_byte
               and any(start <= node.start_byte and value == name for start, value in definitions[scope.id])
               for scope in scopes):
            result.add((node.start_byte, node.end_byte))
    return result


def official_roles(source, kind, tree=None):
    tree = tree or Parser(language(kind)).parse(source)
    query = official_query(kind)
    locals_ = local_ranges(source, kind, tree) if any(query.pattern_assertions(i) for i in range(query.pattern_count)) else set()
    spans = []
    for pattern, captures in QueryCursor(query).matches(tree.root_node):
        assertions = query.pattern_assertions(pattern)
        if "local" in assertions:
            is_local = any((node.start_byte, node.end_byte) in locals_ for values in captures.values() for node in values)
            if is_local != assertions["local"][1]:
                continue
        for name, captured_nodes in captures.items():
            style = capture_style(name)
            if style is not None:
                spans.extend((node.start_byte, node.end_byte, pattern, style) for node in captured_nodes)
    roles = [""] * len(source)
    # Nested captures override surrounding strings; later upstream patterns win
    # when multiple rules capture exactly the same range.
    for start, end, _, style in sorted(spans, key=lambda item: (-(item[1] - item[0]), item[2])):
        roles[start:end] = [style] * (end - start)
    return roles, tree


def is_extension_macro(name):
    return name in {"TEXT", "UFUNCTION", "UPROPERTY", "UCLASS", "USTRUCT", "UENUM", "UINTERFACE", "UPARAM", "UMETA"} or name.startswith(("MARKUPUI_", "UE_", "GET_MEMBER_NAME_", "GENERATED_"))


def nodes(root):
    stack = [root]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(reversed(node.children))


def node_text(node, source):
    return source[node.start_byte:node.end_byte].decode("utf-8")


def field(node):
    if node.parent:
        for index, child in enumerate(node.parent.children):
            if child.id == node.id:
                return node.parent.field_name_for_child(index)
    return None


def macro_ranges(root, source):
    """Locate complete uppercase macro calls without requiring semicolons."""
    tree_nodes = list(nodes(root))
    protected = {node.start_byte: node.end_byte for node in tree_nodes
                 if "comment" in node.type or node.type in {"string_literal", "raw_string_literal", "char_literal"}}
    candidates = []
    for node in tree_nodes:
        if node.type not in {"identifier", "type_identifier", "field_identifier"}:
            continue
        if not is_extension_macro(node_text(node, source)):
            continue
        ancestor = node.parent
        while ancestor and not ancestor.type.startswith("preproc_"):
            ancestor = ancestor.parent
        if ancestor:
            continue
        index = node.end_byte
        while index < len(source) and source[index:index + 1].isspace():
            index += 1
        if source[index:index + 1] != b"(":
            continue
        depth = 0
        while index < len(source):
            if index in protected:
                index = protected[index]
                continue
            char = source[index]
            if char == 40:
                depth += 1
            elif char == 41:
                depth -= 1
                if depth == 0:
                    candidates.append((node.start_byte, index + 1))
                    break
            index += 1
    result = []
    for start, end in sorted(candidates):
        if not result or start >= result[-1][1]:
            result.append((start, end))
    return result


def token_runs(text, roles):
    byte, start, previous = 0, 0, None
    for index, char in enumerate(text):
        style = roles[byte]
        byte += len(char.encode("utf-8"))
        if previous is not None and style != previous:
            yield start, previous, text[start:index]
            start = index
        previous = style
    if previous is not None:
        yield start, previous, text[start:]


def cpp_extensions(source, tree, roles):
    for node in nodes(tree.root_node):
        if node.type in {"identifier", "type_identifier", "field_identifier"} and is_extension_macro(node_text(node, source)):
            roles[node.start_byte:node.end_byte] = ["no"] * (node.end_byte - node.start_byte)
        if node.type == "call_expression":
            fn = node.child_by_field_name("function")
            arguments = node.child_by_field_name("arguments")
            if fn and arguments and node_text(fn, source) in {"UFUNCTION", "UPROPERTY", "UCLASS", "USTRUCT", "UENUM", "UINTERFACE", "UPARAM", "UMETA"}:
                for child in nodes(arguments):
                    if child.type in {"identifier", "field_identifier"}:
                        roles[child.start_byte:child.end_byte] = ["na"] * (child.end_byte - child.start_byte)


def csharp_extensions(source, tree, roles):
    # SDK type identity is known even when an example omits its declaration.
    for node in nodes(tree.root_node):
        if node.type == "identifier" and node_text(node, source) == "DataBindingUtilities":
            receiver = node.parent if node.parent and node.parent.type == "member_access_expression" and field(node) == "name" else node
            if receiver.parent and receiver.parent.type == "member_access_expression" and field(receiver) == "expression":
                roles[node.start_byte:node.end_byte] = ["nc"] * (node.end_byte - node.start_byte)


class TreeSitterHighlighter:
    kind = "cpp"

    def get_tokens_unprocessed(self, text, **options):
        source = text.encode("utf-8")
        parser = Parser(language(self.kind))
        tree = parser.parse(source)
        macros = macro_ranges(tree.root_node, source) if self.kind == "cpp" and options.get("_macros", True) else []
        if macros:
            masked = bytearray(source)
            for start, end in macros:
                for index in range(start, end):
                    if masked[index] not in (10, 13):
                        masked[index] = 32
            tree = parser.parse(bytes(masked))
        # Parse type-only table cells as declarations without modifying output.
        if re.fullmatch(r"[\w\s:.<>,*&?\[\]]+", text) and not text.endswith(";"):
            candidate = source + b" __markupui_preview;"
            alternate = parser.parse(candidate)
            if not alternate.root_node.has_error:
                source, tree = candidate, alternate
        roles, tree = official_roles(source, self.kind, tree)
        if self.kind == "cpp":
            cpp_extensions(source, tree, roles)
        else:
            csharp_extensions(source, tree, roles)
        for start, end in macros:
            byte = start
            for _, role, value in self.get_tokens_unprocessed(source[start:end].decode("utf-8"), _macros=False):
                length = len(value.encode("utf-8"))
                roles[byte:byte + length] = [role] * length
                byte += length
        yield from token_runs(text, roles)


class CppHighlighter(TreeSitterHighlighter):
    kind = "cpp"


class CSharpHighlighter(TreeSitterHighlighter):
    kind = "csharp"
