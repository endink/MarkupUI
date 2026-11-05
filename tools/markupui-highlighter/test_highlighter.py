"""Regression checks for template boundaries and original HTML behavior."""

import unittest
from unittest.mock import patch
from importlib import import_module
from importlib.resources import files
import hashlib
import json

from markdown import Markdown


from markupui_languages import MarkupHTMLHighlighter, highlight_tokens
from markupui_tree_sitter import CppHighlighter, CSharpHighlighter, official_query, official_roles, token_runs


class UpstreamQueryTests(unittest.TestCase):
    def test_bundled_queries_and_licenses_match_pinned_checksums(self):
        root = files('markupui_queries')
        manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(set(manifest), {'c', 'cpp', 'csharp', 'html', 'css', 'javascript', 'json', 'yaml'})
        for kind, entry in manifest.items():
            for filename, metadata in entry['files'].items():
                data = (root / kind / filename).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), metadata['sha256'])
            if kind not in {'c', 'csharp'}:
                installed = import_module('tree_sitter_' + kind)
                self.assertEqual((root / kind / 'highlights.scm').read_text(encoding='utf-8'), installed.HIGHLIGHTS_QUERY)

    def test_all_official_queries_compile_and_cpp_inherits_c(self):
        for kind in ('cpp', 'csharp', 'html', 'css', 'javascript', 'json', 'yaml'):
            self.assertGreater(official_query(kind).pattern_count, 0)
        source = 'if (ready) { auto value = 1; co_return value; }'
        roles = {(role, value) for _, role, value in CppHighlighter().get_tokens_unprocessed(source)}
        self.assertIn(('k', 'if'), roles)
        self.assertIn(('k', 'co_return'), roles)
        self.assertIn(('nc', 'auto'), roles)

    def test_official_predicates_filter_captures(self):
        source = 'int CONSTANT = value;'
        roles = {(role, value) for _, role, value in CppHighlighter().get_tokens_unprocessed(source)}
        self.assertIn(('no', 'CONSTANT'), roles)
        self.assertIn(('n', 'value'), roles)
        self.assertNotIn(('no', 'value'), roles)

    def test_official_javascript_locals_suppress_builtin_capture(self):
        source = 'function example(window) { return window; } window;'
        tokens = list(highlight_tokens(source, 'javascript'))
        roles = [role for _, role, value in tokens if value == 'window']
        self.assertEqual(roles, ['n', 'n', 'nb'])


class HighlightTests(unittest.TestCase):
    def tokens(self, source):
        tokens = list(MarkupHTMLHighlighter().get_tokens_unprocessed(source))
        self.assertEqual("".join(value for _, _, value in tokens), source)
        self.assertFalse(any(token == "err" for _, token, _ in tokens))
        return [(token, value) for _, token, value in tokens]

    def test_directive_prefixes_and_dotted_options(self):
        tokens = self.tokens('<input @value="{Name}" mk:value.mode="twoWay"><p @else>Wait</p>')
        for name in ("@value", "mk:value.mode", "@else"):
            self.assertIn(('nd', name), tokens)

    def test_expression_roles_and_nested_bindings(self):
        tokens = self.tokens('<p @text="{Price, converter={Currency, parameter={@item.Code, 1.5e2}}, mode=oneWay}">{{ @index + 1 }}</p>')
        for pair in (('py', "Price"), ('k', "converter"),
                     ('nv', "@item"), ('nv', "@index"),
                     ('m', "1.5e2"), ('si', "{{")):
            self.assertIn(pair, tokens)

    def test_literals_containing_template_syntax(self):
        tokens = self.tokens('<p>{{ \'@item {not binding}\' ?? Name }}</p>')
        self.assertIn(('s1', "'@item {not binding}'"), tokens)
        self.assertNotIn(('nv', "@item"), tokens)

    def test_nested_trigger_behavior_options(self):
        source = '''<section @trigger="{
    name='mytrigger',
    parameter={param1='value1', param2='value2'},
    do:command={Save, parameter={Name, Age, Selected}},
    do:class={value='active', op='append'}
}"></section>'''
        tokens = self.tokens(source)
        for option in ('name', 'parameter', 'param1', 'param2', 'value', 'op'):
            self.assertIn(('k', option), tokens)
        self.assertIn(('py', 'Save'), tokens)
        for value in ("'value1'", "'value2'", "'active'", "'append'"):
            self.assertIn(('s1', value), tokens)

    def test_comment_script_style_and_plain_attributes_are_not_bindings(self):
        tokens = self.tokens('<!-- {{ @item }} --><style>.a { color: red; }</style><script>let x = "{{ @item }}";</script><p title="{{ @item }}">text</p>')
        self.assertFalse(any(token == 'nv' for token, _ in tokens))
        self.assertTrue(any(token.startswith("c") for token, _ in tokens))

    def test_single_quoted_attribute_and_alias_operator(self):
        tokens = self.tokens("<p @if='{Health :le: 0}'>{{ Health }}</p>")
        self.assertIn(('nd', "@if"), tokens)
        self.assertIn(('m', "0"), tokens)

    def test_escaped_interpolation_stays_literal(self):
        tokens = self.tokens(r'<p>\{{ @item }}</p>')
        self.assertNotIn(('nv', "@item"), tokens)


class ModelHighlightTests(unittest.TestCase):
    def test_cpp_named_keywords_and_constants(self):
        source = '\n'.join((
            'const auto& value = this->GetValue();',
            'inline static constexpr auto Count = 3;',
            'decltype(auto) Result();',
            'bool ready = true;',
            'bool done = false;',
            'auto pointer = nullptr;',
            '// auto this true false',
            '"auto this true false";',
        ))
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(role, value) for _, role, value in tokens}
        for name in ('const', 'constexpr'):
            self.assertIn(('k', name), roles)
        self.assertIn(('nc', 'auto'), roles)
        self.assertIn(('nb', 'this'), roles)
        self.assertIn(('no', 'nullptr'), roles)
        self.assertEqual(sum(value == 'auto' and role == 'nc' for _, role, value in tokens), 4)

    def test_csharp_using_directives_and_static_sdk_receiver(self):
        source = '\n'.join((
            'using System;',
            'using MarkupUI.Sdk.Binding;',
            'global using System.Collections.Generic;',
            'using static System.Math;',
            'using Text = System.String;',
            'DataBindingUtilities.RegisterGlobalCommand("Save", callback);',
            'model.RegisterGlobalCommand("Save", callback);',
        ))
        tokens = list(CSharpHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(role, value) for _, role, value in tokens}
        for name in ('System', 'MarkupUI', 'Sdk', 'Binding', 'Collections', 'Generic'):
            self.assertIn(('n', name), roles)
        for name in ('Math', 'Text', 'String'):
            self.assertIn(('n', name), roles)
        self.assertIn(('nc', 'DataBindingUtilities'), roles)
        self.assertIn(('nf', 'RegisterGlobalCommand'), roles)
        self.assertIn(('n', 'model'), roles)

    def test_consecutive_cpp_macros_without_semicolons(self):
        macros = '\n'.join((
            'MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 80)',
            'MARKUPUI_PROPERTY(PlayerObject, int32_t, TargetHealth, 100)',
            'MARKUPUI_PROPERTY(PlayerObject, bool, Confirmed, true)',
        ))
        for source in (macros, 'class PlayerObject {\n' + macros + '\nFMarkupUIElement Element;\n};'):
            tokens = list(CppHighlighter().get_tokens_unprocessed(source))
            self.assertEqual(''.join(value for _, _, value in tokens), source)
            macro_roles = [role for _, role, value in tokens if value == 'MARKUPUI_PROPERTY']
            self.assertEqual(macro_roles, ['no'] * 3)
            if 'FMarkupUIElement' in source:
                self.assertIn(('nc', 'FMarkupUIElement'), [(role, value) for _, role, value in tokens])

    def test_macro_parentheses_in_strings_and_comments(self):
        source = 'UE_LOG(LogTemp, Log, TEXT("Closing ) and opening ("));\nMARKUPUI_PROPERTY(PlayerObject, int32_t, Health, /* ) */ 80)'
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(role, value) for _, role, value in tokens}
        self.assertIn(('no', 'UE_LOG'), roles)
        self.assertIn(('no', 'MARKUPUI_PROPERTY'), roles)

    def test_tree_sitter_unicode_offsets_and_raw_strings(self):
        samples = (
            (CppHighlighter(), '// 中文说明\nFMarkupUIElement status;\nstatus.SetInnerHtml(TEXT("Ready"));\nauto text = R"tag(PlayerObject {})tag";'),
            (CSharpHighlighter(), '// 中文说明\nclass Player { public System.ComponentModel.INotifyPropertyChanged Source; string Text = "中文"; }'),
        )
        for lexer, source in samples:
            tokens = list(lexer.get_tokens_unprocessed(source))
            self.assertEqual(''.join(value for _, _, value in tokens), source)
            for offset, _, value in tokens:
                self.assertEqual(source[offset:offset + len(value)], value)
            self.assertTrue(any(token.startswith("c") for _, token, _ in tokens))
            self.assertTrue(any(token.startswith("s") for _, token, _ in tokens))
        roles = {(token, value) for _, token, value in samples[1][0].get_tokens_unprocessed(samples[1][1])}
        self.assertIn(('n', 'INotifyPropertyChanged'), roles)

    def test_tree_sitter_type_only_and_incomplete_snippets(self):
        for lexer in (CppHighlighter(), CSharpHighlighter()):
            tokens = list(lexer.get_tokens_unprocessed('FMarkupUIElement'))
            self.assertIn(('nc', 'FMarkupUIElement'), [(token, value) for _, token, value in tokens])
            source = 'void Save(\n'
            self.assertEqual(''.join(value for _, _, value in lexer.get_tokens_unprocessed(source)), source)

    def test_cpp_aliases_and_object_named_methods(self):
        source = '''using MemberAccess = MarkupUI::Binding::Modeling::Internal::Macros::MemberAccess<PlayerObject>;
using HealthValue = int32_t;
using ExternalAlias = External::GenericType<PlayerObject>;
HealthValue Health = 100;
ObservableSupport Support;
auto& object = Support.GetObject();
GetMarkupObservableObject(player);
Support.BindOwner(player);
'''
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for name in ('MemberAccess', 'HealthValue', 'ObservableSupport', 'PlayerObject', 'ExternalAlias', 'GenericType'):
            self.assertIn(('nc', name), roles)
        for name in ('GetObject', 'GetMarkupObservableObject', 'BindOwner'):
            self.assertIn(('nf', name), roles)
            self.assertNotIn(('nc', name), roles)

    def test_cpp_qualified_type_namespaces(self):
        source = 'class PlayerObject : public MarkupUI::Binding::Modeling::ObservableObject {};\nusing Property = MarkupUI::Binding::Modeling::Property;'
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for name in ('MarkupUI', 'Binding', 'Modeling'):
            self.assertIn(('nc', name), roles)
        self.assertIn(('nc', 'ObservableObject'), roles)

    def test_cpp_unreal_declaration_types(self):
        source = '\n'.join((
            'FMarkupUIElement root = Widget->GetRootElement();',
            'FMarkupUIElement status = root.GetElementById(TEXT("status"));',
            'FMarkupUIInputElement input = status.AsInput();',
            'UMarkupUIWidget* Widget;',
            'void HandleClick(const FMarkupUIPointerEvent& Event);',
            'FCustomValue value;',
            'value.FCustomValue();',
        ))
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for name in ('FMarkupUIElement', 'FMarkupUIInputElement',
                     'UMarkupUIWidget', 'FMarkupUIPointerEvent', 'FCustomValue'):
            self.assertIn(('nc', name), roles)
        for name in ('root', 'status', 'input', 'Widget', 'Event', 'value'):
            self.assertNotIn(('nc', name), roles)
        for name in ('Widget', 'root', 'status'):
            self.assertNotIn(('nf', name), roles)
        for name in ('GetRootElement', 'GetElementById', 'AsInput', 'HandleClick', 'FCustomValue'):
            self.assertIn(('nf', name), roles)

    def test_cpp_standard_strings(self):
        source = 'std::string GetName(const std::string& value);\nstd::string_view view;\nint string = 0;'
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        self.assertIn(('nc', 'string'), roles)
        self.assertIn(('nc', 'string_view'), roles)
        self.assertIn(('n', 'string'), roles)

    def test_deep_qualified_types(self):
        for lexer, source, namespaces, final in (
            (CppHighlighter(), 'MarkupUI::Binding::KeyValue<TKey, TValue>', ('MarkupUI', 'Binding'), 'KeyValue'),
            (CSharpHighlighter(), 'System.Collections.Generic.KeyValuePair<TKey, TValue>', ('System', 'Collections', 'Generic'), 'KeyValuePair'),
        ):
            tokens = list(lexer.get_tokens_unprocessed(source))
            self.assertEqual(''.join(value for _, _, value in tokens), source)
            roles = {(token, value) for _, token, value in tokens}
            for namespace in namespaces:
                self.assertIn(('nc' if lexer.kind == 'cpp' else 'n', namespace), roles)
            self.assertIn(('nc', final), roles)
            self.assertIn(('nc', 'TKey'), roles)
            self.assertIn(('nc', 'TValue'), roles)

    def test_multiple_generic_arguments(self):
        for lexer in (CppHighlighter(), CSharpHighlighter()):
            source = 'Container<PlayerObject, HealthState, Nested<OtherType, ResultType>>'
            roles = {(token, value) for _, token, value in lexer.get_tokens_unprocessed(source)}
            for name in ('PlayerObject', 'HealthState', 'Nested', 'OtherType', 'ResultType'):
                self.assertIn(('nc', name), roles)

    def test_enum_types_and_members(self):
        for lexer, source in (
            (CppHighlighter(), 'enum class HealthState : int32_t { Healthy = 0, Critical = 1 }; HealthState::Healthy;'),
            (CSharpHighlighter(), 'public enum HealthState { Healthy = 0, Critical = 1 } HealthState.Healthy;'),
        ):
            tokens = list(lexer.get_tokens_unprocessed(source))
            self.assertEqual(''.join(value for _, _, value in tokens), source)
            # Enum reference classifications come from upstream, not a local
            # symbol table guessing which identifiers are members or types.
            expected = list(token_runs(source, official_roles(source.encode('utf-8'), lexer.kind)[0]))
            self.assertEqual(tokens, expected)

    def test_unreal_macro_specifiers(self):
        source = 'UFUNCTION(BlueprintCallable, Category = "Player", meta=(DisplayName="Save", AdvancedDisplay="1"))\nvoid Save();'
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        self.assertIn(('no', 'UFUNCTION'), roles)
        for name in ('BlueprintCallable', 'Category', 'meta', 'DisplayName', 'AdvancedDisplay'):
            self.assertIn(('na', name), roles)
        self.assertIn(('nf', 'Save'), roles)

    def test_uppercase_macro_calls(self):
        source = 'GET_MEMBER_NAME_CHECKED(UPlayerData, Health); TEXT("Health"); UE_LOG(LogTemp, Warning, TEXT("Test"));'
        roles = {(token, value) for _, token, value in CppHighlighter().get_tokens_unprocessed(source)}
        for name in ('GET_MEMBER_NAME_CHECKED', 'TEXT', 'UE_LOG'):
            self.assertIn(('no', name), roles)

    def test_cpp_sdk_types_macros_and_calls(self):
        source = 'MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 100)\nauto p = MarkupUI::MakeMarkupShared<PlayerObject>();\np->SetHealth(80);'
        tokens = list(CppHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for pair in (('no', 'MARKUPUI_PROPERTY'), ('nc', 'PlayerObject'),
                     ('nf', 'MakeMarkupShared'), ('nf', 'SetHealth')):
            self.assertIn(pair, roles)

    def test_csharp_fields_properties_and_events(self):
        source = 'public class PlayerObject : INotifyPropertyChanged { private int _health; public int Health { get { return _health; } } }'
        tokens = list(CSharpHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for pair in (('nc', 'INotifyPropertyChanged'),
                     ('n', '_health'), ('n', 'Health')):
            self.assertIn(pair, roles)

    def test_csharp_weak_reference_type(self):
        source = 'private WeakReference<OwnerObject> _weaponOwner;\npublic System.WeakReference<OwnerObject> WeaponOwner { get; set; }\nvar owner = new WeakReference<OwnerObject>(target);'
        tokens = list(CSharpHighlighter().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        references = [(token, value) for _, token, value in tokens if value == 'WeakReference']
        self.assertEqual(references, [('nc', 'WeakReference')] * 3)

    def test_comments_and_strings_keep_original_roles(self):
        for lexer in (CppHighlighter(), CSharpHighlighter()):
            tokens = list(lexer.get_tokens_unprocessed('// MARKUPUI_PROPERTY PlayerObject\n"PlayerObject SetHealth()"'))
            self.assertFalse(any(token in {"n", "nc", "nn", "nf", "py", "nv", "vi", "na", "nd", "no"} for _, token, _ in tokens))

    def test_no_pygments_highlight_calls_in_markdown(self):
        samples = [
            ('cpp', 'FMarkupUIElement root = Widget->GetRootElement();', 'class="nc"'),
            ('csharp', 'public class PlayerObject : INotifyPropertyChanged {}', 'class="nc"'),
            ('html', '<p @if="{IsReady}">Ready</p>', 'class="nd"'),
            ('css', '.panel { color: red; }', 'class="py"'),
            ('javascript', 'function save() { return true; }', 'class="k"'),
            ('json', '{"enabled": true}', 'class="kc"'),
            ('yaml', 'enabled: true', 'class="kc"'),
            ('xml', '<section mk:if="{Ready}"/>', 'class="nd"'),
        ]
        with patch('pygments.highlight', side_effect=AssertionError('Pygments called')), \
             patch('pygments.lexers.get_lexer_by_name', side_effect=AssertionError('Lexer called')), \
             patch('pymdownx.highlight.Highlight.highlight', side_effect=AssertionError('Default highlighter called')):
            for _ in range(3):
                md = Markdown(extensions=['pymdownx.superfences', 'pymdownx.inlinehilite', 'markupui_highlighter'])
                for language, source, token in samples:
                    rendered = md.reset().convert('```' + language + '\n' + source + '\n```')
                    self.assertIn(token, rendered, (language, rendered))
                inline = md.reset().convert('`#!cpp FMarkupUIElement` and `#!csharp System.Collections.Generic.List<int>`')
                self.assertIn('class="nc"', inline)
                indented = md.reset().convert('    <plain>& unsafe')
                self.assertIn('&lt;plain&gt;&amp; unsafe', indented)

    def test_tree_sitter_tabs_inline_and_fence_metadata(self):
        md = Markdown(extensions=['attr_list', 'pymdownx.superfences', 'pymdownx.inlinehilite', 'pymdownx.tabbed', 'markupui_highlighter'])
        source = '\n'.join([
            '=== "C++"', '', '    ```cpp title="Example" linenums="1" hl_lines="2"',
            '    FMarkupUIElement root;', '    root.IsValid();', '    ```', '',
            '=== "C#"', '', '    `#!csharp List<int>`',
        ])
        rendered = md.convert(source)
        for expected in ('tabbed', 'Example', 'class="lineno"', 'class="hll"', 'class="nc"', '__span-'):
            self.assertIn(expected, rendered)

    def test_unknown_language_escapes_and_never_executes_html(self):
        md = Markdown(extensions=['pymdownx.superfences', 'markupui_highlighter'])
        rendered = md.convert('```unknown\n<script>alert("test")</script>\n```')
        self.assertIn('&lt;script&gt;', rendered)
        self.assertNotIn('<script>', rendered)



if __name__ == "__main__":
    unittest.main()
