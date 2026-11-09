---
icon: bootstrap/code-slash
---

# Markup and Binding Syntax

Markup UI organizes the interface using HTML elements, and binds using text interpolation and template properties. For detailed rules of expressions, see [Binding Syntax](../binding/binding-syntax.md).

## Instructions and prefixes

Template properties support equivalent `@` and `mk:` prefixes:

```html
<span @text="{Name}"></span>
<span mk:text="{Name}"></span>
```

When `Name` is `Alice`, both outputs are the same:

```html
<span>Alice</span>
```

The two prefixes can be used interchangeably, but the same target or option cannot be declared twice. `@this`, `@item`, and aliases in expressions still use `@`, and are not replaced by `mk:`. For XML specification, see [XHTML Support](../binding/xhtml-support.md).

| Markup | Example | Function |
| --- | --- | --- |
| `@context` | `@context="player"` | Using the named context registered in the application |
| `@context` | `@context="{Child}"` | Using the `Child` property of the current context |
| `@as` | `@as="page"` | Creating `@page` aliases for the current context after inheritance or switching, which can be used independently |
| `@if` | `@if="{IsReady}"` | Generating the current branch when the conditions are met |
| `@else-if` | `@else-if="{IsLoading}"` | Checking the conditions when the previous branch is not hit |
| `@else` | `@else` | When none of the previous branches are hit, generate content. |
| `@for` | `@for="{Items}"` | Repeat the generation of sub-content for the current container based on the collection items. |
| `@item-as` | `@item-as="item"` | Create an `@item` alias for the current collection element. |
| `@items-as` | `@items-as="items"` | Create a `@items` alias for the currently traversed collection. |

`@else-if` and `@else` must be adjacent to the previous branch. Only blanks and comments are allowed between them. The branch chain starts with `@if`, and `@else` is located at the end. `@item-as` and `@items-as` must be associated with `@for` of the same element. The `@as` on the loop container indicates the container context, not the collection element.


## Bind the target

| Markup | Example | Explanation. |
| --- | --- | --- |
| `{{ ... }}` | `{{ Name }}` | Insert the result into the text, allowing it to be mixed with static text. |
| `@text` | `@text="{Name}"` | Replace the text within elements. Placeholder text can be used for preview during design. |
| `@html` | `@html="{Content}"` | Use the result to generate dynamic HTML content. |
| `@value` | `@value="{Name}"` | Used for `input`, `textarea`, `select`, and `option` elements. |
| `@values` | `@values="{SelectedValues}"` | Used for multiple-selection in `select` elements. Cannot be declared simultaneously with `@value`. |
| `@checked` | `@checked="{IsEnabled}"` | Bind the checked state of `input` elements. |
| `@disabled` | `@disabled="{IsBusy}"` | Set the disabled state. |
| `@hidden` | `@hidden="{IsHidden}"` | Set the hidden state |
| `@property-name` | `@src="{AvatarPath}"` | Set the supported properties |
| `@style.property-name` | `@style.opacity="{Opacity}"` | Set the supported CSS property values |

The supported common HTML properties are as follows. The support for these properties does not equal the full browser behavior supported by the platform for those properties.

```text
title id class name lang dir role tabindex accesskey contenteditable
draggable spellcheck src srcset sizes alt href target rel download type
placeholder autocomplete inputmode min max step pattern minlength maxlength
size rows cols form action method enctype accept width height colspan rowspan scope
```

Markup UI also supports `data-*` and `aria-*` attributes with nonempty suffixes. Use `@style.property-name` for styles. Available style targets depend on the CSS properties supported by Markup UI.

!!! warning "Content targets and template content"
    `@text` and `@html` will take over the content of elements. It is not recommended to declare both of them on the same element, or to manage the same content using `@for` at the same time. `template` is a transparent container used for structural instructions and corresponding aliases. It does not accept ordinary properties, styles, or event bindings.


## Binding options

Options can be placed within the binding or expanded as attributes of the same element. Both approaches are equivalent.

```html
<input @value="{Name, mode=twoWay, update=blur}">
<input @value="{Name}" @value.mode="twoWay" @value.update="blur">
```

| Options | Values | Purposes |
| --- | --- | --- |
| `mode` | `oneWay`, `twoWay`, `oneTime`, `oneWayToSource` | Specify the update direction |
| `update` | `input`, `change`, `blur`, `explicit` | Determine the timing for input rewrite |
| `converter` | Apply the registered converter name | Convert binding values |
| `converter.parameter` | Individual expressions | Provide parameters to the converter |

Input properties are typically set to `twoWay`. The `value` of display targets and `option` is set to `oneWay`. Text and number input fields, `textarea` are set to `blur` by default. Checkboxes, radio buttons, select boxes, sliders, etc. are set to `change` by default. For the complete rules, see [Input and Two-Way Binding](../binding/input-and-two-way-binding.md).

Converter parameters should be placed within `converter`, or in expanded form:

```html
<!-- Currency is a converter registered by the application. -->
<span @text="{Price, converter={Currency, parameter={'USD'}}}"></span>
<span @text="{Price}" @text.converter="Currency" @text.converter.parameter="'USD'"></span>
```

The same option for the same target can only be declared once. The expanded option must have a corresponding main binding. There are no independent  or  directives. Text interpolation is not filled in for the binding options. `@mode`, `@update` Or `@converter` Instructions. Text interpolation `{{ ... }}` Do not fill in the binding options.

## Events and commands

Events bind commands from the data context, with parameters provided through `parameter`:

```html
<button @onclick="{Save}">Save</button>
<button @onclick="{Move, parameter={@this, TargetIndex}}">Move</button>
```

| Events | Available options |
| --- | --- |
| `@onclick`, `@onpointerdown`, `@onpointerup` | `parameter`, `button`, `modifiers` |
| `@onkeydown`, `@onkeyup` | `parameter`, `key`, `modifiers` |
| `@oninput`, `@onchange`, `@onsubmit`, `@onfocus`, `@onblur` | `parameter` |

- **`parameter`:** Command parameters, which can be `{Name}` or multiple expressions `{Name, Count}`. It can also be expanded to `@onclick.parameter`.
- **`key`** Static logical button names, for example `'Enter'`.
- **`button`**: `Left`, `Middle`, `Right`, `Back`, `Forward` Or `none`.
- **`modifiers`**: `Control`, `Shift`, `Alt`, `Windows`, `Meta` The combination of, for example `Control+Shift`. `none` Indicates no filtering.

Events do not use `mode`, `update`, or `converter`. The command path is written as `{Save}`, and `{Save()}` is not used. When the same event triggers both input rewriting and command execution, rewriting occurs first, followed by command execution. The order of property declarations does not affect the result. Events do not force the submission of inputs that have not yet reached the time of rewriting.

For the complete rules of events, see [Events and Commands](../binding/events-and-commands.md).

## Usage restrictions

- Expressions do not execute JavaScript. Function calls, assignments, auto-increment, ternary operations, optional chaining, array or object literals are not supported.
- Two-way binding requires a writable path. Calculated results like `Price * Quantity` cannot be written back directly.
- Properties, subscripts, and keys must be valid. Simply adding the binding syntax does not automatically create data objects, properties, or collection items.
- Changes in data require corresponding notifications for properties or collections. Modifying data without notifying the system cannot ensure proper interface updates.
- Only the listed template targets and events are supported. Assigning `@` to any HTML property does not mean it is available.
- Template property prefixes and XML format are two different things. Using `mk:` does not automatically make the entire document XML-compliant.

Data context and aliases can be found in [Data Context](../concepts/data-context.md). Structural instructions can be found in [Collection Binding](../binding/collection-binding.md) and [Conditional Binding](../binding/conditions-and-lists.md).

## Expression quick reference

| Markup | Meaning | Example |
| --- | --- | --- |
| `@context` | Select the data context or switch the context using an expression | `#!html <div @context="{Child}"></div>` |
| `@as` | Create an alias for the current data context | `#!html <div @as="page"></div>` |
| `@if` | Conditional branching | `#!html <div @if="{IsReady}"></div>` |
| `@else-if` | Subsequent conditional branches | `#!html <div><p @if="{IsReady}">Ready</p><p @else-if="{IsLoading}">Loading</p></div>` |
| `@else` | Backup branch | `#!html <div><p @if="{IsReady}">Ready</p><p @else>Waiting</p></div>` |
| `@for` | Repeating container's sub-content based on collection items | `#!html <ul @for="{Items}"><li>{{ Name }}</li></ul>` |
| `@item-as` | Create aliases for set elements | `#!html <ul @for="{Items}" @item-as="item"><li>{{ @item.Name }}</li></ul>` |
| `@items-as` | Create aliases for cyclic sets | `#!html <ul @for="{Items}" @items-as="list"><li>{{ @list.Count }}</li></ul>` |
| `@text` | Set element text | `#!html <span @text="{Name}"></span>` |
| `@html` | Set dynamic HTML content | `#!html <div @html="{Content}"></div>` |
| `@value` | Bind single-value inputs | `#!html <input @value="{Name}">` |
| `@values` | Bind multiple-select values via select controls | `#!html <select multiple @values="{SelectedValues}"><option value="a">A</option></select>` |
| `@checked` | Bind check box states | `#!html <input type="checkbox" @checked="{IsReady}">` |
| `@disabled` | Bind Disabled State | `#!html <button @disabled="{IsBusy}"></button>` |
| `@hidden` | Bind Hidden State | `#!html <div @hidden="{IsHidden}"></div>` |
| `mode` | Bind Direction Options | `#!html <input @value="{Name, mode=twoWay}">` |
| `update` | Rewrite Timing Options | `#!html <input @value="{Name, update=blur}">` |
| `converter` | Converter Options | `#!html <span @text="{Price, converter=Currency}"></span>` |
| `converter.parameter` | Converter Parameters | `#!html <span @text="{Price}" @text.converter="Currency" @text.converter.parameter="'USD'"></span>` |
| `parameter` | Event Command Parameters | `#!html <button @onclick="{Save, parameter={Name}}"></button>` |
| `key` | Keyboard events: Key filtering | `#!html <input @onkeyup="{Save, key='Enter'}">` |
| `button` | Mouse events: Key filtering | `#!html <button @onclick="{Save, button=Left}"></button>` |
| `modifiers` | Modifier key filtering for events | `#!html <input @onkeydown="{Save, modifiers=Control}">` |
| `@onclick` | Execute commands when clicking or activating | `#!html <button @onclick="{Save}"></button>` |
| `@oninput` | Execute commands when the input value changes | `#!html <input @oninput="{Save}">` |
| `@onchange` | Execute commands when there is an actual change in submission | `#!html <input @onchange="{Save}">` |
| `@onsubmit` | Execute commands when the form is submitted | `#!html <form @onsubmit="{Save}"></form>` |
| `@onfocus` | Execute the command when the focus is obtained | `#!html <input @onfocus="{Save}">` |
| `@onblur` | Execute the command when the focus is lost | `#!html <input @onblur="{Save}">` |
| `@onkeydown` | Execute the command when the button is pressed | `#!html <input @onkeydown="{Save}">` |
| `@onkeyup` | Execute the command when the button is released | `#!html <input @onkeyup="{Save}">` |
| `@onpointerdown` | Execute the command when the pointer is pressed | `#!html <button @onpointerdown="{Save}"></button>` |
| `@onpointerup` | Execute the command when the pointer is released | `#!html <button @onpointerup="{Save}"></button>` |
| `{{` | Text interpolation begins | `#!html <p>{{ Name }}</p>` |
| `}}` | Text interpolation ends | `#!html <p>{{ Name }}</p>` |
| `{` | Binding expression or parameter expression begins | `#!html <span @text="{Name}"></span>` |
| `}` | Binding expression or parameter expression ends | `#!html <span @text="{Name}"></span>` |
| `@this` | Current data context | `#!html <p>{{ @this.Name }}</p>` |
| `@item` | Current set element. In a Map, it represents the current value | `#!html <ul @for="{Items}"><li>{{ @item.Name }}</li></ul>` |
| `@index` | Current iteration index of the loop, starting from `0` | `#!html <ul @for="{Items}"><li>{{ @index }}</li></ul>` |
| `@key` | The key of the current item in the Map | `#!html <ul @for="{Stats}"><li>{{ @key }}</li></ul>` |
| `@items` | The collection being traversed in the current loop | `#!html <ul @for="{Items}"><li>{{ @items.Count }}</li></ul>` |
| `true` | Boolean true value | `#!html <span @if="{true}"></span>` |
| `false` | Boolean false value | `#!html <span @disabled="{false}"></span>` |
| `null` | Null value | `#!html <span @if="{Weapon != null}"></span>` |
| `+` | Addition, string concatenation. Unary form represents the positive sign | `#!html <p>{{ Price + Tax }}</p>` |
| `-` | Subtraction. Unary form represents taking the negative | `#!html <p>{{ Health - Damage }}</p>` |
| `*` | Multiplication | `#!html <p>{{ Price * Quantity }}</p>` |
| `/` | Division | `#!html <p>{{ Total / Count }}</p>` |
| `%` | Modulation | `#!html <p>{{ Index % 2 }}</p>` |
| `==` | Equal to | `#!html <span @if="{Health == 100}"></span>` |
| `!=` | Not equal to | `#!html <span @if="{Health != 0}"></span>` |
| `#!html <` | Less than | `#!html <span @if="{Health < 100}"></span>` |
| `#!html <=` | Less than or equal to | `#!html <span @if="{Health <= 100}"></span>` |
| `>` | Greater than | `#!html <span @if="{Health > 0}"></span>` |
| `>=` | Greater than or equal to | `#!html <span @if="{Health >= 0}"></span>` |
| `!` | Logical negation | `#!html <span @if="{!IsDead}"></span>` |
| `&&` | Logical AND, supports short-circuit evaluation | `#!html <span @if="{IsReady && IsVisible}"></span>` |
| `||` | Logical OR, supports short-circuit evaluation | `#!html <span @if="{IsReady || IsLoading}"></span>` |
| `??` | Null value merging: If the left side is non-empty, return the left side. Otherwise, evaluate the right side | `#!html <p>{{ Name ?? 'Guest' }}</p>` |
| `(` | Start of operation grouping | `#!html <p>{{ (Price + Tax) * Quantity }}</p>` |
| `)` | End of operation grouping | `#!html <p>{{ (Price + Tax) * Quantity }}</p>` |
| `.` | Property access | `#!html <p>{{ Weapon.Name }}</p>` |
| `[` | Start of subscript or key access | `#!html <p>{{ Items[0].Name }}</p>` |
| `]` | End of subscript or key access | `#!html <p>{{ Items[0].Name }}</p>` |
| `:lt:` | `#!html <` | `#!html <span @if="{Health :lt: 100}"></span>` |
| `:le:` | `#!html <=` | `#!html <span @if="{Health :le: 100}"></span>` |
| `:gt:` | `>` | `#!html <span @if="{Health :gt: 0}"></span>` |
| `:ge:` | `>=` | `#!html <span @if="{Health :ge: 0}"></span>` |
| `:and:` | `&&` | `#!html <span @if="{IsReady :and: IsVisible}"></span>` |
| `:or:` | `||` | `#!html <span @if="{IsReady :or: IsLoading}"></span>` |
| `\'` | Single quotes in the expression string | `#!html <p>{{ 'Player\'s name' }}</p>` |
| `\\` | Backslashes in the expression string | `#!html <p>{{ 'C:\\UI' }}</p>` |
| `\n` | Newlines in the expression string | `#!html <p>{{ 'Line 1\nLine 2' }}</p>` |
| `\r` | Carriage returns in the expression string | `#!html <p>{{ 'Line 1\rLine 2' }}</p>` |
| `\t` | Tabs in the expression string | `#!html <p>{{ 'Name\tHealth' }}</p>` |
| `\{{` | Outputing the literal `{{` in plain text, without starting interpolation | `#!html <p>\{{ Name }}</p>` |
