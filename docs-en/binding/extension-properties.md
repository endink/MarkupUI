---
icon: bootstrap/puzzle
---

# Extension Properties

Extension properties are attributes registered outside the type definition of observable objects. They can be read via getters and can also support writing via setters. There is no need to add properties with the same name in the original class. The page can access these properties through normal property paths. This approach is suitable for deriving display values or providing binding interfaces for existing models.

> For example, the model provides `Health`. A read-only extension property `HealthStatus` can be registered outside the class, which returns the health status enumeration `HealthState`.

## Definition and registration

Make sure to define and register extension properties before opening the page. Register each extension property once. When only a getter is provided, the property is read-only. When both a getter and a setter are provided, the property can be written to.

=== "C++"

    Suppose there is the following observable object:

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <markupui/binding/modeling/object_model.h>

    class PlayerObject
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        PlayerObject()
        {
            InitializeType<PlayerObject>();
        }

        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 80)
    };
    ```

    Register extension properties for `PlayerObject`:

    ```cpp
    #include <markupui/binding/data_binding.h>

    enum class HealthState : int32_t
    {
        Healthy = 0,
        Injured = 1,
        Critical = 2
    };

    class PlayerExtensions final
    {
    private:
        using StatusExtensionProp =
            MarkupUI::Binding::ExtensionProperty<PlayerObject, HealthState>;

        static HealthState GetHealthStatus(const PlayerObject& player)
        {
            if (player.GetHealth() <= 20)
            {
                return HealthState::Critical;
            }
            if (player.GetHealth() < 60)
            {
                return HealthState::Injured;
            }
            return HealthState::Healthy;
        }

    public:
        inline static const StatusExtensionProp HealthStatusProperty =
            MarkupUI::Binding::RegisterExtensionProperty<PlayerObject, HealthState>(
                MARKUPUI_STR_VIEW("HealthStatus"), &GetHealthStatus);

        // Call before opening the page to initialize the static property descriptor.
        static void Initialize()
        {
            (void)HealthStatusProperty;
        }
    };
    ```

    The getter receives `const TObject&` and returns `TValue`. The setter receives `TObject&` and `const TValue&` and returns `void`. Check whether the registration failed using `if (!PlayerExtensions::HealthStatusProperty)`, for example, to ensure the name is valid and no duplicate declarations of the same type occur.

    After creating an instance, use it as the page data context. The application is responsible for managing the object's lifecycle.

    ```cpp
    PlayerExtensions::Initialize();
    std::shared_ptr<PlayerObject> player = std::make_shared<PlayerObject>();
    ```

=== "C#"

    Suppose there is the following observable object:

    ```csharp
    using System.ComponentModel;

    public class PlayerObject : INotifyPropertyChanged
    {
        private int _health = 80;

        public event PropertyChangedEventHandler PropertyChanged;

        public int Health
        {
            get { return _health; }
            set
            {
                if (_health != value)
                {
                    _health = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs(nameof(Health)));
                }
            }
        }
    }

    ```

    Register extension properties for `PlayerObject`:

    ```csharp
    using MarkupUI.Sdk.Binding;

    public enum HealthState
    {
        Healthy = 0,
        Injured = 1,
        Critical = 2
    }

    public static class PlayerExtensions
    {
        public static readonly ExtensionProperty<PlayerObject, HealthState> HealthStatusProperty =
            DataBindingUtilities.RegisterExtensionProperty<PlayerObject, HealthState>(
                "HealthStatus", GetHealthStatus);

        // Call before opening the page to complete static initialization.
        public static void Initialize() { }

        private static HealthState GetHealthStatus(PlayerObject player)
        {
            if (player.Health <= 20)
            {
                return HealthState.Critical;
            }
            if (player.Health < 60)
            {
                return HealthState.Injured;
            }
            return HealthState.Healthy;
        }
    }
    ```

    After initialization, create an instance and use it as the page data context.

    ```csharp
    PlayerExtensions.Initialize();
    var player = new PlayerObject();
    ```

    Invalid names, empty accessors, or types that are not supported will throw a parameter exception. Duplicate registrations with the same name for the same type will result in an `MarkupInvalidOperationException`. Accessors that use static methods or delegates that do not capture the business instance are also invalid.

## Page usage

Extension properties do not require any special HTML syntax. They can be bound using the same binding path as regular properties.

```html
<!-- Set the current data context to the PlayerObject instance from the example above. -->
<p @if="{HealthStatus == 0}">健康</p>
<p @if="{HealthStatus == 1}">受伤</p>
<p @if="{HealthStatus == 2}">危急</p>
```

When `Health` is greater than or equal to `60`, it is considered `Healthy`. When it is greater than `20` but less than `60`, it is considered `Injured`. When it is less than or equal to `20`, it is considered `Critical`. The page uses the integer values corresponding to the enumerations to display text. The initial value of `Health` is `80`, so it is displayed as "Healthy". The `HealthStatus` only provides a getter method and cannot be used to write back the value.

Extension properties can also be accessed through child object paths, named contexts, or declared aliases. For more details, see [Data Context](../concepts/data-context.md).

## Change notification

The getter calculates the result during reading, without caching or automatic inference of dependencies. After modifying the source data, it is necessary to explicitly notify the affected extension properties. Calling the setter itself does not automatically send notifications for extension properties.

=== "C++"

    ```cpp
    player->SetHealth(15);
    MarkupUI::Binding::NotifyPropertyChanged(
        *player, PlayerExtensions::HealthStatusProperty.GetName());

    ```

=== "C#"

    ```csharp
    player.Health = 15;
    PlayerExtensions.HealthStatusProperty.NotifyChanged(player);

    ```

In C++, both regular properties and extension properties are used uniformly. `MarkupUI::Binding::NotifyPropertyChanged` The object and property names are passed in. In C#, it is also possible to use the extension property names of the object. `PropertyChanged` The extension property names are used to send events. `NotifyChanged` Select one option to avoid duplicate notifications. Data reading and writing follow the data thread access conventions defined by the application configuration.

## Inheritance

The extension properties registered for `PlayerObject` are also applicable to its derived classes, eliminating the need for repeated registration. For example, define the following derived types:

=== "C++"

    ```cpp
    class WarriorObject final : public PlayerObject
    {
    public:
        WarriorObject()
        {
            InitializeType<WarriorObject>();
        }
    };

    PlayerExtensions::Initialize();
    std::shared_ptr<WarriorObject> player = std::make_shared<WarriorObject>();
    ```

=== "C#"

    ```csharp
    public class WarriorObject : PlayerObject
    {
    }

    // Initialize the extension property before opening the page.
    PlayerExtensions.Initialize();
    var player = new WarriorObject();
    ```

After using an `WarriorObject` instance as the data context, the page can still read `HealthStatus`. The getter receives the `PlayerObject` instance corresponding to this instance, and calculates the status based on the inherited `Health`. The derived instances also use the same notification method: in C++, call `MarkupUI::Binding::NotifyPropertyChanged`, and in C#, call the `NotifyChanged` described by the extension property.

When reading or writing properties, the following order is followed for searching:

1. Search for the ordinary properties of the object itself and its inherited properties. Once found, use these ordinary properties. No further searches for extension properties with the same name will be conducted.
2. If there are no ordinary properties with the same name, search for the extension properties registered for the actual type of the object. In this example, we first search for `WarriorObject`.
3. If no extension properties are declared for the current type, continue searching along the inheritance chain from the nearest base class. In this example, we then search for `PlayerObject`, and thus can find the registered `HealthStatus`.
4. If there is no matching extension property throughout the entire inheritance chain, treat the property as non-existent.

Therefore, the extension properties registered by the derived class take precedence over the extension properties with the same name in the base class, but they cannot override the ordinary properties.

## Rules for type and name

- Property names must not contain symbols such as `.`, `/`, `\`, `[`, `]` etc.
- The getter should only read data and should not cause any side effects in the business process.
- The writing of properties follows the type checking rules of ordinary properties, and the number conversion rules of command parameters are not used.

C++ supports reading and writing of scalars, strings, and registered scalar mappings. Explicit shared objects and weak object return values are currently read-only. Value-based return collections are not supported, and shared collection return values are also not within the current support range.

C# supports scalars, strings, nullable scalars, objects, weak objects, and supported collection types. Objects, weak objects, Map, and Set are currently read-only. It is supported to replace scalar arrays entirely according to ordinary property rules. Changes within the collection are still sent by the collection itself.

!!! note "Registration of lifecycle"
    Extension property registration does not hold instances of business objects. Registration cannot be revoked individually. It should be completed during the application initialization phase, and the accessor code should be valid during use.
