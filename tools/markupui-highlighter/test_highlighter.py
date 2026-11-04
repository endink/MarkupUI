"""Regression checks for template boundaries and original HTML behavior."""

import unittest
from unittest.mock import patch

from markdown import Markdown

from pygments.token import Comment, Error, Keyword, Name, Number, String

from markupui_highlighter import MarkupUILexer, MarkupCppLexer, MarkupCSharpLexer


class HighlightTests(unittest.TestCase):
    def tokens(self, source):
        tokens = list(MarkupUILexer().get_tokens_unprocessed(source))
        self.assertEqual("".join(value for _, _, value in tokens), source)
        self.assertFalse(any(token in Error for _, token, _ in tokens))
        return [(token, value) for _, token, value in tokens]

    def test_directive_prefixes_and_dotted_options(self):
        tokens = self.tokens('<input @value="{Name}" mk:value.mode="twoWay"><p @else>Wait</p>')
        for name in ("@value", "mk:value.mode", "@else"):
            self.assertIn((Name.Decorator, name), tokens)

    def test_expression_roles_and_nested_bindings(self):
        tokens = self.tokens('<p @text="{Price, converter={Currency, parameter={@item.Code, 1.5e2}}, mode=oneWay}">{{ @index + 1 }}</p>')
        for pair in ((Name.Property, "Price"), (Keyword, "converter"),
                     (Name.Variable, "@item"), (Name.Variable, "@index"),
                     (Number, "1.5e2"), (String.Interpol, "{{")):
            self.assertIn(pair, tokens)

    def test_literals_containing_template_syntax(self):
        tokens = self.tokens('<p>{{ \'@item {not binding}\' ?? Name }}</p>')
        self.assertIn((String.Single, "'@item {not binding}'"), tokens)
        self.assertNotIn((Name.Variable, "@item"), tokens)

    def test_comment_script_style_and_plain_attributes_are_not_bindings(self):
        tokens = self.tokens('<!-- {{ @item }} --><style>.a { color: red; }</style><script>let x = "{{ @item }}";</script><p title="{{ @item }}">text</p>')
        self.assertFalse(any(token == Name.Variable for token, _ in tokens))
        self.assertTrue(any(token in Comment for token, _ in tokens))

    def test_single_quoted_attribute_and_alias_operator(self):
        tokens = self.tokens("<p @if='{Health :le: 0}'>{{ Health }}</p>")
        self.assertIn((Name.Decorator, "@if"), tokens)
        self.assertIn((Number, "0"), tokens)

    def test_escaped_interpolation_stays_literal(self):
        tokens = self.tokens(r'<p>\{{ @item }}</p>')
        self.assertNotIn((Name.Variable, "@item"), tokens)


class ModelHighlightTests(unittest.TestCase):
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
        tokens = list(MarkupCppLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for name in ('MemberAccess', 'HealthValue', 'ObservableSupport', 'PlayerObject', 'ExternalAlias', 'GenericType'):
            self.assertIn((Name.Class, name), roles)
        for name in ('GetObject', 'GetMarkupObservableObject', 'BindOwner'):
            self.assertIn((Name.Function, name), roles)
            self.assertNotIn((Name.Class, name), roles)

    def test_cpp_qualified_type_namespaces(self):
        source = 'class PlayerObject : public MarkupUI::Binding::Modeling::ObservableObject {};\nusing Property = MarkupUI::Binding::Modeling::Property;'
        tokens = list(MarkupCppLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for name in ('MarkupUI', 'Binding', 'Modeling'):
            self.assertIn((Name.Namespace, name), roles)
        self.assertIn((Name.Class, 'ObservableObject'), roles)

    def test_cpp_standard_strings(self):
        source = 'std::string GetName(const std::string& value);\nstd::string_view view;\nint string = 0;'
        tokens = list(MarkupCppLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        self.assertIn((Name.Namespace, 'std'), roles)
        self.assertIn((Name.Class, 'string'), roles)
        self.assertIn((Name.Class, 'string_view'), roles)
        self.assertIn((Name, 'string'), roles)

    def test_deep_qualified_types(self):
        for lexer, source, namespaces, final in (
            (MarkupCppLexer(), 'MarkupUI::Binding::KeyValue<TKey, TValue>', ('MarkupUI', 'Binding'), 'KeyValue'),
            (MarkupCSharpLexer(), 'System.Collections.Generic.KeyValuePair<TKey, TValue>', ('System', 'Collections', 'Generic'), 'KeyValuePair'),
        ):
            tokens = list(lexer.get_tokens_unprocessed(source))
            self.assertEqual(''.join(value for _, _, value in tokens), source)
            roles = {(token, value) for _, token, value in tokens}
            for namespace in namespaces:
                self.assertIn((Name.Namespace, namespace), roles)
            self.assertIn((Name.Class, final), roles)
            self.assertIn((Name.Class, 'TKey'), roles)
            self.assertIn((Name.Class, 'TValue'), roles)

    def test_multiple_generic_arguments(self):
        for lexer in (MarkupCppLexer(), MarkupCSharpLexer()):
            source = 'Container<PlayerObject, HealthState, Nested<OtherType, ResultType>>'
            roles = {(token, value) for _, token, value in lexer.get_tokens_unprocessed(source)}
            for name in ('PlayerObject', 'HealthState', 'Nested', 'OtherType', 'ResultType'):
                self.assertIn((Name.Class, name), roles)

    def test_enum_types_and_members(self):
        for lexer, source in (
            (MarkupCppLexer(), 'enum class HealthState : int32_t { Healthy = 0, Critical = 1 }; HealthState::Healthy;'),
            (MarkupCSharpLexer(), 'public enum HealthState { Healthy = 0, Critical = 1 } HealthState.Healthy;'),
        ):
            tokens = list(lexer.get_tokens_unprocessed(source))
            self.assertEqual(''.join(value for _, _, value in tokens), source)
            for _, token, value in tokens:
                if value == 'HealthState':
                    self.assertEqual(token, Name.Class)
                if value in ('Healthy', 'Critical'):
                    self.assertEqual(token, Name.Constant)

    def test_unreal_macro_specifiers(self):
        source = 'UFUNCTION(BlueprintCallable, Category = "Player", meta=(DisplayName="Save", AdvancedDisplay="1"))\nvoid Save();'
        tokens = list(MarkupCppLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        self.assertIn((Name.Constant, 'UFUNCTION'), roles)
        for name in ('BlueprintCallable', 'Category', 'meta', 'DisplayName', 'AdvancedDisplay'):
            self.assertIn((Name.Attribute, name), roles)
        self.assertIn((Name.Function, 'Save'), roles)

    def test_uppercase_macro_calls(self):
        source = 'GET_MEMBER_NAME_CHECKED(UPlayerData, Health); TEXT("Health"); UE_LOG(LogTemp, Warning, TEXT("Test"));'
        roles = {(token, value) for _, token, value in MarkupCppLexer().get_tokens_unprocessed(source)}
        for name in ('GET_MEMBER_NAME_CHECKED', 'TEXT', 'UE_LOG'):
            self.assertIn((Name.Constant, name), roles)

    def test_cpp_sdk_types_macros_and_calls(self):
        source = 'MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 100)\nauto p = MarkupUI::MakeMarkupShared<PlayerObject>();\np->SetHealth(80);'
        tokens = list(MarkupCppLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for pair in ((Name.Constant, 'MARKUPUI_PROPERTY'), (Name.Class, 'PlayerObject'),
                     (Name.Function, 'MakeMarkupShared'), (Name.Function, 'SetHealth')):
            self.assertIn(pair, roles)

    def test_csharp_fields_properties_and_events(self):
        source = 'public class PlayerObject : INotifyPropertyChanged { private int _health; public int Health { get { return _health; } } }'
        tokens = list(MarkupCSharpLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        roles = {(token, value) for _, token, value in tokens}
        for pair in ((Name.Class, 'INotifyPropertyChanged'),
                     (Name.Variable.Instance, '_health'), (Name.Property, 'Health')):
            self.assertIn(pair, roles)

    def test_csharp_weak_reference_type(self):
        source = 'private WeakReference<OwnerObject> _weaponOwner;\npublic System.WeakReference<OwnerObject> WeaponOwner { get; set; }\nvar owner = new WeakReference<OwnerObject>(target);'
        tokens = list(MarkupCSharpLexer().get_tokens_unprocessed(source))
        self.assertEqual(''.join(value for _, _, value in tokens), source)
        references = [(token, value) for _, token, value in tokens if value == 'WeakReference']
        self.assertEqual(references, [(Name.Class, 'WeakReference')] * 3)

    def test_comments_and_strings_keep_original_roles(self):
        for lexer in (MarkupCppLexer(), MarkupCSharpLexer()):
            tokens = list(lexer.get_tokens_unprocessed('// MARKUPUI_PROPERTY PlayerObject\n"PlayerObject SetHealth()"'))
            self.assertFalse(any(token in Name for _, token, _ in tokens))

    def test_rendering_survives_unavailable_plugin_discovery_and_repeated_instances(self):
        config = {"pymdownx.highlight": {
            "pygments_lang_class": True,
            "extend_pygments_lang": [
                {"name": "cpp", "lang": "markupui-cpp"},
                {"name": "csharp", "lang": "markupui-csharp"},
                {"name": "html", "lang": "markupui"},
            ],
        }}
        samples = [
            ('cpp', 'MARKUPUI_PROPERTY(PlayerObject, int, Health, 100)', 'class="no"'),
            ('csharp', 'public class PlayerObject : INotifyPropertyChanged {}', 'class="nc"'),
            ('html', '<p @if="{IsReady}">Ready</p>', 'class="nd"'),
        ]
        with patch('pygments.lexers.find_plugin_lexers', return_value=iter(())):
            for _ in range(3):
                md = Markdown(extensions=['markupui_highlighter', 'pymdownx.highlight', 'pymdownx.superfences'], extension_configs=config)
                for language, source, token in samples:
                    rendered = md.reset().convert('```' + language + '\n' + source + '\n```')
                    self.assertIn(token, rendered)
                    self.assertNotIn('language-text', rendered)


if __name__ == "__main__":
    unittest.main()
