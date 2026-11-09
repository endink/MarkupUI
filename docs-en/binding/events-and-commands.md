---
icon: bootstrap/lightning
---

# Events and Commands

- **Events**: Interface operations such as clicks, inputs, or changes in focus.
- **Commands**: Business operations provided by the application.

Event binding associates the events of HTML elements with commands in the data context. When an event occurs and the filtering conditions match, the parameters are read and the command is executed.

## Commands

Commands are business operations provided by the application to data binding. They consist of a name, parameter declarations, and execution logic. In C++, member functions can be registered or an `ICommand` object can be provided. In C#, command registration is configured through `BindingInfo.Commands<TModel>`.

!!! note "C++ ICommand Specification"
    When registering a C++ command through `ICommand`, the command field must use `std::shared_ptr<ICommand<TArgs...>>`.  
    For example:  
    `std::shared_ptr<MarkupUI::Binding::ICommand<int32_t, bool>>`.  
    Parameter-less command:  
    `std::shared_ptr<MarkupUI::Binding::ICommand<>>`.


### Define the command


The following code defines a `Save` command that accepts two parameters: the target health value and the confirmation status. When the confirmation status is true, the `Health` is updated to the target health value.

=== "C++ (function command)"

    Inherit from `ObservableObject`, and register the business method as a command through `RegisterCommand`:

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <markupui/binding/modeling/object_model.h>

    class PlayerObject final
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        PlayerObject()
        {
            InitializeType<PlayerObject>();
        }

        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 80)
        MARKUPUI_PROPERTY(PlayerObject, int32_t, TargetHealth, 100)
        MARKUPUI_PROPERTY(PlayerObject, bool, Confirmed, true)

        void Save(int32_t targetHealth, bool confirmed)
        {
            if (confirmed)
            {
                SetHealth(targetHealth);
            }
        }

        inline static const auto SaveCommand =
            MarkupUI::Binding::Metadata::RegisterCommand<
                PlayerObject, &PlayerObject::Save>(MARKUPUI_STR_VIEW("Save"));
    };
    ```

    Create an object:

    ```cpp
    auto player = std::make_shared<PlayerObject>();
    ```

    `Save` receives `int32_t` and `bool` parameters in the declared order.

    Register the command with the name `Save`. The `SaveCommand` saves the registered definition.

=== "C++ (ICommand)"

    Inherit from `ObservableObject`. Register the `ICommand<int32_t, bool>` member through `RegisterCommand`. Use `DelegateCommand<int32_t, bool>` to provide the execution logic:

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <markupui/binding/delegate_command.h>
    #include <markupui/binding/modeling/object_model.h>

    class PlayerObject final
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        std::shared_ptr<MarkupUI::Binding::ICommand<int32_t, bool>> SaveCommand;

        PlayerObject()
        {
            InitializeType<PlayerObject>();

            SaveCommand = std::make_shared<
                MarkupUI::Binding::DelegateCommand<int32_t, bool>>(
                [this](int32_t targetHealth, bool confirmed)
                {
                    if (confirmed)
                    {
                        SetHealth(targetHealth);
                    }
                });
        }

        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 80)
        MARKUPUI_PROPERTY(PlayerObject, int32_t, TargetHealth, 100)
        MARKUPUI_PROPERTY(PlayerObject, bool, Confirmed, true)

        inline static const auto SaveInfo =
            MarkupUI::Binding::Metadata::RegisterCommand<
                PlayerObject, &PlayerObject::SaveCommand>(MARKUPUI_STR_VIEW("Save"));
    };
    ```

    > No-argument command interface
    > ```cpp
        MarkupUI::Binding::ICommand<>
    > ```

    Create an object:

    ```cpp
    auto player = std::make_shared<PlayerObject>();
    ```

    Register the command with the name `Save`. The `SaveCommand` saves the command object, and the `SaveInfo` saves the registered definition.

    `player` is held by the application. The `PlayerObject` holds the command object through `SaveCommand`. The `this` captured by the callback does not extend the lifecycle of `PlayerObject`. If the command object needs to be saved again, it is necessary to ensure that `PlayerObject` is still valid when the callback is executed.

=== "C#"

    Use `DelegateCommand` to wrap business operations, and register commands through `BindingInfo.Commands<TModel>`:

    ```csharp
    using System.ComponentModel;
    using MarkupUI.Sdk.Binding;

    public class PlayerObject : INotifyPropertyChanged
    {
        private int _health = 80;
        private readonly int _targetHealth = 100;
        private readonly bool _confirmed = true;

        public event PropertyChangedEventHandler PropertyChanged;

        // Register commands explicitly in the static constructor.
        static PlayerObject()
        {
            BindingInfo.Commands<PlayerObject>(commands =>
            {
                commands.Register("Save", model => model.Save);
            });
        }

        public PlayerObject()
        {
            Save = new DelegateCommand<int, bool>(ExecuteSave);
        }

        public int Health
        {
            get { return _health; }
            set
            {
                if (_health != value)
                {
                    _health = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("Health"));
                }
            }
        }

        public int TargetHealth
        {
            get { return _targetHealth; }
        }

        public bool Confirmed
        {
            get { return _confirmed; }
        }

        public ICommand<int, bool> Save { get; }

        private void ExecuteSave(int targetHealth, bool confirmed)
        {
            if (confirmed)
            {
                Health = targetHealth;
            }
        }
    }
    ```

    Create an object:

    ```csharp
    var player = new PlayerObject();
    ```

    `BindingInfo.Commands<PlayerObject>` specifies the model type. You can call `commands.Register` multiple times in the configuration delegate to register different commands. `"Save"` is the registered name, and `model => model.Save` reads the command object from the current model. The type of the command parameter is derived from the interface of that object. The command must be registered in the static constructor, and the reading delegate should not capture specific model instances.

    `DelegateCommand` binds the member method `ExecuteSave`, receiving two parameters in the same order. Here, `ICommand` belongs to `MarkupUI.Sdk.Binding`, not `System.Windows.Input.ICommand`.


    ??? info "C# implements the ICommand interface"

        All C# command interfaces are located in the `MarkupUI.Sdk.Binding` namespace:

        | Number of parameters | Interface |
        | --- | --- |
        | 0 | `#!csharp ICommand` |
        | 1 | `#!csharp ICommand<T1>` |
        | 2 | `#!csharp ICommand<T1, T2>` |
        | 3 | `#!csharp ICommand<T1, T2, T3>` |
        | 4 | `#!csharp ICommand<T1, T2, T3, T4>` |
        | 5 | `#!csharp ICommand<T1, T2, T3, T4, T5>` |
        | 6 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6>` |
        | 7 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7>` |
        | 8 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7, T8>` |
        | 9 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7, T8, T9>` |
        | 10 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7, T8, T9, T10>` |

### Command parameters

#### C++ parameter types and reception forms

Current C++ strong-type command supports **0 to 10 parameters**, which can be specified through the member function signature or declared using `ICommand<TArgs...>`. Command without parameters uses `ICommand<>`. The `T` in the table represents the specific type.

| Parameter types | Supported reception forms | Description |
| --- | --- | --- |
| `bool` | `bool`, `const bool&` | Boolean values |
| `int8_t`, `uint8_t`, `int16_t`, `uint16_t`, `int32_t`, `uint32_t`, `int64_t`, `uint64_t` | `T`, `const T&` | Integers; Check and convert the range according to the target type declared in the command |
| `float`, `double` | `T`, `const T&` | Floating-point numbers |
| Enumerations | `T`, `const T&` | Only supported enumeration types |
| `String`, `StringView` | `String`, `const String&`, `StringView`, `const StringView&` | Strings |
| `Color`, `ColorF`, `Vector2`, `Vector3`, `Matrix4x4` | `T`, `const T&` | SDK structures |
| Platform Scalar[^command-platform-scalar] | `T`, `const T&` | Native scalar types supported by the platform |
| Object[^command-object] | `T*`, `const T*`, `T&`, `const T&` | Borrow the original instance |
| Array, Map, Set | `T*`, `const T*`, `T&`, `const T&` | Collections. Borrow the original instance |
| Shared objects, shared collections[^command-shared] | `T*`, `const T*`, `T&`, `const T&` | The type of the object or collection being referenced by `T` is not a shared pointer type |
| Weak objects, weak collections[^command-weak] | `T*`, `const T*`, `T&`, `const T&` | The type of the object or collection being referenced by `T`. Only received when the target is valid |
| `Null` | Original pointer | Received as `nullptr`. Reference parameters are not accepted. |

For example, shared subcollections can be received using either of the following signatures:

```cpp
void Save(MarkupUI::Binding::IArray<int32_t>* items);
void Save(const MarkupUI::Binding::IArray<int32_t>& items);
```

The following reception forms are not currently supported:

```cpp
void Save(FMyObject object);                   // Unmapped application object passed by value
void Save(ObservableArray<int32_t> items);     // Native collection passed by value
void Save(std::shared_ptr<FMyObject> object);  // The shared pointer itself
void Save(const std::shared_ptr<FMyObject>& object);
```

The `const T&` reference of the Mapper is used to store the temporary value during decoding. References to objects and collections are borrowed from the original instance. Independent shared instances can be temporarily maintained during calls, while embedded collections are still subject to the validity period of the storage. Do not save borrowed pointers or references across calls. When the weak reference target becomes invalid, no business methods are called.

C# provides the parameter-less `ICommand` and generic `ICommand<T1, ...>`, which accept 1 to 10 parameters. `DelegateCommand` provides the corresponding form. Parameters support registered Mappers and nullable types.

### Data types are compatible

Command parameters are determined by the type declared by the receiver. C++ and C# use the same number conversion rules, which apply to commands, global commands, and triggers with the `do:command` behavior in the data context.

The ten digital types supported by SDK (`Int8`, `UInt8`, `Int16`, `UInt16`, `Int32`, `UInt32`, `Int64`, `UInt64`, `Float`, `Double`) can be converted to each other. Before conversion, check the range of the target type:

| Source and Target | Conversion Rules |
| --- | --- |
| Integer → Integer | Check the upper and lower limits of the target type. Negative numbers cannot be passed to unsigned integer parameters. |
| Floating-Point Number → Integer | After rounding to zero, check the range. For example, `17.875` is converted to `17`, and `-17.875` is converted to `-17`. |
| Integer → Floating-Point Number | Allow normal rounding due to the target precision |
| Floating-Point Number → Floating-Point Number | Check the target range, allowing normal precision rounding. May round to zero in case of underflow |

Expressions are evaluated independently first, then converted to the type of command parameters. For example, the evaluation type of an integer literal `17` is `Int64`, which can still be passed to `int32_t` in C++ or `int` in C#. This rule applies only to command parameters and does not change the type rules for property writes, collection keys, or expressions themselves.

For example, if the source value is a floating-point number `17.875`, and the command declaration receives an integer parameter, the SDK will round down to zero and pass `17`.

=== "C++"

    ```cpp
    // Assume the source argument evaluates to 17.875 as a double.
    void SetAge(int32_t age)
    {
        // The SDK calls this function with age set to 17 after conversion.
    }
    ```

=== "C#"

    ```csharp
    // Assume the source argument evaluates to 17.875 as a double.
    void SetAge(int age)
    {
        // The SDK calls this function with age set to 17 after conversion.
    }
    ```

This conversion occurs before the SDK calls the command. When calling functions directly in the business code, there is no conversion of command parameters.

!!! warning "Invalid numbers will prevent the entire command from being executed."
    Conversion failures occur for values that exceed the range, are NaN, or have positive or negative infinity values. The SDK will record an error, and no clamping or reversion will occur. All parameter checks and conversions must be successful before the business function is called. Even if only one parameter fails, the entire business logic will not be executed.

Other types are still checked according to their declared types and do not participate in numerical conversions:

- Boolean values and strings are not automatically converted to numbers. For example, `true` and `'17'` cannot be used as numerical parameters.
- Colors, vectors, matrices, and objects do not participate in numerical conversions. Objects and collections also need to meet the requirements for receiving types and survival conditions.
- Types that have been registered as numerical Mappers are first converted to their mapped scalar types, and then restored to their declared types.
- Null values still follow the nullable rules of the receiving type. C++ raw pointers can accept `nullptr`, while references cannot accept null values. C# nullable types retain their null value semantics.

When the number of parameters, their types, value ranges, or object survival checks fail, the business function will not be executed. The error log will indicate the parameter number, the expected type, and the actual value type, which helps to identify incompatible parameters.

### Execution conditions

`ICommand` provides a `CanExecute()` method without parameters. Directly calling `Execute` will not automatically check the execution conditions. The caller should decide whether to execute based on the query results. `CanExecuteChanged` provides notifications of the available status locally.

## Events {#command-events}

Events are notifications sent by HTML UI elements during user interaction. For example, when a user modifies the value of a `<input>` element, the `change` event is triggered, usually when the input element loses focus.

Markup UI supports using command binding syntax in HTML to associate element events with commands. When a UI event is triggered and the filtering conditions match, and the command is allowed to be executed, the bound command is called, and the defined callback function is executed.

Usage `@event-name="{command-binding-expression}"` Bind the element event to a command through `parameter` Pass parameters in order.`mk:` Equivalent to `@` For example, `@onclick` And `mk:onclick` Equivalent to.

Suppose the `Save` command function is as follows, with three parameters: name, age, and selected status in sequence:

=== "C++"

    ```cpp
    void Save(std::string name, int32_t age, bool selected);
    ```

=== "C#"

    ```csharp
    void Save(string name, int age, bool selected);
    ```

### Syntax

Place the command name and parameter list in the same binding expression:

> `@event-name` Here, the event name is usually the same as the event names in standard HTML syntax.  
> For example:  
> `#!html <input onclick>` (This is the way JavaScript handles events in the browser)  
> Corresponding Markup UI binding syntax:  
> `#!html <input @onclick>`


```xml
<button @onclick="{Save, parameter={Name, Age, Selected}}">
    保存
</button>
```

It is also possible to use an inline method, by declaring the parameter list through the independent `@onclick.parameter` property:

```xml
<button
    @onclick="{Save}"
    @onclick.parameter="{Name, Age, Selected}">
    保存
</button>
```

Both ways of writing are equivalent. When clicked, the `Name`, `Age`, and `Selected` values are read in sequence and passed to the `Save` command.

### Binding command

After using the `PlayerObject` instance from the "Define Command" as the data context, its `Save` command can be bound:

```html
<button @onclick="{Save, parameter={TargetHealth, Confirmed}}">Save</button>
```

The corresponding non-inline way of writing:

```html
<button
    @onclick="{Save}"
    @onclick.parameter="{TargetHealth, Confirmed}">
    Save
</button>
```

### Passing command parameters

#### Parameter expressions

Passing expressions in order using `parameter={...}`

```html
<button @onclick="{Save, parameter={Name}}">Save name</button>
<button @onclick="{MoveItem, parameter={@this, TargetIndex}}">Move</button>
```

The first example passes a parameter, and the second example passes the current object and `TargetIndex` in sequence. For the inline and non-inline writing methods, see [Events](#command-events).

The parameter list can use property paths, literals, computational expressions, and scope names.

```html
<button @onclick="{Adjust, parameter={Health + 10, 'bonus', true}}">
  Apply bonus
</button>
```

Parameters are evaluated in the order they are declared after event matching and when the actual command is executed. The values are not fixed at the time of page loading. The SDK checks the number, type, and emptiness of parameters based on the command declaration. If the check fails, no business method will be called.

#### Parameters with no values and empty values

Neither of the following writing methods passes any parameters:

```html
<button @onclick="{Save}">Save</button>
```
Equivalent to
```html
<button @onclick="{Save, parameter={}}">Save</button>
```

!!! warning "An empty value parameter is not the same as a parameter with no values"
    `parameter={null}` Passing an empty value parameter is different from not passing any parameters.

### Command path and scope

The command path can access sub-objects or declared outer aliases:

```html
<button @onclick="{Settings.Save}">Save settings</button>

<section @context="player" @as="player">
  <ul @for="{Items}">
    <li>
      <span>{{ Name }}</span>
      <button @onclick="{@player.RemoveItem, parameter={@this}}">Remove</button>
    </li>
  </ul>
</section>
```

The commands within the loop locate the player object using `@player`. The parameter `@this` refers to the current item. The commands and parameters can come from different scopes.

!!! note "The command path is not a function call."
    Use `{Save}`, do not write `{Save()}` or `{Save(Name)}`. The template does not execute JavaScript; `onclick="Save()"` will not automatically become a command binding. Parameters are declared using `parameter`.

### Parameter Converters {#command-parameter-converters}

In the parameter list, each individual parameter can use nested binding expressions to declare converters. The parameters of the converters themselves are placed in their `parameter` fields. The following example demonstrates the syntax.

!!! warning "Command Parameter Converters"
    The examples below illustrate the syntax. The current version skips parameter converters when invoking commands. See [Value Converters](value-converters.md) for text display and input writeback.

Inline notation:

```xml
<button @onclick="{Save, parameter={
    {Name, converter=Trim},
    {Age, converter={ToInt, parameter={10}}},
    Selected
}}">
    保存
</button>
```

Non-inline notation:

```xml
<button
    @onclick="{Save}"
    @onclick.parameter="{
        {Name, converter=Trim},
        {Age, converter={ToInt, parameter={10}}},
        Selected
    }">
    保存
</button>
```

`converter=Trim` declares a converter for `Name`; `converter={ToInt, parameter={10}}` declares a converter for `Age`, and passes `10` to the converter. `Selected` does not have a declared converter. These converter names are only used to demonstrate the syntax and do not represent the currently available built-in implementations.

### Command execution conditions

The command path must locate a valid command within the current data context. If the command is missing or the command field is empty, the current call will be skipped, and a warning will be recorded, without affecting other bindings. If the data context or commands change later, the subsequent events can still be re-parse.

!!! note "CanExecute and control state"
    The template event queries the parameter-less `CanExecute()` method before execution. If `false` is returned, the execution is skipped. Direct calling of `Execute` does not automatically query `CanExecute()`. The current `CanExecuteChanged` only provides local notifications and does not automatically update the control state. The available state needs to be expressed through explicit property bindings.

For example, the application provides boolean properties `CanSave` and `Save` for commands:

```html
<button @disabled="{!CanSave}" @onclick="{Save}">Save</button>
```

When the `CanSave` property changes, a property notification is required. The command itself should still verify the current business state, and it cannot rely solely on the button appearance to determine whether it can be executed.

### Input write-back and command order {#command-update-order}

**Execution is triggered according to the event timing. The order of HTML properties does not affect the result. When the same event triggers both write-back and command execution, write-back is performed first, followed by command execution.**

Taking a text box as an example, when the user edits the value and the element loses its focus, and the re-entry is successful:

| Re-entry settings | `oninput` command | `onchange` command | `onblur` command |
| --- | --- | --- | --- |
| `update=input` | New value | New value | New value |
| `update=change` | <span class="text-warning">:bootstrap-exclamation-triangle: Old value</span> | New value | New value |
| `update=blur` | <span class="text-warning">:bootstrap-exclamation-triangle: Old value</span> | New value | New value |
| Omit `update` (default is `blur`) | <span class="text-warning">:bootstrap-exclamation-triangle: Old value</span> | New value | New value |
| `update=explicit` | <span class="text-warning">:bootstrap-exclamation-triangle: Old value</span> | <span class="text-warning">:bootstrap-exclamation-triangle: Old value</span> | <span class="text-warning">:bootstrap-exclamation-triangle: Old value</span> |

- The values of `@checked` in checkboxes and values in radio buttons are written back to the data context by default during `change`: They are written back first during the same `change` event, and then the `onchange` command is executed.
- Commands such as clicking or using the keyboard are executed when the respective events occur. Values that are forced to be submitted before `blur`, `change`, or explicitly submitted are not processed in advance.
- Command parameters read the data context during command execution. If the write conversion or writing fails, the actual value in the data context is read.

The behaviors of the following two methods are the same:

```html
<input @value="{Name, update=input}" @oninput="{Save, parameter={Name}}">
<input @oninput="{Save, parameter={Name}}" @value="{Name, update=input}">
```

#### Writing back to collection elements

Binding the input to a writable collection element and executing the command for the same input event:

```html
<input type="number"
  @value="{Numbers[0], mode=twoWay, update=input}"
  @oninput="{Save, parameter={Numbers[0]}}">
```

First, assign the input value to `Numbers[0]`. Then, execute `Save`. Therefore, the command parameter reads the updated `Numbers[0]`.

The nested collections follow the same order:

```html
<input type="number"
  @value="{SharedRows[0][2], mode=twoWay, update=input}"
  @oninput="{Save, parameter={SharedRows[0][2]}}">
```

`SharedRows[0]` must be a writable shared observable collection. Subcollections nested by value do not support rehydration. The command cannot obtain the value after this input. For more details, see [Value-nested structures do not support rehydration](observable-objects.md).

### Supported events

| Event binding | Meaning of triggering |
| --- | --- |
| `@onclick` | Clicking or activating |
| `@oninput` | During the editing process, the input values change. |
| `@onchange` | The user submits the actual changes to the control values. |
| `@onsubmit` | The form is submitted. |
| `@onfocus` | Getting the focus |
| `@onblur` | Losing the focus |
| `@onkeydown` | Button pressing |
| `@onkeyup` | Button releasing |
| `@onpointerdown` | Pointer press |
| `@onpointerup` | Pointer release |

This is the complete set of events supported by the current template command binding. Events such as `@ondblclick`, `@oncontextmenu`, `@onreset`, `@onwheel`, `@onscroll`, as well as events related to pointer movement, entering, leaving, and cancellation have not been opened for template command binding. Therefore, they cannot be used directly just because the corresponding names exist in standard HTML.

#### Input and focus events

```html
<input
  @value="{Name, update=input}"
  @oninput="{NameEdited, parameter={Name}}"
  @onfocus="{BeginEditing}"
  @onblur="{EndEditing}">
```

`input` indicates changes in the value being edited. It does not refer to a single key press. Deleting, pasting, and changes caused by input methods can all lead to input changes. `change` indicates the submission of actual changes. Text editing usually occurs when the editing is completed and the focus is lost, and the value actually changes. Simply gaining or losing focus corresponds to `focus` and `blur`, respectively.

Event binding has a different purpose from `update`: `@oninput` calls commands, while `update=input` determines when the input value should be written back. Both can be configured separately. For more details, see [Input and Two-Way Binding](input-and-two-way-binding.md).

### Event filtering

The filtering conditions must be static values. `{Expression}` is not accepted. The condition values are case-insensitive. Option names should be written in lowercase. Duplicate names, unknown modifier keys, or empty combinations are invalid. Events that do not match the conditions will not be evaluated, no commands will be executed, and it will not prevent other listeners from taking action or canceling the default action.

#### Keyboard events

`@onkeydown` and `@onkeyup` support static `key` and `modifiers` filtering. Commands are executed only when the conditions are met.

```html
<input
  @onkeydown="{Save}"
  @onkeydown.key="s"
  @onkeydown.modifiers="Control">
```

The conditions can also be written within the binding.

```html
<input @onkeyup="{Save, key='Enter', modifiers=Control+Shift}">
```

| Options | Meanings | Omitted |
| --- | --- | --- |
| `key` | Match the logical key names, such as `Enter`, `Escape`, `s` | There is no restriction on keys |
| `modifiers` | Exact match for modifier key combinations | There is no restriction on modifiers |

`key` The matching logic Key, not the physical keyboard Code. The name is case-insensitive. Spaces are allowed. `key=' '` A plus sign is allowed. `key='+'`.

`modifiers` supports `Control`, `Shift`, `Alt`, `Windows`, `Meta`. Multiple names can be connected by `+`, and the order does not affect the match. `Meta` and `Windows` represent the same modifier key, and cannot be filled in simultaneously. `Control` does not match `Control+Shift` when `Shift` is additionally pressed.

!!! note "None indicates no restrictions"
    `key=none`, `modifiers=none` Similar to the omitted option, it means that no filtering is performed, and it does not mean "no modifier keys should be pressed" or "modifier keys must not be pressed".`none` It cannot be combined with other modifier keys.

#### Mouse events

`@onclick`, `@onpointerdown`, `@onpointerup` Supported `button` And `modifiers`:

```html
<button @onclick="{Save, button=Left, modifiers=Control}">Save</button>

<div
  @onpointerdown="{Select}"
  @onpointerdown.button="Right">
  Select with right button
</div>
```

`button` Supported `Left`, `Middle`, `Right`, `Back`, `Forward` And `none`, Case insensitive. It matches the mouse button triggered by this event, not all buttons that are currently pressed. Can be omitted or written as follows. `none` Indicates no restrictions. The rules for modifier keys are the same as those for keyboard filtering.

`key` Used only for keyboard events.`button` Used only for these three types of mouse or pointer events. Cannot be interchanged.

!!! note "Filtering will not generate new events."
    `@onclick` still relies on the actual click events generated by the platform. The `button=Right` configuration will not automatically generate events for the right-click menu. To handle right-clicking or releasing the mouse button, you can use `@onpointerdown` and `@onpointerup`.

### Options and Platform Limitations

- Event Binding itself does not support `converter`, `update`, or two-way binding modes. For the syntax of converters in parameter expressions, see [Command-Parameter Converters](#command-parameter-converters).
- `template` does not generate interactive elements, and therefore cannot bind element events to it. Events should be bound to actual generated elements such as buttons.
- Currently, there is no syntax to cancel default actions or prevent event propagation through templates, and the command return value does not serve as a switch for these operations.

Whether an event occurs, how focus and input methods are handled, as well as platform-specific operations during command processing, should be based on the actual capabilities of each platform plugin. Template support for event names does not mean that all default behaviors are implemented in the browser.

[^command-platform-scalar]: Platform Scalar refers to native scalar types supported by various platforms, such as Unity and Unreal Engine.

[^command-object]: Object refers to observable objects or platform-specific supported objects.

[^command-shared]: Used in C++. `std::shared_ptr<T>` Used as reference types in C#.

[^command-weak]: Used in C++. `std::weak_ptr<T>` Used in C#. `WeakReference<T>`.
