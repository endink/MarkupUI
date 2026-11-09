---
icon: bootstrap/link-45deg
---

# Data Binding Overview

Data binding establishes a connection between business data and the HTML interface. The application provides data objects, and the page specifies the properties to be read and the positions to display them. When data changes, the binding updates the interface based on notifications. For editable content, the binding also allows users to write back their input into the business object.

The binding design of Markup UI was inspired by [WPF data binding](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/data/#data-context){ target="_blank" rel="noopener noreferrer" }And it adopts the text interpolation and property directive syntax suitable for HTML. WPF documents are used to understand the design concepts, while the specific syntax and behavior are determined by Markup UI.

![The data context is updated in the HTML interface through binding, and user input is written back to the writable properties at the configured time](images/data-binding-flow.svg#light){ .diagram-light }
![The data context is updated in the HTML interface through binding, and user input is written back to the writable properties at the configured time](images/data-binding-flow.svg#dark){ .diagram-dark }

## Data Context and Binding Target

A binding can be understood from the following aspects:

- **data context**: The object that provides the business data.
- **property path**: The path from the data context to retrieve a specific value, such as `Name` or `Weapon.Name`.
- **binding target**: The text, element property, or style property on the page that receives the result.
- **binding mode**: Specifies the direction of updates between the data context and the interface.

For example, using the following object as the default data context for the document:

```yaml
PlayerObject:
  Name: "Alice"
  Health: 100
```

Binding `Name` on the page:

```html
<h1>{{ Name }}</h1>
```

The data context is `PlayerObject`, the property path is `Name`, and the target is the text within the `h1` element.

The final HTML code output:

```html
<h1>Alice</h1>
```

This HTML displays the binding results. It does not mean that the entire document needs to be regenerated and loaded every time there is an update.

## Data Context

The data context determines the starting point for finding property paths. By default, the page uses the document's default data context. You can choose a named context or a property of an object using `@context`.

```html
<!-- Use the document's default data context. -->
<p>{{ Name }}</p>

<!-- Use the context named "player". -->
<section @context="player">
  <p>{{ Name }}</p>
</section>
```

A named context needs to be registered by the application. It cannot be created simply by declaring it in HTML. For rules regarding default, named, and nested contexts, see [Data Context](../concepts/data-context.md).

## Text, properties, and styles binding

### Text binding

Text interpolation can mix fixed text with property values:

```html
<p>Player: {{ Name }}</p>
<p>Health: {{ Health }}</p>
```

You can also use `@text` to explicitly set the text content of an element:

```html
<span @text="{Name}">Player name</span>
```

The `Player name` within the element can be used as placeholder text during design, and is replaced by the binding result of `@text` during runtime. For example, when `Name` is `Alice`, the final display will be `Alice`.

- **Double brackets `{{ ... }}`**: Used for text interpolation, such as `<p>{{ Name }}</p>`.
- **Single brackets `{...}`**: Used to bind expressions in properties, for example, `<span @text="{Name}"></span>`.

### Property Binding

By adding `@` before the target property, the result of the expression can be bound to the property.

```html
<img @src="{AvatarPath}" alt="Player avatar">
<input @value="{Name}" @value.mode="twoWay">
```

`AvatarPath` provides the image path. The `value` in the input field is associated with `Name`. The image path still follows the [Resource Paths](../authoring/resource-paths.md) rules, and data binding does not change the way resources are retrieved.

### Style binding

Use `@style.property-name` Bind a single style property. For example, the data object provides `Opacity` When using a property:

```html
<div @style.opacity="{Opacity}">Player information</div>
```

Fixed appearances can still use external CSS. Only set the values that need to change with the business state as bindings. The results of the expressions should meet the requirements of the target property. It cannot be assumed that any object can be converted into valid CSS values.

## Binding mode

For input properties of interactive HTML elements, such as input boxes `value` And for checkboxes `checked` For Markup UI, two-way binding is used by default (`twoWay`. For display targets such as text, common properties, and styles, one-way binding is used by default (`oneWay`).

| Mode | Direction | Common uses |
| --- | --- | --- |
| `oneWay` | Data context → Interface | Names, status text, etc. are read-only displays. |
| `twoWay` | Data context ↔ Interface | Input values that users can modify |
| `oneTime` | Read the data context when setting the value for the first time | Displays that do not need to be updated continuously during the current binding period |
| `oneWayToSource` | Interface → Data context | Only the interface values need to be submitted to the business object. |

!!! note "Two-Way Binding"
    `twoWay` is used to support HTML elements that allow user input and their writable properties. For example, the `value` of input fields and the `checked` state of checkboxes. For elements whose bound values cannot be modified through user interaction, using `twoWay` is meaningless. Instead, `oneWay` should be used.

    When using two-way binding, the corresponding properties in the data context must be writable, and the interface target must provide the necessary input controls. Text interpolation, basic styles, and any complex expressions cannot be used as editable fields directly.

The configuration mode can be set in an expanded form:

```html
<input @value="{Name}" @value.mode="twoWay">
```

Options can also be written in the binding expression:

```html
<input @value="{Name, mode=twoWay}">
```

Different targets have their own default modes. When a clear direction is required, it should be explicitly specified. The mode only determines the update direction. It does not guarantee that the target has the ability to input data, nor does it make the read-only business properties automatically writable.

## Data update and change notifications

### Update the data context interface

After modifying the `Health` field, it is necessary to send notifications of property changes through the methods supported by the platform. When the binding receives the notification, it revalues the value and updates the corresponding target. There is no need to reload the HTML for modifying a single value.

Adding, deleting, and replacing elements in a collection also involves notifications of collection changes. It is not possible to update the list solely by assigning values to ordinary properties. For more information, see [Collection Binding](collection-binding.md).

### Users write data into the data context

`twoWay` and `oneWayToSource` involve writing data from the interface to the data context. `mode` specifies the direction, and `update` specifies the time of submission.

Omitted `update` When a text input box or text field loses focus, it is submitted by default (`blur`. Other inputs are submitted when `change` When submitting, for example, by selecting changes or checking changes. It can be explicitly set when submitting with the input. `input`.

```html
<!-- Text inputs commit on blur by default. -->
<input @value="{Name}">
```

If submission with input is required, you can explicitly specify `input`:

```html
<input
  @value="{Name}"
  @value.mode="twoWay"
  @value.update="input">
```

Even when the data context changes, the input field can still be updated. After the user makes edits, the write-back operation is performed according to the configured submission timing. For detailed default and explicit submission rules, refer to [Input and Two-Way Binding](input-and-two-way-binding.md).

Property notifications, object references, and input integration are provided by platform plugins. For more information, please refer to the documentation of each platform.

## Null values, binding errors

When the value is null, the property does not exist, the index is out of range, or the Map key does not exist, the expression can yield unavailable or null results. Such results should not be considered valid business data. The final display is determined by the binding target and expression processing rules.

This is different from syntax errors, invalid targets, or mismatched write-back types. When the page does not display the expected value, check the following in order:

1. Whether the application provides the correct data context.
2. Whether the named context and property names are consistent with the actual definitions.
3. The objects that the property path passes through exist and remain valid.
4. Have corresponding notifications been sent after the data changed?
5. Does the binding mode, target type, and write permissions meet expectations?
6. Are any binding or type errors recorded in the platform logs?

!!! tip "Do not cover up notification failures by reloading."
    When the page is loaded for the first time with data, but subsequent modifications do not update the data, it is necessary to check for change notifications first. Reloading can read the initial values again, but it cannot replace the correct data update process.

## Further reading

- [Data Types](data-types.md) Understand the support for numbers, strings, colors, vectors, matrices, and sets.
- [Basic Binding](basic-binding.md) Distinguish between scalar values and objects, access nested properties, and handle object substitutions.
- [Collection Binding](collection-binding.md) Iterate through Arrays, Maps, and Sets, display set items, and respond to set changes.
- [Binding Syntax](binding-syntax.md) Access nested data, indices, and expression results.
- [Conditional Binding](conditions-and-lists.md) According to the state, the displayed content is switched.
- [Events and Commands](events-and-commands.md) Associate buttons and other interactions with business operations.
