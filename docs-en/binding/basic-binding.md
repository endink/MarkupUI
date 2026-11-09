---
icon: bootstrap/link-45deg
---

# Basic Binding

The basic binding reads a single value from the data context and uses it for text, HTML attributes, or CSS styles. The read value can be a string, numerical value, or boolean value, or it can be an attribute within an object. The object itself can be used as the data context for a set of elements.

## Scalar Values and Objects

The following code defines players, weapons, and weapon owners. The created `player` is used as the default data context for the document. For scalar values, objects, and their supported ranges, see [Data Types](data-types.md).

=== "C++"

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <string>
    #include <markupui/binding/modeling/object_model.h>

    class OwnerObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        OwnerObject() { InitializeType<OwnerObject>(); }

        MARKUPUI_PROPERTY(OwnerObject, std::string, Name, "Alice")
        MARKUPUI_PROPERTY(OwnerObject, std::string, AvatarPath, "/images/alice.png")
    };

    class WeaponObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        WeaponObject() { InitializeType<WeaponObject>(); }

        MARKUPUI_PROPERTY(WeaponObject, std::string, Name, "Sword")
        MARKUPUI_PROPERTY(WeaponObject, int32_t, Damage, 25)
        /*
         * Argument 1 is WeaponObject, the class that declares the property.
         * Argument 2 is std::weak_ptr<OwnerObject>, a weak reference that leaves the owner's lifetime independent.
         * Argument 3 is WeaponOwner, the C++ property identifier used to generate
         *         the GetWeaponOwner() and SetWeaponOwner() accessors.
         * Argument 4 is "WeaponOwner", the property name used in HTML bindings,
         *         for example, WeaponOwner in Weapon.WeaponOwner.Name.
         * Argument 5 is the optional default value. Omitting it here leaves the reference initially empty.
         */
        MARKUPUI_NAMED_PROPERTY(WeaponObject, std::weak_ptr<OwnerObject>, WeaponOwner, "WeaponOwner")
    };

    class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        PlayerObject() { InitializeType<PlayerObject>(); }

        MARKUPUI_PROPERTY(PlayerObject, std::string, Name, "Alice")
        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 100)
        MARKUPUI_PROPERTY(PlayerObject, std::string, AvatarPath, "/images/alice.png")
        MARKUPUI_PROPERTY(PlayerObject, bool, IsReady, true)
        MARKUPUI_PROPERTY(PlayerObject, std::shared_ptr<WeaponObject>, Weapon)
    };
    ```

    Create objects and connect nested properties:

    ```cpp
    auto owner = std::make_shared<OwnerObject>();

    auto weapon = std::make_shared<WeaponObject>();
    weapon->SetWeaponOwner(std::weak_ptr<OwnerObject>{owner});

    auto player = std::make_shared<PlayerObject>();
    player->SetWeapon(weapon);
    ```

    The binding name for `WeaponOwner` is `WeaponOwner`, so in HTML, it is referred to as `Weapon.WeaponOwner.Name`. In C++, this business property is set using `SetWeaponOwner()`.

    Weapons use weak references to their owners, which does not extend the lifetime of the owners. The strong reference of `owner` in the example should be retained by the application. After the owner is destroyed, the weak reference becomes invalid. In C++ business code, when accessing weak references, a temporary strong reference should be obtained using `lock()` and the result should be checked.

=== "C#"

    ```csharp
    using System;
    using System.ComponentModel;

    public class OwnerObject : INotifyPropertyChanged
    {
        private string _name = "Alice";
        private string _avatarPath = "/images/alice.png";

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

        public string AvatarPath
        {
            get { return _avatarPath; }
            set
            {
                if (_avatarPath != value)
                {
                    _avatarPath = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("AvatarPath"));
                }
            }
        }
    }

    public class WeaponObject : INotifyPropertyChanged
    {
        private string _name = "Sword";
        private int _damage = 25;
        // C# garbage collection can reclaim unreachable objects that reference each other.
        // This example uses WeakReference<T> to demonstrate support for weak-reference properties.
        private WeakReference<OwnerObject> _weaponOwner;

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

        public WeakReference<OwnerObject> WeaponOwner
        {
            get { return _weaponOwner; }
            set
            {
                if (_weaponOwner != value)
                {
                    _weaponOwner = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("WeaponOwner"));
                }
            }
        }
    }

    public class PlayerObject : INotifyPropertyChanged
    {
        private string _name = "Alice";
        private int _health = 100;
        private string _avatarPath = "/images/alice.png";
        private bool _isReady = true;
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

        public string AvatarPath
        {
            get { return _avatarPath; }
            set
            {
                if (_avatarPath != value)
                {
                    _avatarPath = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("AvatarPath"));
                }
            }
        }

        public bool IsReady
        {
            get { return _isReady; }
            set
            {
                if (_isReady != value)
                {
                    _isReady = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("IsReady"));
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

    Creating objects:

    ```csharp
    var owner = new OwnerObject();
    var player = new PlayerObject();
    var weapon = player.Weapon;
    weapon.WeaponOwner = new WeakReference<OwnerObject>(owner);
    ```

    `WeaponOwner` is a weak reference property declared as `WeakReference<OwnerObject>`. The binding can continue to access the target object, such as `Weapon.WeaponOwner.Name`. There is no need to define a strong-reference wrapping property in the observable object. Applications should retain a strong reference to `owner`. After the target object is reclaimed, the binding path cannot obtain the target object. The failure of the weak reference does not trigger any property notifications. In business terms, when the ownership relationship is terminated, it is necessary to explicitly set `WeaponOwner = null` and notify the binding.

- `Name`, `Health`, `AvatarPath`, and `IsReady` are scalar properties.
- `Weapon` is an object property, containing `Name` and `Damage`.
- `Weapon.Name` is a property path, and the final value read is the string `"Sword"`.

!!! note "Object properties and HTML properties"
    The properties in the data context belong to business objects, such as `PlayerObject.Name`; HTML properties belong to elements, such as `img`’s `src`. The binding uses the value of the former for the latter. There is no requirement that the names of the two properties be the same.

## Bind the scalar value

### Display text

Text interpolation will insert the scalar value into the text content of the element. It can be combined with fixed text:

```html
<h1>{{ Name }}</h1>
<p>Health: {{ Health }}</p>
```

The final HTML code produced:

```html
<h1>Alice</h1>
<p>Health: 100</p>
```

You can also use `@text` to bind the entire text content:

```html
<h1 @text="{Name}">Player name</h1>
```

`Player name` is a placeholder text during design, and it is replaced by the binding result during runtime. Text binding is used to display text, and the HTML tags in the string are not parsed as part of the page structure.

### Set HTML properties

Use `@property-name` to bind a value to an HTML attribute. The example binds `AvatarPath` to the image `src` and `Name` to the input `value`.

```html
<img @src="{AvatarPath}" alt="Player avatar">
<input @value="{Name}">
```

The purpose of the bound values is as follows: The image path is parsed according to the [Resource Paths](../authoring/resource-paths.md) rules. The input fields display strings, and the input can be written back to `Name` according to the binding mode.

### Set the style

Use `@style.property-name` to set an individual CSS property. This example uses the numeric `Opacity` property from the data context.

```html
<div @style.opacity="{Opacity}">Player information</div>
```

The bound results must conform to the target's type and value range. `opacity` requires a valid transparency value. Other styles such as length and color also require corresponding values. The binding does not automatically select CSS units for any numerical values.

## Access properties within the object

Using a dot to connect property names allows for reading values within the object level by level:

```html
<p>Weapon: {{ Weapon.Name }}</p>
<p>Damage: {{ Weapon.Damage }}</p>
```

The path starts from the current data context: First, read the `Weapon` of `PlayerObject`, and then read the `Name` or `Damage` of the weapon object.

The final HTML code produced:

```html
<p>Weapon: Sword</p>
<p>Damage: 25</p>
```

`Name` and `Weapon.Name` point to different properties: The former is the player's name, and the latter is the weapon's name. Property names are **case-sensitive** and should be consistent with the names provided by the application.

### Multi-level property paths

The property path can be used to access deeper objects through multiple dots. For example, `Weapon.WeaponOwner.Name` reads `Weapon`, the weapon's `Owner`, and finally the owner's `Name` from the current data context in sequence:

```html
<p>Owner: {{ Weapon.WeaponOwner.Name }}</p>
```

The final HTML code produced:

```html
<p>Owner: Alice</p>
```

Each name in the path belongs to the object read from the previous level, not a single property name with dots. The intermediate object must exist in order to continue reading subsequent properties.

Multi-level paths can also be used for HTML property binding. For example, when the weapon's `Owner` object provides `AvatarPath`:

```html
<img @src="{Weapon.WeaponOwner.AvatarPath}" alt="Weapon owner avatar">
```

The path is parsed starting from the current data context. Use it. `@context="{Weapon}"` After that, the same owner name should be written as. `WeaponOwner.Name`:

```html
<section @context="{Weapon}">
  <p>Owner: {{ WeaponOwner.Name }}</p>
</section>
```

For `Weapon.WeaponOwner.Name`, when the owner name is changed, the `Name` change is notified by the owner object. When the owner is replaced, the `Owner` change is notified by the weapon object. When the weapon is replaced, the `Weapon` change is notified by the player object. The binding reads the affected paths again accordingly, and subsequent updates use the replaced objects.

## Use the object as a data context

When a group of elements display the properties of the same object, this object can be used as a data context through `@context`:

```html
<section @context="{Weapon}">
  <h2>{{ Name }}</h2>
  <p>Damage: {{ Damage }}</p>
</section>
```

`Weapon` reads from the outer data context. After specifying the context, both the element itself and its child elements will use the specified data context. Therefore, both `Name` and `Damage` belong to the weapon object.

The two notations have different purposes:

| Notation | Meaning | Applicable scenarios |
| --- | --- | --- |
| `{{ Weapon.Name }}` | Read nested properties from the current context | Only display a limited number of properties within the object |
| `@context="{Weapon}"` It is used internally. `{{ Name }}` | Use the object as the data context to read properties | Display the object together with a group of elements |

!!! note "The object is not an automatically generated interface"
    `Weapon` Represents the object.`Weapon.Name` Only represents the weapon name. Do not use it instead of. `{{ Weapon }}` Instead of `{{ Weapon.Name }}` When displaying the name, do not rely on it to automatically expand object fields. The attributes that need to be displayed should be explicitly declared in HTML.

When using an object directly for text insertion, bind to the string representation provided by the object. If no representation is provided, use `[Object]`. This string is not equal to the object's `Name` property, nor is it the serialized result of all fields.

Incorrect scenario: Attempting to display the weapon name by directly binding the weapon object. Assuming that this object does not provide a string representation:

```html
<!-- Invalid because Weapon is an object. Use Weapon.Name to display its name. -->
<p>Weapon: {{ Weapon }}</p>
```

The final HTML code produced:

```html
<p>Weapon: [Object]</p>
```

For details on naming contexts, nested scopes, and outer aliases, see [Data Context](../concepts/data-context.md).

## Changes in properties and object replacements

Continuous updates to bindings require corresponding notification. For `Weapon.Name`, distinguish between the following two operations:

| Operations | Example | Required notifications and results |
| --- | --- | --- |
| Modify properties within the object | Change the `Name` of the current weapon from `Sword` to `Bow` | The weapon object notifies the change in `Name`, and the relevant text reads the new name again |
| Replace object properties | Replace the player's `Weapon` with another weapon | The player object notifies the `Weapon` of changes. The binding is re-parse to read the properties of the new weapon. |

After replacing the `Weapon`, `Weapon.Name` and the areas using `@context="{Weapon}"` will be redirected to the new object. Subsequent updates should be driven by the properties of the new weapon. Changes to the old weapon no longer determine the content of those areas.

For scalar properties like `Health` that are directly bound, it is also necessary to notify when the corresponding property changes. Simply modifying the value in the business object does not mean that the interface has been updated.

The above continuous update behavior applies to bindings that need to monitor data changes. `oneTime` does not continuously monitor subsequent changes. For details on the mode and input write-back rules, see [Data Binding Overview](getting-started.md). Please refer to the documentation for the respective platforms for information on notification methods.

## Empty objects and missing properties

When `Weapon` is empty, `Weapon.Name` cannot read the weapon name. When a property does not exist, no valid value can be obtained. Text interpolation will display as empty in these cases, and the outer property with the same name will not be automatically used.

```html
<!-- The weapon name is blank when Weapon is null. -->
<p>Weapon: {{ Weapon.Name }}</p>
```

After setting a valid object for `Weapon` and sending the corresponding notification, the binding can retrieve the name again.

Do not treat empty results as numerical values of `0` or boolean values of `false`. Also, do not assume that the handling of empty values is the same for texts, images, styles, and input targets. When default texts or hidden areas are required in the business logic, it is necessary to set corresponding expressions or display conditions clearly.
