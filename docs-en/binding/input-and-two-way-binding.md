---
icon: bootstrap/input-cursor-text
---

# Input and Two-Way Binding

data context , . , . ,  data context.

The examples in this chapter use the writable properties of observable objects. For definitions of objects and methods of notifying, see [Data Context](../concepts/data-context.md). For details on the range of types, see [Data Types](data-types.md).

## Input Value and Binding Target

| HTML Element | Binding Target | Values in the Data Context | Default mode |
| --- | --- | --- | --- |
| `input`, `textarea` | `@value` | String or convertible numerical value | `twoWay` |
| `input type="checkbox"` | `@checked` | Boolean value | `twoWay` |
| Single-selection `select` | `@value` | Scalar value corresponding to the option value | `twoWay` |
| Multiple-selection `select` | `@values`, or `multiple` in conjunction with `@value` | Scalar Array | `twoWay` |
| `option` | `@value` | The value of the current option | `oneWay` |

`@value` is used to read and set the current input value of the control. `@checked` is used to read and set the actual checked status. `@checked` is used for checkboxes and radio buttons. In XHTML, it is written as `mk:checked`. Using `@value` for these two types of controls will result in a template compilation error. The ordinary HTML `value` attribute can still be used to declare form values.

!!! note "Two-way binding requires writable properties"
    The path must be able to locate writable business properties or writable collection items. The control must also provide corresponding input behaviors. Calculated values like `Price * Quantity` and `Name ?? 'Guest'` cannot be written back directly. Setting `twoWay` will not automatically derive the business properties.

## Text input

### Single-line and multi-line text

Bind the string property `Name` to a single-line input box, and bind `Description` to a text field:

```html
<label>
  Name
  <input type="text" @value="{Name}">
</label>

<label>
  Description
  <textarea @value="{Description}"></textarea>
</label>
```

For the input control, use `twoWay` as the `value` setting by default. There is no need to declare the mode repeatedly. Both controls read and write `Name` and `Description` from the current data context.

The same property can be used for both editing and display purposes:

```html
<input @value="{Name}">
<p>Player: {{ Name }}</p>
```

After the user edits the input box, the setter updates `Name` and sends a property notification. The text below is updated accordingly. Writing data to the property and notifying other bindings are two separate steps. The property setter should maintain the correct notification logic.

### Design-time placeholder values

Static text can be provided for design-time preview, while runtime uses the bound values:

```html
<input value="Player name" @value="{Name}">
<textarea @value="{Description}">Character description</textarea>
```

Static content is not used as part of the business data initialization process. When initial names or descriptions are required, they should be set as initial values within the observable objects.

### Numerical input

The input field can be bound to integer or floating-point properties. For example, the integer property `Health`:

```html
<input type="number" @value="{Health}">
```

When displayed, the numerical values are converted into text. When written back, the text input is converted according to the actual type of `Health`, and its range is checked. The `type="number"` attribute in HTML does not change the type of the business property, nor can it replace the validation when writing back the value.

!!! warning "Invalid inputs will not become valid values."
    Empty texts, numbers that cannot be fully parsed, out-of-bounds values, or content that does not match the target type will cause the write-back to fail, and the original attribute value will be retained. For example, an integer attribute cannot receive `12.5`, and a signed-unsigned attribute cannot receive negative numbers. The binding will not automatically replace failed inputs with `0`, nor will it automatically generate error messages.

When units, special number formats, or other business conversions are required, the application should provide appropriate converters and inverse conversions. Do not write the display text with units directly into the numerical attribute.

## Checked status

Checkboxes use `@checked` to bind boolean properties:

```html
<label>
  <input type="checkbox" @checked="{IsReady}">
  Ready
</label>
```

When `IsReady` is `true`, the checkbox is checked. When it is `false`, the checkbox is unchecked. After the user switches the check state, the boolean value is written back to `IsReady`.

Do not use `@value` to indicate whether a checkbox is checked, and do not use strings `'true'` or `'false'` as boolean properties.

## Single-choice options

For single-select `select` options, use `@value` to bind the values of the selected options:

```html
<select @value="{Difficulty}">
  <option value="easy">Easy</option>
  <option value="normal">Normal</option>
  <option value="hard">Hard</option>
</select>
```

When `Difficulty` is `normal`, **Normal** is selected. After the user selects **Hard**, the value `hard` is written back, but this does not result in the text `Hard` being displayed, nor does it affect the index of the option.

Option values can also be converted into numerical values for business properties:

```html
<select @value="{QualityLevel}">
  <option value="1">Low</option>
  <option value="2">Medium</option>
  <option value="3">High</option>
</select>
```

If `QualityLevel` is an integer property, when **High** is selected, the value `3` should be written back.

### Options generated from the collection

`select` supports binding options through `@for`. It can be used for single or multiple selections. `@for` determines the available options, while `@value` or `@values` determine the currently selected value. Both are bound to their respective options.

Assume that the object items of `Difficulties` contain `Id` and `Name`. Options can be generated through collection binding:

```html
<select @value="{Difficulty}" @for="{Difficulties}">
  <option @value="{Id}">{{ Name }}</option>
</select>
```

The `Difficulty` of `select` is read from the outer data context. The `Id` and `Name` of each `option` are read from the current collection item. The `@value` of `option` provides the option value, but it is not responsible for writing the selected result back to the collection item.

The bound property value takes precedence over the static `selected`. If the property is empty or there is no corresponding option, it should not be assumed that the static selected items will be automatically restored. The application should provide valid initial values that match the options.

## Multiple selections

Use `@values` to bind the multiple selection results to a scalar Array:

```html
<select @values="{SelectedTags}">
  <option value="fire">Fire</option>
  <option value="ice">Ice</option>
  <option value="wind">Wind</option>
</select>
```

`SelectedTags` is a string array or list property. It contains the items selected when `fire` and `wind` are selected. After the user changes the selection, write back all the currently selected values.

You can also explicitly declare `multiple` and use `@value`:

```html
<select multiple @value="{SelectedTags}">
  <option value="fire">Fire</option>
  <option value="ice">Ice</option>
  <option value="wind">Wind</option>
</select>
```

Both methods have the same meaning. `@values` enables multiple selections, eliminating the need to specify `multiple` again.

Multiple selections can also generate options using `@for`. Suppose the items in `Tags` contain `Id` and `Name`:

```html
<select @values="{SelectedTags}" @for="{Tags}">
  <option @value="{Id}">{{ Name }}</option>
</select>
```

`Tags` provides options, and `SelectedTags` stores the selected `Id`. The `Id` and `Name` within the loop belong to the current tag object, while `SelectedTags` is retrieved from the outer data context. Any changes to the collection or option properties require corresponding notifications. For details, see [Collection Binding](collection-binding.md).

!!! note "The multiple selections are written back to the entire array."
    The multiple-selection results are arranged in a new array according to the options, not in the order in which the user clicks, nor is it a modification of the original set item by item. Therefore, the property that receives the selection results must allow for overall assignment. It is not possible to use a single string, Map, Set, or object array to receive the multiple-selection results. Also, do not declare both `@value` and `@values` on the same element.

The numerical array converts all selected values according to the element type. If any of the options conversion fails, the successfully converted parts of the results will not be written back to the original property.

## Binding mode

When entering the target, it defaults to using `twoWay`. You can change it to other modes as needed:

| Mode | The behavior of the target when entering data |
| --- | --- |
| `twoWay` | Read the data context and write it back when entering data |
| `oneWay` | Update the control from the data context, without writing back the user's modifications. |
| `oneTime` | Read the value during initialization. It does not continuously track changes in properties, nor does it write back the values. |
| `oneWayToSource` | Write the control value back to the data context. The control is not updated based on properties. |

For example, only allow the data context to update the input field:

```html
<input @value="{Name, mode=oneWay}">
```

`oneWay` only restricts the binding direction. It does not prevent the control from receiving keyboard or mouse inputs. When read-only or interactive operations need to be disabled, use the settings supported by the control.

## Timing of submission

`mode` determines the update direction, and `update` determines when user inputs are written back. The timing of submission is meaningful only for the write-back directions of `twoWay` and `oneWayToSource`. It does not delay the normal update of the data context to the control.

The submission timing can be explicitly specified through `update`:

1. **`update=input`**: The submission occurs when the value changes during editing, or when the control generates an `input` event. For example, changing the text from `A` to `AB` will trigger an input change. Operations like deletion or pasting can also trigger this event. This indicates that the value has been edited, but it does not mean that the user has completed the editing process.
2. **`update=change`**: The submission occurs when the user makes an actual change, and the control generates a `change` event. For example, switching between options or checking checkboxes will trigger a new state. Text boxes usually generate this event after the editing process is completed and the focus is lost, and the value has indeed changed compared to the last submission. This emphasizes the change in value after confirmation, and it does not equate to all focus loss operations.
3. **`update=blur`**: The submission occurs when the control loses focus, and the existing value to be written back is submitted. This event is triggered by the change in focus, and it does not require the control to generate a `change` event first. Only when the focus is lost and there is no value to be written back, will new data be generated.
4. **`update=explicit`**: This does not automatically write back the value due to `input`, `change`, or `blur`. The edited value remains in a state that is ready to be submitted until it is explicitly submitted through a valid write-back mechanism.

!!! note "Input is the input event, Update is the binding option"
    `input` describes how the value within the control changes; `update` determines when the value is written back to the data context. The meaning of `update=input` is to choose the `input` event as the submission timing, rather than triggering an additional event called `update`.

    `input` Not equal to "pressing a key once". The text changes from `A` to `AB` Reverting, deletion, or pasting can all lead to this situation. `input` It can also occur during the Chinese input method group typing process. Therefore, it cannot be considered as completing a text input every time. `input` The platform determines how to handle the input method group typing and when it is allowed to be reverted, based on its input access rules.

    Even if the text box generates `input`, the default `update=blur` does not immediately write back the value. Instead, it waits for the focus to be lost. Only when `update=input` is explicitly set does the value change in response to input.

When `update` is omitted, the default submission times for each input element are as follows:

| HTML Element | Target property | Default submission time |
| --- | --- | --- |
| `<input type="text">` (including omitted `type`) | `@value` | `blur` |
| `<input type="search">` | `@value` | `blur` |
| `<input type="email">` | `@value` | `blur` |
| `<input type="url">` | `@value` | `blur` |
| `<input type="tel">` | `@value` | `blur` |
| `<input type="password">` | `@value` | `blur` |
| `<input type="number">` | `@value` | `blur` |
| `<textarea>` | `@value` | `blur` |
| `<input type="checkbox">` | `@checked` | `change` |
| `<input type="radio">` | `@checked` | `change` |
| `<input type="range">` | `@value` | `change` |
| `<input type="color">` | `@value` | `change` |
| `<input type="date">` | `@value` | `change` |
| `<input type="datetime-local">` | `@value` | `change` |
| `<input type="month">` | `@value` | `change` |
| `<input type="week">` | `@value` | `change` |
| `<input type="time">` | `@value` | `change` |
| `<input type="file">` | `@value` | `change` |
| `<select>` | `@value` | `change` |
| `<select multiple>` | `@value` | `change` |
| `<select>` | `@values` | `change` |

The above lists the default submission rules of the SDK by element type. Whether special controls such as color, date, and file selection are available depends on the actual support of the platform plugins. `@value` does not refer to providing the browser's file object or upload interface.

Unidirectional binding does not write back to the data context. The `update` method does not change the binding direction.

### Default submission

```html
<input @value="{Name}">
```

Text input fields write back to `Name` when they lose focus. If it needs to be updated as the input is entered, the `input` property should be explicitly set:

```html
<input @value="{Name, update=input}">
```

### Submission when losing focus

```html
<input @value="{Name, update=blur}">
```

During editing, the control can display content that has not been submitted yet. This content is written back to `Name` after leaving the control. Alternatively, the expansion method can be used:

```html
<input @value="{Name}" @value.update="blur">
```

Multiple targets use their own option names, such as `@values.update="blur"`.

### Explicit submission

```html
<input @value="{Name, update=explicit}">
```

At this point, the input will not be automatically written back. Simply adding buttons, triggering the HTML `submit` command, or binding to the `@onclick` command does not mean that an explicit submission has been implemented. The application needs to provide an actual mechanism for writing back the data. Whether to provide such mechanisms and how to call them depends on the capabilities of the plugins available on each platform.

!!! warning "Do not rely on commands to implicitly submit inputs."
    Writing back inputs and issuing event commands are different operations. Commands do not guarantee that all controls will be automatically submitted before execution, and they should not be used to replace the `update=explicit` method of writing back data. If the business operations require reading the latest values, it is necessary to clearly configure the timing and order of submission.

## Nested properties and collection items

Two-way binding can also be used to target the writable properties of nested objects and collection items:

```html
<input @value="{Weapon.Name}">
<input @value="{Items[SelectedIndex].Name}">
```

The objects, arrays, or Map keys in the path must be valid. After the dynamic index or context changes, subsequent inputs will be directed to the currently parsed properties, and the old objects will no longer be updated.

Properties of editable object items during iteration:

```html
<ul @for="{Items}">
  <li><input @value="{Name}"></li>
</ul>
```

Scalar Array items can be accessed using the aliases `@this` or `@item-as`. The collection itself must support writing at the corresponding positions.

```html
<ul @for="{Numbers}">
  <li><input @value="{@this}"></li>
</ul>
```

`@index`, `@key`, and `@items` are loop-related information and cannot be written back as editable fields. Sets also do not provide the ability to assign values using subscripts.

## The range of platform inputs is supported

The binding syntax is provided by the SDK. Focus, keyboard, mouse, input methods, and control input events are handled by the platform. The statements in this document do not represent that all HTML input types or browser controls are supported. For specific input types, input methods, and focus restrictions, please refer to the documentation of each platform.

When the interface can display initial values but does not update after editing, check the following:

1. Whether the current data context and property path are correct.
2. Whether the property is writable, and whether the input value can be converted to the target type.
3. Whether the mode allows write-back, and whether the submission timing is met.
4. Whether the property setter sends notifications to update other bindings.
5. Whether the platform passes focus and input events to the page, and whether there are any conversion or binding errors in the logs.
