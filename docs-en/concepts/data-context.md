---
icon: bootstrap/database
---

# Data Context

**Data Context** is the object used by the page binding expression to read data. For example, the player information panel can use the player object as the data context, and display character information through properties such as `Name` and `Health` of the object.

The data context is provided by the application through the platform plugin. HTML is responsible for declaring which data is used, and there is no need to fix business data such as the current character name and health value in the page.

## Observable Objects

The data context of Markup UI is provided in the form of **observable objects**. Observable objects include business properties that can be read by HTML binding, and notifications are issued when these properties change, enabling the interface to update. Once the observable object is provided to a document or an element, this object becomes the corresponding data context.

The following example defines the player object `PlayerObject` and the weapon object `WeaponObject`. Both provide notifications when properties change, allowing for updates to the player's `Health`, `Weapon.Name`, or even the entire `Weapon` object.

=== "C++"

    1. Inherit the `ObservableObject` base class provided by the SDK.
    2. Use `MARKUPUI_PROPERTY` to declare bindable properties.
    3. In the constructor, call `InitializeType<T>()`, where `T` is the type of the current class.
    4. Use `std::make_shared<T>()` to create objects.

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <string>
    #include <markupui/binding/modeling/object_model.h>

    class WeaponObject final
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        WeaponObject()
        {
            InitializeType<WeaponObject>();
        }

        /*
         * Argument 1 is WeaponObject, the class that declares the property.
         * Argument 2 is std::string, the property type.
         * Argument 3 is Name, the property name used by HTML bindings. The macro
         *         also generates the GetName() and SetName() accessors.
         * Argument 4 is "Sword", the default property value.
         */
        MARKUPUI_PROPERTY(WeaponObject, std::string, Name, "Sword")
        MARKUPUI_PROPERTY(WeaponObject, int32_t, Damage, 25)
    };

    class PlayerObject final
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        PlayerObject()
        {
            InitializeType<PlayerObject>();
        }

        MARKUPUI_PROPERTY(PlayerObject, std::string, Name, "Alice")
        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 100)
        MARKUPUI_PROPERTY(
            PlayerObject, std::shared_ptr<WeaponObject>, Weapon)
    };
    ```

    Create players and their weapons:

    ```cpp
    auto weapon = std::make_shared<WeaponObject>();

    auto player = std::make_shared<PlayerObject>();
    player->SetWeapon(weapon);
    ```

    The macro generates accessors such as `GetName()` and `SetName()`. When modifying properties through setter methods like `SetHealth()` and `SetWeapon()`, the change notifications are handled by the observable object. In HTML, the declared property names `Health` and `Weapon` are used, not the accessor names.

=== "C#"

    The SDK supports the standard `INotifyPropertyChanged` interface. Data is read through the public properties, and change notifications are received through `PropertyChanged`. The following two classes directly implement this interface and send notifications in the property setters.

    ```csharp
    using System.ComponentModel;

    public class WeaponObject : INotifyPropertyChanged
    {
        private string _name = "Sword";
        private int _damage = 25;

        public event PropertyChangedEventHandler PropertyChanged;

        public string Name
        {
            get { return _name; }
            set
            {
                if (_name != value)
                {
                    _name = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("Name"));
                }
            }
        }

        public int Damage
        {
            get { return _damage; }
            set
            {
                if (_damage != value)
                {
                    _damage = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("Damage"));
                }
            }
        }
    }

    public class PlayerObject : INotifyPropertyChanged
    {
        private string _name = "Alice";
        private int _health = 100;
        private WeaponObject _weapon = new WeaponObject();

        public event PropertyChangedEventHandler PropertyChanged;

        public string Name
        {
            get { return _name; }
            set
            {
                if (_name != value)
                {
                    _name = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("Name"));
                }
            }
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

        public WeaponObject Weapon
        {
            get { return _weapon; }
            set
            {
                if (_weapon != value)
                {
                    _weapon = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("Weapon"));
                }
            }
        }
    }
    ```

    Create players and their weapons:

    ```csharp
    var player = new PlayerObject();
    var weapon = player.Weapon;
    ```

    The property setter sends notifications with the same name as the property when the value changes. For example, setting `Health` will notify `Health` of the change, and setting `Weapon` will notify the weapon object of being replaced.

    !!! tip "Use the existing ObservableObject base class"
        When the project references the corresponding toolkit, the business class can inherit from [ObservableObject](https://learn.microsoft.com/dotnet/api/microsoft.toolkit.mvvm.componentmodel.observableobject){ target="_blank" rel="noopener noreferrer" }. It implements `INotifyPropertyChanged` and provides auxiliary methods such as `SetProperty`, which can reduce the repetition of code related to property change notifications.

        The type in the link belongs to the `Microsoft.Toolkit.Mvvm` package, not a .NET Standard built-in type. Only use its property notification capabilities. There is no need to adopt a specific application architecture.

!!! note "Each object notifies itself of changes to its properties."
    When modifying `Weapon.Name`, the weapon object notifies changes to `Name`. When replacing `PlayerObject.Weapon`, the player object notifies changes to `Weapon`. Only make the player object observable. Do not replace the notification of internal weapon properties.

## Read properties from the data context

Use the `player` object provided in the above example as the default data context for the document. For specific settings, please refer to the documentation for each platform.

When using this object as the data context, properties can be referenced in HTML:

```html
<h1>{{ Name }}</h1>
<p>Health: {{ Health }}</p>
<p>Weapon: {{ Weapon.Name }}</p>
```

The final HTML code output:

```html
<h1>Alice</h1>
<p>Health: 100</p>
<p>Weapon: Sword</p>
```

`{{ ... }}` indicates text interpolation. `Name` is retrieved from the current data context, while `Weapon.Name` is obtained from the property path. The C++ and C# examples use the same property names, so the same HTML structure is used.

The data context serves as the starting point for finding properties. The specific property path determines the value to be bound. Whether the value is displayed in an element, written as text, or as an element property, is determined by the binding declaration.

## Default to the named data context

A document can configure multiple data contexts (DataContext). There is at most one **default data context**, which has no name. Other data contexts are distinguished by their names, and each name must be unique within the same document.

### Default data context

By default, all HTML elements use the document's default data context as their own data context. Once the context is specified using `@context`, both the element itself and its child elements will use the specified data context.

```html
<!-- Use the document's default data context. -->
<p>{{ Name }}</p>

<!-- Switch to the Weapon property of the default data context. -->
<section @context="{Weapon}">
  <h1>{{ Name }}</h1>
  <p>Damage: {{ Damage }}</p>
</section>

<!-- Switch to the context named "player". -->
<section @context="player">
  <h1>{{ Name }}</h1>
  <p>Health: {{ Health }}</p>
</section>
```

### Name the data context

When a page requires multiple independent business objects, the application can register data contexts by name. For example, register the player object as `player`, and the settings object as `settings`.

```html
<section @context="player">
  <h1>{{ Name }}</h1>
  <p>Health: {{ Health }}</p>
</section>

<section @context="settings">
  <p>Volume: {{ Volume }}</p>
</section>
```

`@context="player"` selects the `player` object registered by the application. `@context="settings"` selects the `settings` object. The page can use only the named data context without setting a default object.

!!! note "The name must be registered by the application."
    Entering `player` in HTML does not create a player object, nor does it automatically find game objects with the same name. Names are **case-sensitive**. When the application does not register a corresponding name, this area uses an empty context, and it will not revert to the parent or default object.

Static names should consist of non-empty ASCII letters, numbers, underscores, or hyphens. `mk:context` is equivalent to `@context`, and either form can be chosen according to the page's writing convention.

## Nested contexts and the current object

### Switch the context through properties

Obtain a child object in the current context, which can be used as the new context for a certain area:

```html
<section @context="player">
  <h1>{{ Name }}</h1>
  <div @context="{Weapon}">
    <p>{{ Name }}</p>
    <p>Damage: {{ Damage }}</p>
  </div>
</section>
```

The `Name` at the outermost level represents the player's name. When entering `Weapon`, the `Name` and `Damage` within represent the name of the weapon and its damage respectively. This switch applies to the declared elements and their descendants, without changing the context of the external sibling areas.

| Writing method | Meaning |
| --- | --- |
| Do not write `@context` | Inherit the parent context. Use the default context at the outermost level |
| `@context="player"` | Select the named context to which the application is registered. |
| `@context="{Weapon}"` | Evaluate the `Weapon` property from the current context and use the result. |

!!! note "The name is different from the property expression."
    `@context="Weapon"` selects the context with the name `Weapon`; `@context="{Weapon}"` reads the `Weapon` property of the current object. These two cannot be used interchangeably.

### Current object

`@this` represents the current data context. The normal property path `Name` is equivalent to `@this.Name`. After switching contexts, the reference of `@this` also changes.

## Data context alias

Use `@as` on any HTML element to give its data context an alias. You can then refer to that context with `@alias`. If the element has no `@context` declaration, the alias refers to the inherited context.

### Create an alias for the inherited context

`@as="page"` creates an alias for the current inherited context:

```html
<section @as="page">
  <p>{{ @page.Name }}</p>
</section>
```

`@page` It does not switch the context itself. `section` The inherited data context,`@as` Does not switch the context itself.

### Create aliases for the switched context

When both `@context` and `@as` are declared, the alias points to the changed context.

```html
<section @as="page">
  <div @context="{Child}" @as="child">
    <p>Child: {{ @child.Name }}</p>
    <p>Page: {{ @page.Name }}</p>
  </div>
</section>
```

`@child` points to the object provided by the `Child` property, while `@page` still points to the outer context.

### The alias for the data context of the loop container

`@for="{Items}" @as="page"` creates an alias for the data context of the loop container. Aliases are created using `@item-as` for collection elements:

```html
<ul @for="{Items}" @as="page" @item-as="item">
  <li>{{ @page.Name }}: {{ @item.Name }}</li>
</ul>
```

`@page` refers to the context that provides `Items`, while `@item` refers to the current collection element. `@as` does not create aliases for collection elements. For more details on loop rules, see [Collection Binding](../binding/collection-binding.md).

Aliases are used within the declaration area and its sub-areas, and do not affect external sibling areas. They are names within the template, not part of the named data context registered by the application.

## Data changes and context replacement

Modify the properties of the objects already mentioned in the previous example:

=== "C++"

    ```cpp
    player->SetHealth(80);
    weapon->SetName("Bow");
    ```

=== "C#"

    ```csharp
    player.Health = 80;
    weapon.Name = "Bow";
    ```

Both methods update the bindings through the object's notification mechanism. The original HTML then displays `Health: 80` and `Weapon: Bow`.

Modifying the properties of a business object and replacing the entire data context are different operations:

- **Property changes**: For example, changing the `Health` value of the current player from `100` to `80`. The object itself is not replaced. The application should update the bindings through corresponding change notifications.
- **Context replacement**: For example, when selecting another player, the player object used on the page is replaced with a new object. The related bindings then read data from the new object.

The default context and each named context are managed separately. Replacing the default object does not automatically overwrite registered named objects such as `player` and `settings`.

!!! tip "When the interface has not been updated yet"
    First, check whether the context is available, whether the names are consistent, whether the property paths are correct, and whether the corresponding notifications have been sent for the data changes. Simply modifying the context name in HTML cannot replace the data configuration on the application side.

## The way the platform provides data

The default context, named context, and page-specific scope are common concepts. The type of business objects, the entry points for settings, the management of references, and the notification of changes are determined by the platform integration methods. For more details, please refer to the documentation of each platform.

Related chapters: [Data Binding Overview](../binding/getting-started.md), [Basic Binding](../binding/basic-binding.md), [Binding Syntax](../binding/binding-syntax.md), [Events and Commands](../binding/events-and-commands.md).
