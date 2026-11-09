---
icon: bootstrap/braces
---

# Binding Syntax

The property path reads values from the current data context. Expressions can further combine property values, literals, and operators, used to display calculation results or determine conditions. The expression re-evaluates as it depends on the data.

## Declaring expressions

- **Text interpolation** uses double parentheses `{{ ... }}`, which can be mixed with fixed texts.
- **Binding properties** use single parentheses `{...}`, such as `@text`, `@value`, and `@style.opacity`.

```html
<p>Health: {{ Health }} / {{ MaxHealth }}</p>
<span @text="{Health + Shield}"></span>
```

Assume `Health` is `80`, `MaxHealth` is `100`, and `Shield` is `20`.

Output:

```html
<p>Health: 80 / 100</p>
<span>100</span>
```

In expressions, the names of properties, scope names, and string contents are **case-sensitive**. Static text and ordinary property values in HTML are not automatically evaluated as bound expressions.

## Property path

### The current context and multi-level properties

Names without prefixes are read from the current data context. The dot symbol is used to continue accessing the properties of the previous object:

```html
<p>{{ Name }}</p>
<p>{{ Weapon.Name }}</p>
<p>{{ Weapon.Owner.Name }}</p>
```

Suppose the player's name is `Alice`, the weapon's name is `Sword`, and the weapon's owner's name is `Alice`.

Output:

```html
<p>Alice</p>
<p>Sword</p>
<p>Alice</p>
```

`Weapon.Owner.Name` reads the `Weapon` of the current object, the `Owner` of the weapon, and the owner's `Name` in sequence. `@this` clearly indicates the current data context, so `Name` has the same meaning as `@this.Name`.

After switching contexts, the path starts from the new context:

```html
<section @context="{Weapon}">
  <p>{{ Name }}</p>
  <p>{{ Owner.Name }}</p>
</section>
```

Output:

```html
<section>
  <p>Sword</p>
  <p>Alice</p>
</section>
```

Here, `Name` represents the name of the weapon. For object substitution and property notification in the path, refer to [Basic Binding](basic-binding.md).

### Fixed indices and keys

In an Array, integer indices start from `0`. In a Map, keys correspond to the actual key types.

```html
<p>{{ Items[0].Name }}</p>
<p>{{ Stats['Health'] }}</p>
<p>{{ PlayersById[1001].Name }}</p>
```

Assume the first item is named `Sword`, the `Health` key of `Stats` corresponds to `80`, and the player named `Alice` has an index number of `1001`.

Output:

```html
<p>Sword</p>
<p>80</p>
<p>Alice</p>
```

The integer keys in a Map represent the value-key pairs, not the traversal positions. String keys should be enclosed in single quotes. In `Stats['Health']`, `Health` is a fixed key, not an attribute of the data context.

!!! warning "Sets do not support subscript access."
    Paths like `Tags[0]` are invalid. Sets should read data items through loops, and subscripts should not be used to access elements in reverse order of traversal. For rules on accessing various sets, refer to [Collection Binding](collection-binding.md).

### Dynamic Index and Keys

Properties or expressions can also be used in square brackets. Data items are selected based on the current value:

```html
<p>{{ Items[SelectedIndex].Name }}</p>
<p>{{ Items[SelectedIndex + 1].Name }}</p>
<p>{{ Stats[SelectedStat] }}</p>
```

Suppose `SelectedIndex` is `0`. The names of the first two items are `Sword` and `Potion` respectively. If `SelectedStat` is `Health`, the corresponding value is `80`.

Output:

```html
<p>Sword</p>
<p>Potion</p>
<p>80</p>
```

`SelectedIndex` provides integer indices, while `SelectedStat` provides keys for the Map. When these values change, the binding needs to be updated accordingly. The path will read the selected data item again. Changes in the collection and the properties of the selected items also require corresponding notifications.

Dynamic indexes do not change the access rules of containers: Arrays do not accept string indices. The keys of a Map still need to match the actual types. Sets still do not support indexing.

### Value Converters {#value-converters}

The binding reads the last property in the path and passes its value to the converter named by `converter`. The application registers the converter. A binding can pass one extra argument, either a literal or a value read from another path in the data context.

#### No Parameter

This example reads the entire `FullName` structure and passes it to `FormatName`. With the parameter omitted, the converter receives a null parameter.

```html
<p @text="{FullName, converter=FormatName}"></p>
<input type="text" @value="{FullName, converter=FormatName, mode=twoWay, update=blur}">
```

Both the text and input display the converted name. When the input loses focus and submits an edit, `FormatName` can return a complete name structure for the binding to write back to `FullName`.

#### Literal Parameter

Both forms read the amount from `Order.Price` and pass the string `'USD'` to `Currency` as a separate parameter.

```html
<!-- Inline form -->
<span @text="{Order.Price, converter={Currency, parameter={'USD'}}}"></span>

<!-- Expanded form -->
<span @text="{Order.Price}" @text.converter="Currency" @text.converter.parameter="'USD'"></span>
```

If `Order.Price` is `10`, `Currency` can display it as `USD 10.00`. The converter defines the display format.

#### Object Parameter

Suppose the current data context exposes a `FormatOptions` object with `CurrencyCode` and `DecimalPlaces` properties. The binding passes `Order.Price` as the value and the `FormatOptions` object as a separate parameter to `PriceWithOptions`. Write the `FormatOptions` path without quotation marks.

```html
<!-- Inline form -->
<span @text="{Order.Price, converter={PriceWithOptions, parameter={FormatOptions}}}"></span>

<!-- Expanded form -->
<span @text="{Order.Price}" @text.converter="PriceWithOptions"
      @text.converter.parameter="{FormatOptions}"></span>
```

The converter can read the parameter object's properties to determine the format. For example, with `CurrencyCode` set to `"USD"` and `DecimalPlaces` set to `2`, the amount `10` can display as `USD 10.00`. See [Value Converters](value-converters.md) for definition, registration, and writeback examples.

## Literal Values

| Categories | Writing Method | Explanation |
| --- | --- | --- |
| Integers | `0`, `100`, `-10` | Decimal Integers |
| Floating-Point Numbers | `0.5`, `1.25`, `1e3`, `2.5e-2` | Decimals or Scientific Notation |
| Strings | `'Alice'`, `''` | Use single quotes; `''` represents an empty string. |
| Boolean values. | `true`, `false` | Use lowercase notation. |
| Null values. | `null` | Indicate that there is no value. |

## Character escaping

Different escaping rules apply for plain text, expression strings, and HTML attributes. The code below represents the actual content in the HTML file. If this code is written into a C++ or C# string, it must follow the string rules of the corresponding language.

### The escape characters in the expression string

The escape characters:

| The escaping process | The meaning |
| --- | --- |
| `\'` | Single quotes |
| `\\` | Backslashes |
| `\n` | Newline characters |
| `\r` | Press Enter |
| `\t` | Tab key |

```html
<p>{{ 'Player: ' + Name }}</p>
<span @text="{'Player\'s weapon: ' + Weapon.Name}"></span>
```

Assume `Name` is `Alice`, and `Weapon.Name` is `Sword`.

Output:

```html
<p>Player: Alice</p>
<span>Player's weapon: Sword</span>
```

The strings in the expression must be enclosed in single quotes. **They cannot be enclosed in double quotes or backticks.** The string content can contain double quotes. When writing double quoted HTML attributes, the double quotes in the content should be written as `&quot;`. Unicode characters can be entered directly. `\uXXXX` escape sequences are **not supported**.

```html
<span @text="{'Path: C:\\temp'}"></span>
```

Output:

```html
<span>Path: C:\temp</span>
```

Here, the backslashes within the string need to be written as `\\`. This is different from the rule of writing `C:\temp` directly as plain text.

### Handling of double quotes

The expression strings are enclosed in single quotes. The double quotes in the content can be written directly without the need for backslash escape:

```html
<!-- Name = "Alice" -->
<p>{{ '"Player: ' + Name + '"' }}</p>
```

Output:

```html
<p>"Player: Alice"</p>
```

If the expression is written within an HTML attribute enclosed in double quotes, the double quotes in the content should be written as `&quot;` to avoid ending the attribute value prematurely:

```html
<!-- Name = "Alice" -->
<span @text="{'&quot;Player: ' + Name + '&quot;'}"></span>
```

Output:

```html
<span>"Player: Alice"</span>
```

HTML first decodes the `&quot;` into double quotes, and then parses the expression. Do not use `\"` to replace HTML entities: The backslash cannot escape the end quote of an HTML attribute, and the expression string does not support `\"` escaping.

### Braces in plain text

Single `{`, `}` It is plain text and does not require escaping. Only `{{` It will start text interpolation. When it needs to be displayed as it is, add a backslash in front of it, written as `\{{`:

```html
<p>Object: { Name, Health }</p>
<p>Syntax: \{{ Name }}</p>
```

Output:

```html
<p>Object: { Name, Health }</p>
<p>Syntax: {{ Name }}</p>
```

The `}}` that has not completed the interpolation can be displayed directly, without the need for additional escaping. The `\{{` only escapes the starting marker that follows it immediately, and does not prevent the subsequent text from being recognized as interpolation.

### Mixing escaped text with interpolation

Assume `Name` is `Alice`. In the same piece of text, both the interpolation syntax and the actual bound value can be displayed simultaneously:

```html
<p>Literal: \{{ Name }}; value: {{ Name }}</p>
```

Output:

```html
<p>Literal: {{ Name }}; value: Alice</p>
```

When it is necessary to display a single curly brace outside the binding result, the literal curly braces can be separated from the interpolation:

```html
<p>{ {{ Name }} }</p>
```

Output:

```html
<p>{ Alice }</p>
```

String concatenation can also be used within the expression:

```html
<p>{{ '{' + Name + '}' }}</p>
<span @text="{'{' + Name + '}'}"></span>
```

Output:

```html
<p>{Alice}</p>
<span>{Alice}</span>
```

The curly braces in the string are text, not new binding boundaries. There is no need to write them as `\{` or `\}`.

### The backslash before the interpolation

Only the consecutive backslashes immediately following `{{` are processed according to the interpolation escape rule: one literal backslash is output for every two backslashes, and the last one is escaped as `{{`. Assume again that `Name` is `Alice`:

| HTML text content | Final display |
| --- | --- |
| `\{{ Name }}` | `{{ Name }}` |
| `\\{{ Name }}` | `\Alice` |
| `\\\{{ Name }}` | `\{{ Name }}` |

The backslashes in other plain text remain unchanged. For example,`C:\temp` It will not be interpreted as tab characters. The `\t` Backslashes in plain text `@`, `@@` Also remain unchanged and not used `@@` Indicating a single item `@`.

### HTML entities and template escapes

It is recommended to use operator aliases for characters like `<` and `&` in property expressions to avoid conflicts with HTML/XML tags:

```html
<p @if="{Health :lt: MaxHealth :and: !IsDead}">Needs healing</p>
```

Assume that `Health` is `80`, `MaxHealth` is `100`, and `IsDead` is `false`.

Output:

```html
<p>Needs healing</p>
```

!!! info "Standard HTML escape characters can be used, but this is not recommended."
    HTML entities are decoded first, and then the expressions are parsed. Therefore, this method can also be used. `&lt;`, `&amp;` Similar to standard HTML escape characters. The following notation is equivalent to operator aliases, but it is less readable. It is recommended to use this notation instead. `:lt:`, `:and:` Similar aliases.

    ```html
    <p @if="{Health &lt; MaxHealth &amp;&amp; !IsDead}">Needs healing</p>
    ```

    Equivalent built-in operator alias notations:

    ```html
    <p @if="{Health :lt: MaxHealth :and: !IsDead}">Needs healing</p>
    ```

    Using the example data above, output the following:

    ```html
    <p>Needs healing</p>
    ```

For the complete rules of XML-compatible templates, refer to [XHTML Support](xhtml-support.md).

!!! warning "Character entities do not prevent interpolation."
    `&#123;&#123; Name }}` will still be decoded as `{{ Name }}`. It will read `Name`, and the interpolation syntax will not be displayed as is. When you need to display literal interpolation markers, use `\{{ Name }}`.

### The binding results are not re-parse

The results of ordinary text and property bindings are data, and the template syntax within them will not be scanned again. For example, when the actual content of `Name` is `{{ OtherName }}`:

```html
<!-- Name = "{{ OtherName }}" -->
<p>{{ Name }}</p>
```

Output:

```html
<p>{{ OtherName }}</p>
```

In this case, `{{ OtherName }}` is literal text, and `OtherName` will not be read further. There is no need to add template escapes in the business data. Explicit dynamic HTML bindings are processed according to their own rules and do not belong to ordinary text bindings.

## Operators

Numbers, strings, colors, vectors, and matrices support different operations. The following introduces the general syntax. For the complete range of types and vector/matrix arithmetic, see [Data Types](data-types.md).

### Arithmetic Operators

| Operators | The meaning | Examples |
| --- | --- | --- |
| `+` | Addition: String concatenation occurs when either of the operands is a string. | `Health + Shield`, `'HP: ' + Health` |
| `-` | Subtraction or unary negation | `MaxHealth - Health`, `-Offset` |
| `*` | Multiplication | `Price * Quantity` |
| `/` | Division | `Health / MaxHealth` |
| `%` | Modulation | `SelectedIndex % 2` |

```html
<p>Total: {{ Price * Quantity }}</p>
<p>{{ 'HP: ' + Health + '/' + MaxHealth }}</p>
```

Assume that `Price` is `10`, `Quantity` is `3`, `Health` is `80`, and `MaxHealth` is `100`.

Output:

```html
<p>Total: 30</p>
<p>HP: 80/100</p>
```

Division can produce decimals. For example, `5 / 2` results in `2.5`. Do not rely on operators to automatically convert string representations of numbers into numerical values. The result of `'10' + 2` is the string `102`, not the numerical value `12`.

Division by zero, modulus operations, integer operations outside the supported range, and non-finite floating-point results will result in empty values and will not automatically become `0`.

### Comparison operators

| Operators | The meaning |
| --- | --- |
| `==`, `!=` | Equal to, not equal to |
| `<`, `<=` | Less than, less than or equal to |
| `>`, `>=` | Greater than, greater than or equal to |

Values are compared numerically. String values can be compared based on the order of the texts. Do not rely on implicit conversions between values of different categories. For example, `null == 0` results in `false`, and `null == ''` also results in `false`. Equality of objects does not mean comparing all their business properties individually.

### Logical operators

| Operators | The meaning |
| --- | --- |
| `!` | Logical negation |
| `&&` | Logical AND |
| `||` | Logical OR |

The logical operation returns a boolean value:

```html
<p>{{ IsReady :and: HasWeapon }}</p>
<p>{{ !IsDead }}</p>
```

Assume that `IsReady` and `HasWeapon` are both `true`, and `IsDead` is `false`.

Output:

```html
<p>true</p>
<p>true</p>
```

In the logical judgment, `null`, unavailable values, `false`, the numerical value `0`, and empty strings are considered false, while non-zero finite values and non-empty strings are considered true. Valid objects and collections are considered true, and an empty collection will not become false just because the number of items is `0`. When determining whether a collection has content, use `Items.Count :gt: 0`.

#### Short-circuit evaluation

Logical AND `&&` (`:and:`) and logical OR `||` (`:or:`) support short-circuit evaluation:

- **Logical AND**: When the left side is false, the result is already determined to be `false`, and the right side is not evaluated.
- **Logical OR**: When the left side is true, the result is already determined to be `true`, and the right side is not evaluated.

```html
<!-- The left operand is false, so division on the right is skipped. -->
<p>{{ false :and: (1 / 0) }}</p>

<!-- The left operand is true, so division on the right is skipped. -->
<p>{{ true :or: (1 / 0) }}</p>
```

Output:

```html
<p>false</p>
<p>true</p>
```

It is also possible to check the calculation conditions first, and then decide whether to continue evaluating:

```html
<!-- With Divisor = 0, the left operand is false and division is skipped. -->
<p>{{ Divisor != 0 :and: Amount / Divisor :gt: 1 }}</p>
```

Output:

```html
<p>false</p>
```

### The ?? operator

The null coalescing operator `??` is used to provide an alternative value when there is no value. It reads the value on the left side first:

- When the left side has a value, the value on the left side is returned, and the right side is not evaluated.
- When the left side is `null` or not available, the value on the right side is evaluated and returned.

`??` returns the selected value, without converting the result to a boolean value.

#### Provide a default value

```html
<p>{{ Nickname ?? 'Guest' }}</p>
<p>{{ Weapon.Owner.Name ?? 'Unknown' }}</p>
<p>{{ Items[SelectedIndex].Name ?? 'No item' }}</p>
```

Assume that `Nickname` and `Weapon` are both empty, `Items` is an empty collection, and `SelectedIndex` is `0`.

Output:

```html
<p>Guest</p>
<p>Unknown</p>
<p>No item</p>
```

When intermediate objects in the path are empty, have missing properties, exceed array subscripts, or the map keys do not exist, default values can be provided using `??`.

| Expression | Result |
| --- | --- |
| `null ?? 'Guest'` | `Guest` |
| `'' ?? 'Guest'` | Empty string |
| `0 ?? 100` | `0` |
| `false ?? true` | `false` |

`??` does not consider empty strings, `0`, or `false` as missing values, and it also cannot correct syntax errors in expressions.

#### Calculate alternative values only when necessary

When there is a value on the left side, the substitute expression on the right side will not be calculated:

```html
<!-- With Name = "Alice", keep the left operand and skip the division. -->
<p>{{ Name ?? (1 / 0) }}</p>
```

Output:

```html
<p>Alice</p>
```

The substitute value can also be read from another property:

```html
<!-- Nickname = null，Name = "Alice" -->
<p>{{ Nickname ?? Name ?? 'Guest' }}</p>
```

Output:

```html
<p>Alice</p>
```

!!! note "Different from logical OR"
    `Name || 'Guest'` returns a boolean value, not the name or `Guest`. When there is no value, a default text should be displayed. In this case, `Name ?? 'Guest'` should be used.

!!! info "It does not support merging assignments with null values."
    Markup UI support `??` However, it does not support C# syntax. `??=` Assignment operators `throw` Expression or `?.` Optional chain.`??` Only calculates the result, without modifying the original property. Cannot use the C# example directly as a template expression.

### Operator aliases

Written in HTML `<`, `>`, `&` Characters such as tags and entity escapes may be involved. The following equivalent aliases can be used:

| Operators | Aliases |
| --- | --- |
| `<` | `:lt:` |
| `<=` | `:le:` |
| `>` | `:gt:` |
| `>=` | `:ge:` |
| `&&` | `:and:` |
| `||` | `:or:` |

```html
<p>{{ Health :lt: MaxHealth :and: !IsDead }}</p>
<span @text="{Health :ge: 100}"></span>
```

Assume that `Health` is `80`, `MaxHealth` is `100`, and `IsDead` is `false`.

Output:

```html
<p>true</p>
<span>false</span>
```

The colon at both ends of the alias must be retained. The string `':and:'` is just text and is not treated as an operator.

## Priority and parentheses

The table below is arranged in order of increasing priority:

| Priority | Syntax |
| --- | --- |
| 1 | Property access `.`, index `[]` |
| 2 | Unary `!`, unary `-` |
| 3 | `*`, `/`, `%` |
| 4 | `+`, `-` |
| 5 | `<`, `<=`, `>`, `>=` |
| 6 | `==`, `!=` |
| 7 | `&&` |
| 8 | `||` |
| 9 | `??` |

Operator aliases have the same priority as the corresponding symbols. Binary operations at the same level are combined from left to right. Parentheses can clarify the calculation order:

```html
<p>{{ 1 + 2 * 3 }}</p>
<p>{{ (1 + 2) * 3 }}</p>
```

Output:

```html
<p>7</p>
<p>9</p>
```

The results within parentheses can also be accessed through properties or collection items:

```html
<p>{{ (Weapon ?? DefaultWeapon).Name }}</p>
<p>{{ (Items ?? DefaultItems)[SelectedIndex].Name }}</p>
```

Assume that `Weapon`, `Items` are both empty, `DefaultWeapon.Name` is `Sword`, the name of the first item in `DefaultItems` is `Potion`, and `SelectedIndex` is `0`.

Output:

```html
<p>Sword</p>
<p>Potion</p>
```

## Scope and aliases

### Outer data context

Through `@as` Declare an alias for the context, and use it in the expression `@alias` Access. After switching the data context, you can continue to reference the outer objects:

```html
<section @context="{@this}" @as="player">
  <div @context="{Weapon}">
    <p>Weapon: {{ Name }}</p>
    <p>Owner: {{ @player.Name }}</p>
  </div>
</section>
```

Assume the current player's name is `Alice`, and the weapon's name is `Sword`.

Output:

```html
<section>
  <div>
    <p>Weapon: Sword</p>
    <p>Owner: Alice</p>
  </div>
</section>
```

`@player` is an alias that has been declared, not an automatically recognized context name. To use the context named `player`, it is still necessary to use `@context="player"`.

### Loop scope

In the loop, you can use `@item`, `@items`, `@index`, and Map's `@key`. `@item-as` declares an alias for the current item, and `@items-as` declares an alias for the current collection:

```html
<ul @for="{Items}" @item-as="entry" @items-as="inventory">
  <li>{{ @index }}: {{ @entry.Name }} / {{ @inventory.Count }}</li>
</ul>
```

Assume `Items` contains two objects with names `Sword` and `Potion` respectively.

Output:

```html
<ul>
  <li>0: Sword / 2</li>
  <li>1: Potion / 2</li>
</ul>
```

In nested loops, the built-in names point to the inner loop. When it is necessary to retain the outer items or collections, use aliases with different names. Aliases are only valid within the scope where they are declared and their child scopes. They are not passed to adjacent areas. Inner aliases with the same name will mask the outer aliases.

## Expressions and binding options

The property path or calculation formula determines what is read, while the binding options determine how the results are passed. For example:

```html
<input @value="{Name, mode=twoWay, update=blur}">
```

Suppose `Name` is set to `Alice`. The initial output is as follows:

```html
<input value="Alice">
```

Here, `Name` is an expression, and `mode` and `update` after the comma are binding options. The expanded form corresponds to this:

```html
<input @value="{Name}" @value.mode="twoWay" @value.update="blur">
```

Output:

```html
<input value="Alice">
```

See [Value Converters](#value-converters) for inline and expanded converter options.

`mode`, `update`, converter, and event parameters are options specified for each binding. They are not general operators, and these comma-separated options cannot be directly included in `{{ ... }}`. For details on modes and update times, see [Data Binding Overview](getting-started.md).

## writable path and calculation result

Paths such as `Name`, `Weapon.Name`, `Items[SelectedIndex].Name` can point to specific properties. Whether it can be written back depends on whether the property is writable, whether the container supports the corresponding write operation, and whether the binding target supports input.

```html
<input @value="{Items[SelectedIndex].Name}">
```

Assume that `SelectedIndex` is `0`, and the corresponding item name is `Sword`. The initial output is as follows:

```html
<input value="Sword">
```

Expressions such as `Price * Quantity`, `Name ?? 'Guest'` only produce calculation results and do not correspond to business properties that can be written directly.

```html
<span @text="{Price * Quantity}"></span>
```

Assume that `Price` is `10` and `Quantity` is `3`.

Output:

```html
<span>30</span>
```

The calculation result cannot be automatically inferred back to the original property by setting `twoWay`. To edit the calculation result, the application should provide clear writable properties and business processing procedures.

## Unsupported syntax

Expressions are not JavaScript or C# scripts. The following syntax is not supported:

| Writing Method | Reason |
| --- | --- |
| `GetName()`, `Math.Round(Price)` | Function or method calls are not supported. |
| `Health = 100`, `Health += 1`, `Health++` | Assignments, compound assignments, or self-increment operations are not supported. |
| `IsReady ? 'Ready' : 'Waiting'` | Ternary conditional operators are not supported. |
| `Weapon?.Name` | Optional chaining is not supported. Missing results can be handled using normal paths and `??`. |
| `Value === 0`, `Value !== 0` | Strict equality operators are not supported. Use `==` or `!=`. |
| `[1, 2]`, `{Name: 'Alice'}` | Does not support array or object literals. |
| `A & B`, `A << 1`, `2 ** 3` | Does not support bitwise operations, shifting, or exponentiation operations. |

When formatting, complex calculations, or business operations are required, the application should provide properties, converters, or commands. Do not write scripts into the binding expression.
