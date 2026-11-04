"""HTML plus Markup UI bindings, following the editor's highlighting roles.

Reference: MarkupUI-VSCode-Extensions/src/highlight.ts and highlight-palette.ts.
This lexer colors declarations; it does not validate runtime support.
"""

import re

from markdown.extensions import Extension
from pygments.lexer import RegexLexer, bygroups, inherit
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers.dotnet import CSharpLexer
from pygments.lexers.html import HtmlLexer
from pygments.token import Comment, Keyword, Name, Number, Operator, Punctuation, String, Text


IDENTIFIER = r"[^\W\d]\w*"
__all__ = ["MarkupUILexer", "MarkupCppLexer", "MarkupCSharpLexer"]


class BindingExpressionLexer(RegexLexer):
    """Expression roles shared by interpolation and attribute bindings."""

    tokens = {
        "root": [
            (r"\s+", Text),
            (r"'(?:\\.|[^'\\])*'", String.Single),
            (r"&(?:[A-Za-z]+|#\d+|#x[\da-fA-F]+);", Name.Entity),
            (r"\b(?:true|false|null)\b", Keyword.Constant),
            (r"\b(?:oneWayToSource|oneWay|twoWay|oneTime|input|change|blur|explicit)\b", Keyword),
            (r"(?:converter\.parameter|converter|parameter|mode|update|modifiers|button)\b(?=\s*=)", Keyword),
            (r"@[A-Za-z_]\w*", Name.Variable),
            (r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?", Number),
            (r":(?:lt|le|gt|ge|and|or):", Operator.Word),
            (r"\?\?|&&|\|\||==|!=|<=|>=|[+*/%!=<>-]", Operator),
            (IDENTIFIER, Name.Property),
            (r"[.\[\](),]", Punctuation),
            # Bindings can contain nested converter and parameter declarations.
            (r"[{}]", String.Interpol),
            (r".", Text),
        ],
    }


def expression(lexer, match):
    for offset, token, value in BindingExpressionLexer().get_tokens_unprocessed(match.group()):
        yield match.start() + offset, token, value


class MarkupUILexer(HtmlLexer):
    """Keep HTML/CSS/JS lexing, adding template syntax only where allowed."""

    name = "Markup UI HTML"
    aliases = ["markupui"]
    filenames = []
    mimetypes = []
    tokens = {
        "root": [
            (r"\\(?:\\)*\{\{", Text),
            (r"\{\{", String.Interpol, "interpolation"),
            (r"[^<&{\\]+", Text),
            (r"\\.|\{(?!\{)", Text),
            inherit,
        ],
        "tag": [
            (r"((?:@|mk:)[\w.:-]+)(\s*)(=)(\s*)",
             bygroups(Name.Decorator, Text, Operator, Text), "binding-attr"),
            (r"(?:@|mk:)[\w.:-]+", Name.Decorator),
            inherit,
        ],
        "binding-attr": [
            (r'"', String, ("#pop", "binding-double")),
            (r"'", String, ("#pop", "binding-single")),
            (r"[^\s>]+", String, "#pop"),
        ],
        "binding-double": [
            (r'"', String, "#pop"),
            (r"\{", String.Interpol, "binding-expression"),
            (r'[^"{]+', String),
        ],
        "binding-single": [
            (r"'", String, "#pop"),
            (r"\{", String.Interpol, "binding-expression"),
            (r"[^'{]+", String),
        ],
        "binding-expression": [
            (r"'(?:\\.|[^'\\])*'", String.Single),
            (r"\{", String.Interpol, "#push"),
            (r"\}", String.Interpol, "#pop"),
            (r"[^{}']+", expression),
        ],
        "interpolation": [
            (r"'(?:\\.|[^'\\])*'", String.Single),
            (r"\}\}", String.Interpol, "#pop"),
            (r"[^}']+|\}(?!\})", expression),
        ],
    }


SDK_TYPES = {
    "ObservableObject", "ObservableArray", "ObservableMap", "ObservableSet",
    "MarkupSharedPtr", "MarkupWeakPtr", "String", "StringView", "Property",
    "IObject", "IArray", "IMap", "ISet", "ICommand", "DelegateCommand",
    "INotifyPropertyChanged", "PropertyChangedEventHandler", "PropertyChangedEventArgs",
    "ObservableCollection", "ObservableDictionary", "ObservableHashSet", "WeakReference",
    "MemberAccess", "ObservableSupport",
}


class ModelRoles:
    """Add lexical SDK hints without claiming to resolve symbols or types."""

    def get_tokens_unprocessed(self, text, *args, **kwargs):
        qualified_roles = {}
        ue_specifiers = set()
        for macro in re.finditer(r"\b(?:UFUNCTION|UPROPERTY|UCLASS|USTRUCT|UENUM|UINTERFACE|UPARAM|UMETA)\s*\(", text):
            depth = 1
            for item in re.finditer(r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|//[^\n]*|/\*[\s\S]*?\*/|[()]|\b[A-Za-z_]\w*\b''', text[macro.end():]):
                value = item.group()
                if value == '(':
                    depth += 1
                elif value == ')':
                    depth -= 1
                    if not depth:
                        break
                elif re.fullmatch(r"[A-Za-z_]\w*", value):
                    ue_specifiers.add(macro.end() + item.start())
        enum_types = set()
        enum_members = set()
        for declaration in re.finditer(r"\benum\s+(?:(?:class|struct)\s+)?([A-Za-z_]\w*)\s*(?::[^{}]+)?\{([^{}]*)\}", text, re.S):
            enum_types.add(declaration.group(1))
            for member in re.finditer(r"(?:^|,)\s*([A-Za-z_]\w*)", declaration.group(2)):
                enum_members.add(declaration.start(2) + member.start(1))
        generic_arguments = set()
        depth = 0
        for match in re.finditer(r"[<>]|\b[A-Za-z_]\w*\b", text):
            value = match.group()
            if value == '<':
                depth += 1
            elif value == '>':
                depth = max(0, depth - 1)
            elif depth and value[0].isupper():
                generic_arguments.add(match.start())
        for match in re.finditer(r"\b(?:MarkupUI|System|std)(?:(?:::|\.)[A-Za-z_]\w*)+", text):
            parts = list(re.finditer(r"[A-Za-z_]\w*", match.group()))
            if not parts[-1].group()[0].isupper() and not match.group().startswith("std::"):
                continue
            for index, part in enumerate(parts):
                qualified_roles[match.start() + part.start()] = (
                    Name.Class if index == len(parts) - 1 else Name.Namespace
                )
        aliases = set(re.findall(r"\busing\s+([A-Za-z_]\w*)\s*=", text))
        for target in re.findall(r"\busing\s+[A-Za-z_]\w*\s*=\s*([^;]+);", text):
            match = re.match(r"(?:(?:[A-Za-z_]\w*)\s*::\s*)*([A-Za-z_]\w*)", target)
            if match:
                aliases.add(match.group(1))
        for offset, token, value in super().get_tokens_unprocessed(text, *args, **kwargs):
            if token in Name:
                suffix = text[offset + len(value):]
                if re.fullmatch(r"MARKUPUI_[A-Z0-9_]+", value) or value in {"UFUNCTION", "UPROPERTY", "UCLASS", "USTRUCT", "UENUM", "UINTERFACE", "UPARAM", "UMETA", "GENERATED_BODY", "GENERATED_UCLASS_BODY"}:
                    token = Name.Constant
                elif offset in ue_specifiers:
                    token = Name.Attribute
                elif re.fullmatch(r"[A-Z][A-Z0-9_]*", value) and re.match(r"\s*\(", suffix):
                    token = Name.Constant
                elif value in enum_types:
                    token = Name.Class
                elif offset in enum_members or any(re.search(r"\b" + re.escape(name) + r"\s*(?:::|\.)\s*$", text[:offset]) for name in enum_types):
                    token = Name.Constant
                elif offset in qualified_roles and not re.match(r"\s*(?:<[^<>;{}\n]*>)?\s*\(", suffix):
                    token = qualified_roles[offset]
                elif value in SDK_TYPES or value in aliases:
                    token = Name.Class
                elif offset in generic_arguments and token in (Name, Name.Other):
                    token = Name.Class
                elif re.fullmatch(r"T(?:[A-Z][A-Za-z0-9_]*|[0-9]+)?", value) and re.search(r"[<,]\s*$", text[:offset]) and re.match(r"\s*[,>\[?]", suffix):
                    token = Name.Class
                elif token in (Name, Name.Other, Name.Function) and re.match(r"\s*(?:<[^<>;{}\n]*>)?\s*\(", suffix):
                    token = Name.Function
                elif value.endswith(("Object", "ViewModel")):
                    token = Name.Class
                elif value.startswith("_") and token == Name:
                    token = Name.Variable.Instance
                elif token == Name and re.match(r"\s*\{\s*(?:get|set)\b", suffix):
                    token = Name.Property
            yield offset, token, value


class MarkupCppLexer(ModelRoles, CppLexer):
    name = "Markup UI C++"
    aliases = ["markupui-cpp"]
    filenames = []

    def get_tokens_unprocessed(self, text, *args, **kwargs):
        for offset, token, value in super().get_tokens_unprocessed(text, *args, **kwargs):
            if token in Name and value in {"string", "wstring", "u8string", "u16string", "u32string", "string_view", "wstring_view"} and re.search(r"\bstd\s*::\s*$", text[:offset]):
                token = Name.Class
            elif token in Name and token != Name.Class and re.match(r"\s*::", text[offset + len(value):]):
                token = Name.Namespace
            yield offset, token, value


class MarkupCSharpLexer(ModelRoles, CSharpLexer):
    name = "Markup UI C#"
    aliases = ["markupui-csharp"]
    filenames = []


class MarkupHighlightExtension(Extension):
    """Register lexers per Markdown instance, including incremental workers.

    Entry-point discovery alone is unreliable in reused Zensical workers.
    Keep the registration local to the Python process, never modify Pygments
    installation files. The lookup-table integration is regression-tested.
    """

    def extendMarkdown(self, md):
        from pygments.lexers import LEXERS

        for cls in (MarkupUILexer, MarkupCppLexer, MarkupCSharpLexer):
            LEXERS[cls.__name__] = (
                __name__, cls.name, tuple(cls.aliases), (), (),
            )
        md.registerExtension(self)


def makeExtension(**kwargs):
    return MarkupHighlightExtension(**kwargs)
