---
icon: bootstrap/diagram-3
---

# Observable Objects

The properties of observable objects can be provided to other objects or collections, and the items in the collections can also contain objects or collections. For example, a backpack object contains a list of items, and each item contains a property object. Each task in the task list contains its own goal list.

!!! note "Platform-native types"
    Each platform plugin also supports its own native types, such as `UObject` and `TArray` in Unreal Engine. For specific support scope and usage methods, please refer to the documentation for each platform.

The nesting method determines the granularity of change notifications in the SDK and the starting point for reading the binding path. For details on types and language representation, see [Data Types](data-types.md). For the HTML traversal syntax of collections, see [Collection Binding](collection-binding.md).

## Objects

Observable objects provide bindable properties and send notifications when the properties change. In C++, you can use `ObservableObject`, add macro support to an existing class, or implement `MarkupUI::Binding::IObject` directly. In C#, implement `INotifyPropertyChanged`.

**Property Change Notifications**

| Creation Method | Modification Method | Notification |
| --- | --- | --- |
| `ObservableObject` and Property Macros | `player->SetHealth(80)` | Automatic Sending |
| `ObservableObject` and Manual Registration of Properties | `SetValue(HealthProperty, value)` | Automatic Sending |
| Member Macros | `player->Health = 80` | Then call `NotifyPropertyChanged` |
| Customize `IObject` | Custom property setting function | Send property events by the implementation |
| C# `INotifyPropertyChanged` | `player.Health = 80` | Trigger `PropertyChanged` by the setter |

The notification name must be the same as the bound property name. Directly modifying the field does not automatically equal the property notification.


### C++ implementation

#### ObservableObject

Derive from `ObservableObject` and declare properties with `MARKUPUI_PROPERTY`. The macro generates accessors, and the generated setters send property change notifications.

```cpp
#include <cstdint>
#include <memory>
#include <string>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    PlayerObject()
    {
        InitializeType<PlayerObject>();
    }

    MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 100)
    MARKUPUI_PROPERTY(PlayerObject, std::string, Name, "Alice")
};
```

The following code registers the same properties by hand.

```cpp
#include <cstdint>
#include <memory>
#include <string>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    using Property = MarkupUI::Binding::Modeling::Property;

    inline static const Property HealthProperty =
        Property::Register<PlayerObject, int32_t>("Health", 100);

    inline static const Property NameProperty =
        Property::Register<PlayerObject, std::string>("Name", "Alice");

    PlayerObject()
    {
        InitializeType<PlayerObject>();
    }

    int32_t GetHealth() const
    {
        return GetValue<int32_t>(HealthProperty);
    }

    void SetHealth(int32_t value)
    {
        SetValue(HealthProperty, value);
    }

    const std::string& GetName() const
    {
        return GetValue<std::string>(NameProperty);
    }

    void SetName(const std::string& value)
    {
        SetValue(NameProperty, value);
    }
};
```

The setters send property change notifications when the values change.

```cpp
auto player = std::make_shared<PlayerObject>();

player->SetHealth(80);    // Notify that Health changed.
player->SetName("Grace"); // Notify that Name changed.
```

!!! note "Initialize the Type"
    Call `InitializeType<T>()` in the constructor of a class derived from `ObservableObject`. Use the concrete class as `T`, such as `InitializeType<PlayerObject>()`.

#### Plain Classes {#ordinary-observable-classes}

Use `MARKUPUI_SUPPORT_BEGIN`, `MARKUPUI_MEMBER`, and `MARKUPUI_SUPPORT_END` to expose members of an existing class. Send a notification after assigning to a field directly.

```cpp
#include <cstdint>
#include <memory>
#include <string>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final
{
public:
    int32_t Health = 100;
    std::string Name = "Alice";

    MARKUPUI_SUPPORT_BEGIN(PlayerObject)
        MARKUPUI_MEMBER(Health)
        MARKUPUI_MEMBER(Name)
    MARKUPUI_SUPPORT_END()
};
```

After changing a property, send a notification for that property.

```cpp
auto player = std::make_shared<PlayerObject>();

player->Health = 80;
MarkupUI::Binding::NotifyPropertyChanged(*player, "Health");

player->Name = "Grace";
MarkupUI::Binding::NotifyPropertyChanged(*player, "Name");
```

To keep assignment and notification together, provide getters and setters. The example below uses member macros.

```cpp
#include <cstdint>
#include <memory>
#include <string>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final
{
private:
    int32_t Health = 100;
    std::string Name = "Alice";

public:
    int32_t GetHealth() const
    {
        return Health;
    }

    void SetHealth(int32_t value)
    {
        using MarkupUI::Binding::NotifyPropertyChanged;

        if (Health != value)
        {
            Health = value;
            NotifyPropertyChanged(*this, "Health");
        }
    }

    const std::string& GetName() const
    {
        return Name;
    }

    void SetName(const std::string& value)
    {
        using MarkupUI::Binding::NotifyPropertyChanged;

        if (Name != value)
        {
            Name = value;
            NotifyPropertyChanged(*this, "Name");
        }
    }

    MARKUPUI_SUPPORT_BEGIN(PlayerObject)
        MARKUPUI_MEMBER(Health)
        MARKUPUI_MEMBER(Name)
    MARKUPUI_SUPPORT_END()
};

auto player = std::make_shared<PlayerObject>();
player->SetHealth(80);
player->SetName("Grace");
```

### C# implementation

Implement `INotifyPropertyChanged` and raise `PropertyChanged` when a property changes.

!!! important "Notify on the Outer Property"
    A C# `struct` can be stored in a field and exposed to bindings through a property. When a member changes, the containing object raises `PropertyChanged` for the whole property. For example, after changing `FullName.FirstName`, notify `FullName`. The inner member cannot notify the binding independently.

#### Property Changes {#implement-property-change-notification}

```csharp
using System.ComponentModel;

public class PlayerObject : INotifyPropertyChanged
{
    private int _health = 100;
    private string _name = "Alice";

    public event PropertyChangedEventHandler? PropertyChanged;

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

    public string Name
    {
        get { return _name; }
        set
        {
            if (_name != value)
            {
                _name = value;
                PropertyChanged?.Invoke(
                    this, new PropertyChangedEventArgs(nameof(Name)));
            }
        }
    }
}
```

The property setters send notifications when the values change.

```csharp
var player = new PlayerObject();

player.Health = 80;
player.Name = "Grace";
```

## Structures {#observable-struct}

An observable structure is an observable object stored and passed by value. In C++, define it with a `class` or `struct` that meets the binding requirements.

### Definition

=== "C++"

    `Name` uses `MARKUPUI_MEMBER` to expose `FirstName` and `LastName`. If the containing model declares a field `Name FullName;`, expose it with `MARKUPUI_MEMBER(FullName)`. A non-`const`, copy-assignable structure field supports whole-value writeback from a converter. Member paths through a `const` field are read-only.

    ```cpp
    #include <markupui/binding/modeling/object_model.h>
    #include <string>

    struct Name
    {
        std::string FirstName = "Ada";
        std::string LastName = "Lovelace";

        MARKUPUI_SUPPORT_BEGIN(Name)
            MARKUPUI_MEMBER(FirstName)
            MARKUPUI_MEMBER(LastName)
        MARKUPUI_SUPPORT_END()
    };
    ```

=== "C#"

    Define `Name` as a regular `struct` with two public fields, `FirstName` and `LastName`.

    ```csharp
    public struct Name
    {
        public string FirstName;
        public string LastName;
    }
    ```

### Usage

=== "C++"

    In an `ObservableObject` subclass, use `MARKUPUI_PROPERTY` to store `FullName` by value. If you omit the default, `Name` is default-constructed. To register it by hand, use `Property::Register<Profile, Name>("FullName")`. For shared object properties, specify the full pointer type, as in `Property::Register<Profile, std::shared_ptr<Other>>("Other")`.

    ```cpp
    class Profile : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        Profile()
        {
            InitializeType<Profile>();
        }

        MARKUPUI_PROPERTY(Profile, Name, FullName)
    };
    ```

    `GetFullName()` returns `const Name&`. Getters for strings and built-in SDK structures likewise return `const T&`. Copy the current value, edit the copy, and submit it. Here `profile` points to the current data context.

    ```cpp
    Name fullName = profile->GetFullName();
    fullName.FirstName = "Grace";
    profile->SetFullName(fullName);
    ```

=== "C#"

    Expose a `Name FullName` property on the containing object. Its setter accepts the whole structure and raises `PropertyChanged` for `FullName`.

    ```csharp
    using System.ComponentModel;

    public sealed class Profile : INotifyPropertyChanged
    {
        private Name _fullName;

        public event PropertyChangedEventHandler? PropertyChanged;

        public Profile()
        {
            _fullName.FirstName = "Ada";
            _fullName.LastName = "Lovelace";
        }

        public Name FullName
        {
            get => _fullName;
            set
            {
                _fullName = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(FullName)));
            }
        }
    }
    ```

    Reading `FullName` gives you a copy. Edit it, then assign the whole structure back to the property. Here `profile` is the current data context.

    ```csharp
    Name fullName = profile.FullName;
    fullName.FirstName = "Grace";
    profile.FullName = fullName;
    ```

!!! important "Notify on the Whole Structure"
    Members of a by-value structure cannot notify the binding independently. After editing a copy, pass the whole value to the containing object's setter. The containing object sends the notification for `FullName`.

Set a `Profile` instance as the page's [data context](../concepts/data-context.md) to read individual members through `FullName`.

```html
<p>{{ FullName.FirstName }} {{ FullName.LastName }}</p>
```

To edit the full name in one input, bind it to `FullName` and use a [value converter](value-converters.md) that returns a complete `Name`.

## Collection

The collection interface defines conventions for reading, writing, and changing notifications. Built-in observable collections provide implementations of these interfaces. Creating a collection does not require attribute macros. Attribute declarations are only necessary when the collection is made available as an object property.

**Collection Change Notification**

| Operations | Notification Content |
| --- | --- |
| `Add()`, `Insert()` | Element Addition |
| `RemoveAt()` or removal of keys and values | Element Deletion |
| `Set()` Or C# index assignment | Element replacement |
| Moving elements | Changes in the position of elements, requiring the collection to support movement operations. |
| Clearing or resetting the entire content. | Changes to the collection itself. The specific events depend on the collection's implementation. |

Changes to the properties of objects within the collection are still notified by those objects themselves. There is no need to reassign the entire collection. Directly modifying the underlying storage or bypassing the collection operation interface will not trigger corresponding collection events automatically.


### C++ implementation

#### Create observable collections

Use `From()` to move existing containers:

```cpp
#include <algorithm>
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include <markupui/binding/modeling/container.h>

namespace
{
    using MarkupUI::Binding::Modeling::ObservableArray;
    using MarkupUI::Binding::Modeling::ObservableMap;
    using MarkupUI::Binding::Modeling::ObservableSet;
}

std::vector<int32_t> numberValues{10, 20};
std::map<std::string, int32_t> statValues;
std::set<std::string> tagValues;

ObservableArray<int32_t> numbers = ObservableArray<int32_t>::From(std::move(numberValues));
ObservableMap<std::string, int32_t> stats = ObservableMap<std::string, int32_t>::From(std::move(statValues));
ObservableSet<std::string> tags = ObservableSet<std::string>::From(std::move(tagValues));
```

`From()` accepts rvalues. Named containers use `std::move`, while temporary containers can be passed directly.

#### Collection helper functions

`MakeObservableArray`, `MakeObservableMap`, and `MakeObservableSet` can infer the type from the passed elements or containers, simplifying collection creation:

```cpp
#include <algorithm>
#include <cstdint>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <markupui/binding/modeling/container.h>

namespace
{
    using MarkupUI::Binding::Modeling::MakeObservableArray;
    using MarkupUI::Binding::Modeling::MakeObservableMap;
    using MarkupUI::Binding::Modeling::MakeObservableSet;
    using MarkupUI::Binding::Modeling::ObservableArray;
    using MarkupUI::Binding::Modeling::ObservableMap;
    using MarkupUI::Binding::Modeling::ObservableSet;
}

ObservableArray<int32_t> numbers = MakeObservableArray<std::vector>(10, 20);
ObservableMap<std::string, int32_t> stats = MakeObservableMap<std::map<std::string, int32_t>>();
ObservableSet<std::string> tags = MakeObservableSet<std::set<std::string>>();

numbers.Add(30);
stats.Set("Health", 100);
tags.Add("Fire");
```

`MakeObservableArray<std::vector>(10, 20)` infers the type from the elements. When creating an empty collection, specify the complete container type. `MakeObservableMap` and `MakeObservableSet` support moving the corresponding standard containers. The container parameter overload for `MakeObservableArray` applies to containers adapted through `ContainerTraits`. Existing `std::vector` can use the previous `From(std::move(...))`.

When creating nested collections, the helper functions can infer the outer element type from shared sub-collections:

```cpp
#include <algorithm>
#include <cstdint>
#include <memory>
#include <vector>
#include <markupui/binding/modeling/container.h>

namespace
{
    using MarkupUI::Binding::Modeling::MakeObservableArray;
    using MarkupUI::Binding::Modeling::ObservableArray;
}

std::shared_ptr<ObservableArray<int32_t>> firstRow = std::make_shared<ObservableArray<int32_t>>(
    MakeObservableArray<std::vector>(10, 20));

std::shared_ptr<ObservableArray<int32_t>> secondRow = std::make_shared<ObservableArray<int32_t>>(
    MakeObservableArray<std::vector>(30, 40));

ObservableArray<std::shared_ptr<ObservableArray<int32_t>>> rows = MakeObservableArray<std::vector>(firstRow, secondRow);
```

The element type of `rows` is derived from `firstRow` and `secondRow`. The outer collection stores two observable sub-collections through shared pointers.

!!! info "Collection interface"
    Observable collections are based on three interfaces: `IArray<T>`, `IMap<TKey, TValue>`, and `ISet<T>`. The SDK's `ObservableArray<T>`, `ObservableMap<TKey, TValue>`, and `ObservableSet<T>` implement these interfaces respectively.

#### Collection Notifications {#collection-notifications-in-object-properties}

Expose a collection with a property macro or a member macro.

**With ObservableObject**

```cpp
class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    template<class T>
    using ObservableArray = MarkupUI::Binding::Modeling::ObservableArray<T>;

    // Constructor and other properties omitted.

    MARKUPUI_PROPERTY(PlayerObject, ObservableArray<int32_t>, Numbers)
};
```

**Without ObservableObject**

```cpp
class PlayerObject final
{
public:
    template<class T>
    using ObservableArray = MarkupUI::Binding::Modeling::ObservableArray<T>;

    ObservableArray<int32_t> Numbers = ObservableArray<int32_t>::From(std::vector<int32_t>{});

    // Other properties and methods omitted.

    MARKUPUI_SUPPORT_BEGIN(PlayerObject)
        MARKUPUI_MEMBER(Numbers)
    MARKUPUI_SUPPORT_END()
};
```

When you modify a collection through its interface, the collection sends the notification. When you replace the whole collection property, the containing object sends a property change notification.

### C# implementation

For a binding to update when collection contents change, the collection instance must implement `INotifyCollectionChanged`. Use .NET's `ObservableCollection<T>` or the `ObservableHashSet<T>` and `ObservableDictionary<TKey, TValue>` types provided by Markup UI.

#### ObservableCollection: List

`ObservableCollection<T>` These are observable lists provided by .NET:

```csharp
using System.Collections.ObjectModel;

var numbers = new ObservableCollection<int>();
numbers.Add(10);
numbers.Add(20);
numbers[0] = 30;
numbers.RemoveAt(1);
```

When elements are added, deleted, replaced, or moved, the collection sends the `CollectionChanged` notification.

#### ObservableHashSet: collection

`ObservableHashSet<T>` These are observable collections provided by the SDK, without duplicate elements:

```csharp
using MarkupUI.Sdk.Binding;

var tags = new ObservableHashSet<string>();
tags.Add("Fire");
tags.Add("Ice");
tags.Remove("Fire");
```

After adding or removing elements, the set sends a change notification. Repeatedly adding existing elements will not change the set. Sets do not support subscript access.

#### ObservableDictionary:

`ObservableDictionary<TKey, TValue>` These are observable dictionaries provided by the SDK:

```csharp
using MarkupUI.Sdk.Binding;

var stats = new ObservableDictionary<string, int>();
stats.Add("Health", 100);
stats.Add("Mana", 50);
stats["Health"] = 80;
stats.Remove("Mana");
```

When adding, deleting, or replacing the value corresponding to a key, the dictionary sends a change notification. The keys of a Map support string and integer types.

When operating on the above collections through `IList<T>`, `ISet<T>`, or `IDictionary<TKey, TValue>`, the notification is still sent by the corresponding instance. Ordinary `List<T>`, `HashSet<T>`, and `Dictionary<TKey, TValue>` do not provide collection change notifications.

## Object Nesting

When a property references another observable object, a path can read that object's properties, as in `Player.Weapon.Name`. Each object reports changes to its own properties.

- When the weapon name changes, the weapon object notifies `Name`.
- When the player gets a different weapon, the player object notifies `Weapon`.
- After `Weapon` is set to null and the player object notifies the change, the old weapon is no longer available through the path.

Editing `Weapon.Name` keeps the current `Player` data context. The `Weapon` object must send a notification for `Name`.

=== "C++"

    Declare `Weapon` as a `std::shared_ptr<WeaponObject>` property on `PlayerObject`. The player object shares ownership of the weapon.

    ```cpp
    #include <markupui/binding/modeling/object_model.h>
    #include <memory>
    #include <string>

    class WeaponObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        WeaponObject()
        {
            InitializeType<WeaponObject>();
        }

        MARKUPUI_PROPERTY(WeaponObject, std::string, Name, "Sword")
    };

    class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        PlayerObject()
        {
            InitializeType<PlayerObject>();
        }

        MARKUPUI_PROPERTY(PlayerObject, std::shared_ptr<WeaponObject>, Weapon)
    };
    ```

    **Usage**

    ```cpp
    auto weapon = std::make_shared<WeaponObject>();
    auto player = std::make_shared<PlayerObject>();
    player->SetWeapon(weapon);

    // Rename the current weapon. The weapon notifies Name.
    weapon->SetName("Bow");

    // Replace the weapon. The player notifies Weapon.
    player->SetWeapon(std::make_shared<WeaponObject>());
    ```

=== "C#"

    Declare `Weapon` as a `WeaponObject` reference on `PlayerObject`. Each class implements `INotifyPropertyChanged`.

    ```csharp
    using System.ComponentModel;

    public sealed class WeaponObject : INotifyPropertyChanged
    {
        private string _name = "Sword";

        public event PropertyChangedEventHandler? PropertyChanged;

        public string Name
        {
            get => _name;
            set
            {
                if (_name == value)
                {
                    return;
                }

                _name = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Name)));
            }
        }
    }

    public sealed class PlayerObject : INotifyPropertyChanged
    {
        private WeaponObject? _weapon;

        public event PropertyChangedEventHandler? PropertyChanged;

        public WeaponObject? Weapon
        {
            get => _weapon;
            set
            {
                if (ReferenceEquals(_weapon, value))
                {
                    return;
                }

                _weapon = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Weapon)));
            }
        }
    }
    ```

    **Usage**

    ```csharp
    var weapon = new WeaponObject();
    var player = new PlayerObject();
    player.Weapon = weapon;

    // Rename the current weapon. The weapon notifies Name.
    weapon.Name = "Bow";

    // Replace the weapon. The player notifies Weapon.
    player.Weapon = new WeaponObject();
    ```

## Value-based nesting and shared references

First, define `ParentCollection<T>` And `ChildCollection<T>`.  `ObservableArray<T>` Type aliases:

```cpp
#include <algorithm>
#include <cstdint>
#include <memory>
#include <vector>
#include <markupui/binding/modeling/object_model.h>

class CollectionTypes
{
public:
    template<class T>
    using ParentCollection = MarkupUI::Binding::Modeling::ObservableArray<T>;

    template<class T>
    using ChildCollection = MarkupUI::Binding::Modeling::ObservableArray<T>;
};
```

The `CollectionTypes::` prefix is omitted in the following table:

| Nested type | Change notification |
| --- | --- |
| `ParentCollection<ChildCollection<int32_t>>` | `ChildCollection` is processed based on structural values. After modification, the entire collection is submitted. The `ParentCollection` notifies the overall change, but cannot notify the addition or deletion of a specific element within `ChildCollection`. |
| `ParentCollection<std::shared_ptr<ChildCollection<int32_t>>>` | `ChildCollection` can independently notify the addition, deletion, or replacement of a specific element, without requiring the `ParentCollection` to notify the change of the entire collection. |

> `ParentCollection<ChildCollection<int32_t>>` is used as an example only. The SDK does not allow nested collections based on values.

!!! warning "Scope of overall replacement and layout refresh"
    When the embedded collection is processed based on structural values and changes are submitted through overall assignment, the binding receives the change of the entire property. It cannot be understood as the addition or deletion of a specific element within the original collection. Collections that depend on this property need to be reread, which may result in the reconstruction of more elements and an expansion of the layout refresh scope.

    When shared references point to the same observable collection, the collection can send detailed notifications such as addition, deletion, replacement, or movement. Nested lists that are updated frequently should prioritize retaining the collection instance, and the content should be modified through the collection interface.

### Collections in object properties

Collection properties on objects should use the collection type directly. Shared pointer collections should not be used.

```cpp
// Declare the collection property directly in the observable class.
using NumberArray = MarkupUI::Binding::Modeling::ObservableArray<int32_t>;
MARKUPUI_PROPERTY(PlayerObject, NumberArray, Numbers)
```

Unrecommended approach:

```cpp
// Declare the collection property with a shared pointer inside the observable class.
using NumberArray = MarkupUI::Binding::Modeling::ObservableArray<int32_t>;
using SharedNumberArray = std::shared_ptr<NumberArray>;
MARKUPUI_PROPERTY(PlayerObject, SharedNumberArray, Numbers)
```

In C#, collections are usually of reference type. For example, each inner collection in `ObservableCollection<ObservableCollection<int>>` can notify changes independently. When implementing collection interfaces using structures, this behavior cannot be directly applied.

## Nested collections

Nested collections can represent grouped lists, table rows, or tasks and sub-targets. Taking a two-dimensional integer list as an example, the outer layer stores the rows, while the inner layer stores the numbers for each row.

=== "C++"

    The outer layer stores the sub-collections using `std::shared_ptr<NumberArray>`, ensuring that each row maintains its own independent instance and collection notification.

    ```cpp
    #include <algorithm>
    #include <cstdint>
    #include <memory>
    #include <vector>
    #include <markupui/binding/modeling/object_model.h>

    class GridObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        template<class T>
        using ObservableArray = MarkupUI::Binding::Modeling::ObservableArray<T>;

        using NumberArray = ObservableArray<int32_t>;
        using RowArray = ObservableArray<std::shared_ptr<NumberArray>>;

        GridObject()
        {
            InitializeType<GridObject>();

            auto firstRow = std::make_shared<NumberArray>(
                NumberArray::From(std::vector<int32_t>{10, 20}));

            auto secondRow = std::make_shared<NumberArray>(
                NumberArray::From(std::vector<int32_t>{30}));

            auto rows = RowArray::From(std::vector<std::shared_ptr<NumberArray>>{});
            rows.Add(firstRow);
            rows.Add(secondRow);

            SetRows(rows);
        }

        MARKUPUI_PROPERTY(GridObject, RowArray, Rows)
        MARKUPUI_PROPERTY(GridObject, int32_t, SelectedRow, 0)
    };

    auto grid = std::make_shared<GridObject>();
    ```

=== "C#"

    The outer `ObservableCollection<T>` stores references to the inner collections. Each inner collection sends its own notification of changes.

    ```csharp
    using System.Collections.ObjectModel;
    using System.ComponentModel;

    public class GridObject : INotifyPropertyChanged
    {
        private int _selectedRow;

        public event PropertyChangedEventHandler PropertyChanged;

        public GridObject()
        {
            var firstRow = new ObservableCollection<int>();
            firstRow.Add(10);
            firstRow.Add(20);

            var secondRow = new ObservableCollection<int>();
            secondRow.Add(30);

            Rows = new ObservableCollection<ObservableCollection<int>>();
            Rows.Add(firstRow);
            Rows.Add(secondRow);
        }

        public ObservableCollection<ObservableCollection<int>> Rows { get; }

        public int SelectedRow
        {
            get { return _selectedRow; }
            set
            {
                if (_selectedRow != value)
                {
                    _selectedRow = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("SelectedRow"));
                }
            }
        }
    }

    var grid = new GridObject();
    ```

When `grid` is used as the default data context, it is possible to display each row using nested loops.

```html
<div @for="{Rows}">
  <div class="row" @for="{@item}">
    <span>{{ @item }}</span>
  </div>
</div>
```

Output:

```html
<div>
  <div class="row">
    <span>10</span>
    <span>20</span>
  </div>
  <div class="row">
    <span>30</span>
  </div>
</div>
```

When modifying a specific row, the notification is sent by that row’s collection. When adding or removing an entire row, the notification is sent by `Rows`. If a row is an observable object and it provides sub-collections through its properties, then the replacement of those sub-collections should be notified by the corresponding properties of the row object.

## Why is value-based nesting not recommended?

When nesting collections, it is advisable to use `std::shared_ptr` to reference `ChildCollection`. Value-based nesting, which treats `ChildCollection` as a structure, can have the following consequences:

1. **It is not possible to write revert or notify individually.** Binding cannot be written back directly. `ChildCollection` Each of these items can only cover the entire item. `ChildCollection` It notifies changes in the entire item.
2. **Increases the overhead of path reading.** When reading nested items, it is necessary to read the subsequent structure paths from the nearest shared reference node.
3. **May expand the layout refresh range**: Overall notifications may cause more bindings to be re-evaluated, resulting in the reconstruction of more interface elements.

```cpp
class GridObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    // ParentCollection and ChildCollection aliases and initialization are omitted.

    // This by-value nested collection illustrates an unsupported type.
    ParentCollection<ChildCollection<int32_t>> ValueRows;

    // Use a separate shared observable collection for each ChildCollection.
    ParentCollection<std::shared_ptr<ChildCollection<int32_t>>> SharedRows;

    // Property registration and other code are omitted.
};
```

When binding to read the `0` th row and the `2` nd item, the access paths for the two structures are as follows:

```html
<p>{{ ValueRows[0][2] }}</p>
<p>{{ SharedRows[0][2] }}</p>
```

When both pieces of data have the value `30`, the output is:

```html
<p>30</p>
<p>30</p>
```

### If the values are nested, the structure path needs to be read again

`ValueRows[0]` is processed based on the structure value. There is no independent shared reference point for reading. When binding reads the `[2]` nd item again, it needs to start from the nearest shared reference node on the path. Then, retrieve the `ValueRows`, the `0` th `ChildCollection`, and finally read the `2` nd item.

The deeper the nested level, the longer the structure path that needs to be traversed during re-reading. When multiple bindings access different items within the same `ChildCollection`, they also need to go through these structure levels.

### Shared collections can be directly read from the current instance

`SharedRows[0]` is an independent, shared observable collection. After the upper-level path is resolved, the binding can directly read the `2`-nd item from this `ChildCollection`, without having to obtain `SharedRows[0]` again for this item.

| Binding path | Subsequent reading method |
| --- | --- |
| `ValueRows[0][2]` | Re-traversing the structure path `ValueRows[0][2]` from the nearest shared reference node |
| `SharedRows[0][2]` | From the resolved data context `ChildCollection` Directly read from `[2]` |

!!! note "The reading starting point will be updated based on the reference relationships."
    When the `ParentCollection` replaces a certain `ChildCollection`, it is still necessary to notify the corresponding items of the change, so that the binding can be switched to the new `ChildCollection`.

### Value-based nesting does not support overwriting

!!! danger "Elements in value-based subcollections cannot be overwritten."
    In value-based nesting, two-way binding cannot directly set `ValueRows[0][2]`. Instead, the entire `ValueRows[0]` must be overwritten. This corresponding notification indicates a change for the entire item. This may cause more bindings to re-evaluate, resulting in the reconstruction of more interface elements and expanding the scope of layout updates.

    ```html
    <!-- ValueRows uses by-value nesting. Its elements support reading only. -->
    <input type="number" @value="{ValueRows[0][2], mode=twoWay, update=blur}">
    ```

    Changes in the input field cannot be overwritten into `ValueRows[0][2]`.

    **Commands may use unupdated data**.

    If the modification in the input field fails to be written back, the following command will still read the original value of `ValueRows[0][2]`. Do not consider this parameter as the value that the user just entered. Otherwise, incorrect data may be saved or submitted.

    ```html
    <button @onclick="{Save, parameter={ValueRows[0][2]}}">Save</button>
    ```

The shared `ChildCollection` can notify about the addition, deletion, or replacement of specific items, reducing the need for re-reading and updating of irrelevant items. The actual layout still depends on the template structure and the content that changes.

## Range of change notification

- **Nested by value**: `Rows = ValueRows`.
- **Nested with shared reference**: `Rows = SharedRows`.

Operations in the table are uniformly represented as `Rows`. The need for dereferencing the shared pointer is omitted.

| Operations | Nested by value | Shared reference nesting |
| --- | --- | --- |
| `Rows[0][2] = 40` | Change in `Rows[0]` | Notified that `Rows[0][2]` has changed |
| `Rows[0].Add(40)` | Change in `Rows[0]` | New item notified by `Rows[0]` |
| `Rows[0].RemoveAt(2)` | Change in `Rows[0]` | The `2`-nd item has been deleted, as notified by `Rows[0]` |
| `Rows[0] = newRow` | The `0`-th item has been replaced, as notified by `Rows` | The `0`-th item has been replaced, as notified by `Rows` |
| `Rows = newRows` | The `ValueRows` property has changed, notified by `GridObject` | The `GridObject` notifies the `SharedRows` property of changes. |

### Different notification sources within the same path

The path can pass through value-based structures, observable collections, and reference objects. For `Root.ByKey['main'].Rows[0].Target.Health`, it is necessary to choose the notification based on the location of the change.

- After replacing `Root` or modifying the borrowed members within it, the `Root` property notification is released by the data object.
- When replacing `ByKey['main']`, the change in the element corresponding to the key is notified by the observable dictionary. When replacing or moving `Rows[0]`, the change in the corresponding collection is notified by the observable array or list.
- When modifying `Target.Health`, the `Health` property notification is released by `Target`. When replacing the reference to `Target` itself, the notification is released by the property or collection that owns the reference.

When modifying collections, the original observable instance should be used. References within the value-based structure can point to objects or collections with independent notification capabilities, and the notification is still issued by that instance. The nested collections within the Unreal Engine reflection structure are notified through their owners. For detailed operations, see [Unreal Engine Property Binding](../ue/binding/property-binding.md#nested-struct-notifications).

## Shared Objects and Lifecycle

Shared References allow multiple parent objects or collections to use the same child object. Deleting an item from a collection only removes the references held by that collection. Other holders can still retain and use the object.

=== "C++"

    Revert `std::shared_ptr<T>` Maintain the lifecycle of objects or subCollections. Used when a reverse reference to the parent object is required. `std::weak_ptr<T>` Avoid circular strong references. Do not let parent-child objects survive solely relying on strong references held between them.

=== "C#"

    The GC can reclaim circularly referenced objects that are no longer reachable. `WeakReference<T>` is used for references where it is not desired to extend the target object's lifecycle. It is not a necessary measure to avoid circular references.

The failure of a weak reference does not mean that there is a change notification for the property or collection. When it is necessary to remove interface content immediately, the relationship should be terminated through the corresponding property or collection operations, and notifications should be sent accordingly.
