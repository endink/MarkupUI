---
icon: bootstrap/cursor
---

# Command Binding

Markup UI natively supports command binding. Page events are associated with commands in the data context, and application logic is executed when buttons are clicked or input fields are submitted. For detailed usage, see [Events and Commands](../../binding/events-and-commands.md).

!!! abstract "Calling thread"
    All command callbacks are executed on the **game thread**.

## UFUNCTION

Page events can call C++ or blueprint functions on data objects that meet the following conditions to execute game logic.

Command functions must meet the following requirements:

- **Function type**: It must be a public instance function that can be called from the blueprint. In C++, it is declared using `UFUNCTION(BlueprintCallable)`. Static functions, delegates, and network functions cannot be used as commands.
- **Return value**: There is no return value. In C++, `void` is used, and no return value is added in the blueprint.
- **Property Accessor**: Also determined based on the function signature. `BlueprintSetter` that has no return value and can be called from the blueprint can be bound as a command. `BlueprintGetter` with a return value does not meet the requirements.
- **Parameter Types**: Supports scalar values, boolean values, enums, `FString`, `FName`, `FText`, colors, vectors, and references to `UObject` objects.
- **Parameter Constraints**: Does not support ordinary structures, collections, or writeable output parameters. The number, order, and type of parameters passed must be consistent with the function declaration.

## Binding

First, set the data object as the data context of **MarkupUI Widget**. For specific operations, refer to [Property Binding](property-binding.md). For example, if the data object provides a `Save` function with no parameters and no return value, bind it to the function name in HTML:

```html
<button @onclick="{Save}">保存</button>
```

Use `{Save}`, do not use `{Save()}`. The command name should use the actual function name.

=== "C++"

    Declare public instance functions in the class of the data object, and implement the saving logic in the implementation:

    ```cpp
    public:
        UFUNCTION(BlueprintCallable, Category = "Player")
        void Save();
    ```

    The function needs to be declared as `UFUNCTION`. Ordinary C++ member functions cannot be bound through reflection.

=== "Blueprint"

    1. Create the `Save` function in the blueprint object that serves as the data context.
    2. Set the access permission of the function to **Public**, without adding input parameters or return values.
    3. Write the saving logic within the function.
    4. Use `@onclick="{Save}"` to bind the function in HTML.
    On the left side of the figure is the `Save` function in the **Functions** list, and on the right side is the `Save` entry node in the function graph. The saving logic is connected from the execution pin of the entry node.

    ![The Save function in the blueprint Functions list and its entry nodes](images/command-binding/bluepirint-save-command.jpg)

## Command parameters

Pass the property value through `parameter`. For example, pass the `TargetHealth` from the data context to `ApplyHealth`:

```html
<button @onclick="{ApplyHealth, parameter={TargetHealth}}">应用生命值</button>
```

Corresponding C++ declaration:

```cpp
UPROPERTY(BlueprintReadWrite, Category = "Player")
int32 TargetHealth = 100;

UFUNCTION(BlueprintCallable, Category = "Player")
void ApplyHealth(int32 Value);
```

Create a function with the same name in the blueprint and add an integer input parameter. The number, order, and type of parameters must be consistent with the function declaration. Use `parameter={FirstValue, SecondValue}` for multiple parameters.

After the command modifies the bound property, a property change notification must still be sent. Use the corresponding notification for the modified collection. See [Property Binding](property-binding.md) for details.

## Execution conditions

The execution of commands can be controlled through conditional functions or boolean properties. Before executing a command due to a page event, the conditional function is queried first. If no corresponding function is found, then the boolean property with the same name is read.

### Naming rules

The names of conditional members are `Can` followed by the name of the command function. These members are defined on the same data object, and no additional declaration in HTML is required.

- `Save` corresponds to `CanSave`.
- `ApplyHealth` corresponds to `CanApplyHealth`.
- `{Settings.Save}` checks `CanSave` on the `Settings` object.

### Conditional function

- It must be an instance of `UFUNCTION`. It cannot be a static function or a network function.
- It does not accept any input or output parameters. Even if the command itself has parameters, the conditional function does not accept these parameters.
- It must return a `bool` value. In C++, the `const` modifier is optional.

For example, `Save` and its conditional function are declared as follows:

```cpp
public:
    UFUNCTION(BlueprintCallable, Category = "Player")
    void Save();

    UFUNCTION(BlueprintCallable, Category = "Player")
    bool CanSave() const;
```

In the blueprint, a function `CanSave` is created. No input parameters are added. Only a return value of the **Boolean** type is provided.

### Boolean property

When the condition only requires reading a boolean value, you can directly use `bool` type `UPROPERTY`, without having to write a separate conditional function.

```cpp
public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Player")
    bool CanSave = true;

    UFUNCTION(BlueprintCallable, Category = "Player")
    void Save();
```

In the blueprint, you can also create a **Boolean** variable named `CanSave`. Read the current value of this property before executing `Save`.

### Search order

1. Search for conditional functions on the same data object, such as `CanSave`.
2. When there are no conditional functions, search for the boolean property with the same name.
3. When neither functions nor properties are found, the execution is allowed by default.

If a conditional function is found but its signature does not meet the requirements, or a property is found but its type is not `bool`, an error will be recorded and the execution will be rejected. Other conditions will not be used anymore.

### Check the results

- If the conditional function returns a value of `true`, the command is executed.
- If the conditional function returns a value of `false`, this command is skipped.

The conditional check does not automatically change the button's disabled appearance. The button state needs to be manually bound when necessary.

Commands on child objects can use `{Settings.Save}`. For general syntax for entering commands, refer to [Events and Commands](../../binding/events-and-commands.md).
