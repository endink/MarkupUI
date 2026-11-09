---
icon: bootstrap/filetype-xml
---

# XHTML Support

XHTML uses XML syntax to write HTML documents. The template properties of Markup UI support equivalent `@` and `mk:` prefixes. When it is necessary to ensure that the templates comply with XML writing rules, change the `@` in the property names to `mk:` instead. For basic XML rules, refer to [XML Specification](https://www.w3.org/TR/REC-xml/){ target="_blank" rel="noopener noreferrer" } and [XML Namespaces](https://www.w3.org/TR/xml-names/){ target="_blank" rel="noopener noreferrer" }.

!!! info "Writing Format and Parsing Ability"
    The current SDK supports the use of `mk:` template properties, but it will not switch to XML parsing mode, nor will it perform XHTML DTD validation. This chapter explains how to write HTML templates that comply with XML specifications. This does not mean that templates with custom properties comply with a strict XHTML DTD.

## Replace the template property prefix

Only replace the `@` at the beginning of the property name. The meaning of the property values and expressions remains unchanged:

| The original writing method | XML compatible notation |
| --- | --- |
| `@context="player"` | `mk:context="player"` |
| `@as="player"` | `mk:as="player"` |
| `@text="{Name}"` | `mk:text="{Name}"` |
| `@value="{Name}"` | `mk:value="{Name}"` |
| `@value.update="blur"` | `mk:value.update="blur"` |
| `@checked="{IsReady}"` | `mk:checked="{IsReady}"` |
| `@style.opacity="{Opacity}"` | `mk:style.opacity="{Opacity}"` |
| `@if="{IsLoading}"` | `mk:if="{IsLoading}"` |
| `@else-if="{HasError}"` | `mk:else-if="{HasError}"` |
| `@else` | `mk:else=""` |
| `@for="{Items}"` | `mk:for="{Items}"` |
| `@item-as="item"` | `mk:item-as="item"` |
| `@onclick="{Save}"` | `mk:onclick="{Save}"` |
| `@onclick.parameter="{@this}"` | `mk:onclick.parameter="{@this}"` |

The same target cannot be declared twice using two different prefixes at the same time. For example, the same element cannot be filled with both `@value` and `mk:value`.

!!! note "The @ symbol in the expression is not replaced"
    `mk:` is used only for template property names. Scopes such as `@this`, `@item`, `@index`, `@key`, `@items`, and `@player` in the expression remain unchanged. Text interpolation still uses `{{ ... }}`. `@` characters in regular text, such as email addresses, do not need to be replaced.

## Declare the namespace

XML documents require namespace declaration for attributes with prefixes. The XHTML default namespace and the `mk` prefix can be declared on the root element simultaneously.

```html
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:mk="urn:markupui:template">
  <head>
    <title>Player</title>
  </head>
  <body>
    <p mk:text="{Name}">Player name</p>
  </body>
</html>
```

The namespace URI is used for identification and does not need to be loaded over the network. `urn:markupui:template` is the identifier used in this example. It is not a download address.

The SDK recognizes the fixed `mk:` extension property prefix. It does not automatically recognize any other prefixes based on the namespace URI. Changing `mk` to `ui` will result in no automatic equivalence of template instructions, even if the URI is the same.

!!! info "Whether xmlns:mk can be omitted"
    Whether to omit `xmlns:mk` depends on the purpose:

    - **Loaded by the current SDK according to HTML**: It is possible to omit `xmlns:mk`. However, directives such as `mk:context` remain effective.
    - **Templates must comply with XML namespace standards**: When using the `mk:` property, `xmlns:mk` must be declared. It cannot be omitted. The URI is used solely for identification and is not loaded through the network.

    Therefore, there is no need to declare xmlns:mk in ordinary HTML examples. The complete XHTML template example at the end of this article retains this declaration.

## Rules for XML writing

1. **Only one root element is allowed.** The entire page uses `html`, and segments also require a root element to enclose all content.
2. **Elements must be properly closed and nested.** Use `<p>...</p>` Empty elements are written as `<input ... />`, `<br />`, `<img ... />`.
3. **Attribute values must be enclosed in quotes.** Use `class="panel"`, do not use `class=panel`.
4. **Properties must have values.** Use `checked="checked"`, `multiple="multiple"`; Branches with unconditional values are written as `mk:else=""` No naked properties need to be written `mk:else`.
5. **Names are case-sensitive.** The spelling of start and end labels must be consistent. HTML elements and ordinary attributes use lowercase letters, while business attribute names maintain the actual spelling used in the application.
6. **Reserved characters must be escaped.** The `&` in text or attribute values is written as `&amp;`, `<` is written as `&lt;`; The same type of quotes as those around the attributes should also be represented using corresponding entities.
7. **Do not use undeclared HTML naming entities.** XML predefined entities include only `amp`, `lt`, `gt`, `quot`, `apos`. For example, the non-breaking space can be written as `&#160;`, and `&nbsp;` should not be used directly.

### Character escaping in expressions

You can use operator aliases to avoid reserved characters such as `<` and `&`:

```html
<p mk:if="{Health :lt: MaxHealth :and: !IsDead}">Needs healing</p>
```

When using symbolic operators, escape them according to XML rules:

```html
<p mk:if="{Health &lt; MaxHealth &amp;&amp; !IsDead}">Needs healing</p>
```

Both notations have the same meaning. `mk:` is not used as an operator. `mk:lt` and `mk:and` are not valid alternative notations. For more operation rules, see [Binding Syntax](binding-syntax.md).

## Complete template example

The following template includes a named context, context aliases, text and property bindings, style bindings, input write-back, conditional branches, set loops, selection boxes, and command parameters. It conforms to XML well-formed rules. The actual data and commands still need to be provided by the application.

- Register the observable player object as the named context `player`.
- Provide properties such as `Name`, `AvatarPath`, `Opacity`, `IsReady`, `IsLoading`, `HasError`, `IsEmpty`, and `CanSave`.
- Each item in `Items` contains `Name` and `Quantity`. Each item in `Difficulties` contains `Id`, `Name`, and `Difficulty` stores the current option value.
- `Save` receives the player object and name, while `RemoveItem` receives the item object and the serial number of the item. The command parameters should match the application's declarations.

```html
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:mk="urn:markupui:template"
      lang="en" xml:lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Player panel</title>
    <link rel="stylesheet" href="styles/player.css" />
  </head>
  <body>
    <main mk:context="player" mk:as="player">
      <header mk:style.opacity="{Opacity}">
        <img mk:src="{AvatarPath}" alt="Player avatar" />
        <h1 mk:text="{Name}">Player name</h1>
      </header>

      <section>
        <label>
          Name
          <input type="text"
                 mk:value="{Name}"
                 mk:value.update="blur" />
        </label>
        <label>
          <input type="checkbox" mk:checked="{IsReady}" />
          Ready
        </label>
        <label>
          Difficulty
          <select mk:value="{Difficulty}" mk:for="{Difficulties}">
            <option mk:value="{Id}">{{ Name }}</option>
          </select>
        </label>
      </section>

      <p mk:if="{IsLoading}">Loading</p>
      <p mk:else-if="{HasError}">Load failed</p>
      <p mk:else-if="{IsEmpty}">No items</p>
      <section mk:else="">
        <h2>Inventory</h2>
        <p>Total: {{ Items.Count }}</p>
        <ul mk:for="{Items}" mk:item-as="item" mk:items-as="inventory">
          <li>
            <span>{{ @item.Name }} × {{ Quantity }}</span>
            <span mk:if="{Quantity :le: 0}">Out of stock</span>
            <button type="button"
                    mk:onclick="{@player.RemoveItem}"
                    mk:onclick.parameter="{@item, @index}">
              Remove
            </button>
          </li>
        </ul>
      </section>

      <button type="button"
              mk:disabled="{!CanSave}"
              mk:onclick="{Save, parameter={@this, Name}}">
        Save
      </button>
    </main>
  </body>
</html>
```
