---
icon: bootstrap/list-ul
---

# Collection Binding

The collection binding uses `@for` to iterate through the collections in the data context, generating corresponding HTML content for each data item. The collection items can be scalar values, objects, or another collection.

## Supported collection types

The Markup UI supports the following three types of collections:

| Types | Data organization methods | Single-item access | Common uses |
| --- | --- | --- | --- |
| `Array` (arrays or lists) | Data items arranged by position | Integer index starting from `0`, such as `Items[0]` | Backpack items, task list |
| `Map` (mapping or dictionary) | The correspondence between keys and values. Keys must be unique | Retrieved by key, such as `Stats['Health']` | Search for data by name or identifier |
| `Set` (collection) | A data collection without duplicate entries | Subscript access is not supported. Data items are read using traversal | Tags, unlocked capabilities |

These names indicate the collection types recognized by the binding mechanism. Each platform uses the corresponding actual container type. Whether the interface automatically updates after modifications also depends on whether the platform provides corresponding change notifications.

Each of the following examples defines an observable object. Create a `player` based on the selected example and provide it as the default data context for the documentation:

=== "C++"

    ```cpp
    // This example uses NumberListObject. Use the corresponding class name in other examples.
    auto player = std::make_shared<NumberListObject>();
    ```

=== "C#"

    ```csharp
    // This example uses NumberListObject. Use the corresponding class name in other examples.
    var player = new NumberListObject();
    ```

The collection itself is responsible for adding and removing notifications. The property setter of the object items is responsible for notifying the properties within the items. In the C# example, the collection properties are read-only, but it is still possible to add or remove content through collection operations. When it is necessary to replace the entire collection, a setter should be added to notify the property changes.

## Array: Data arranged by position

### Iterate over scalar items

Assume that the default data context provides the following array:

=== "C++"

    ```cpp
    #include <algorithm>
    #include <cstdint>
    #include <memory>
    #include <string>
    #include <vector>
    #include <map>
    #include <set>
    #include <markupui/binding/modeling/object_model.h>

    class NumberListObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        using NumberArray = MarkupUI::Binding::Modeling::ObservableArray<int32_t>;

        NumberListObject()
        {
            InitializeType<NumberListObject>();
            // The MARKUPUI_PROPERTY macro generates SetNumbers.
            SetNumbers(NumberArray::From(std::vector<int32_t>{10, 20, 30}));
        }

        MARKUPUI_PROPERTY(NumberListObject, NumberArray, Numbers)
    };
    ```

=== "C#"

    ```csharp
    using System.Collections.ObjectModel;
    using System.ComponentModel;

    public class NumberListObject : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public ObservableCollection<int> Numbers { get; } = new ObservableCollection<int> { 10, 20, 30 };
    }
    ```

Declare `@for` on the container, and its content serves as the template for each item. Use `@item` to read the current item, and `@index` to read the traversal index starting from `0`.

```html
<ul @for="{Numbers}">
  <li>{{ @index }}: {{ @item }}</li>
</ul>
```

The final output HTML code:

```html
<ul>
  <li>0: 10</li>
  <li>1: 20</li>
  <li>2: 30</li>
</ul>
```

Keep a copy of `ul`, and generate a copy of `li` for each data item.

### Traverse the object items

Assume that `Items` contains two objects:

=== "C++"

    ```cpp
    #include <algorithm>
    #include <cstdint>
    #include <memory>
    #include <string>
    #include <vector>
    #include <map>
    #include <set>
    #include <markupui/binding/modeling/object_model.h>

    class ItemObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        ItemObject() { InitializeType<ItemObject>(); }

        MARKUPUI_PROPERTY(ItemObject, std::string, Name, "Sword")
        MARKUPUI_PROPERTY(ItemObject, int32_t, Quantity, 1)
    };

    class ItemListObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        using ItemArray = MarkupUI::Binding::Modeling::ObservableArray<std::shared_ptr<ItemObject>>;

        ItemListObject()
        {
            InitializeType<ItemListObject>();
            auto sword = std::make_shared<ItemObject>();
            auto potion = std::make_shared<ItemObject>();
            potion->SetName("Potion");
            potion->SetQuantity(3);
            SetItems(ItemArray::From(std::vector<std::shared_ptr<ItemObject>>{sword, potion}));
        }

        MARKUPUI_PROPERTY(ItemListObject, ItemArray, Items)
    };
    ```

=== "C#"

    ```csharp
    using System.Collections.ObjectModel;
    using System.ComponentModel;

    public class ItemObject : INotifyPropertyChanged
    {
        private string _name = "Sword";
        private int _quantity = 1;

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

        public int Quantity
        {
            get { return _quantity; }
            set
            {
                if (_quantity != value)
                {
                    _quantity = value;
                    PropertyChanged?.Invoke(
                        this, new PropertyChangedEventArgs("Quantity"));
                }
            }
        }
    }

    public class ItemListObject : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public ObservableCollection<ItemObject> Items { get; } =
            new ObservableCollection<ItemObject>
            {
                new ItemObject { Name = "Sword", Quantity = 1 },
                new ItemObject { Name = "Potion", Quantity = 3 }
            };
    }
    ```

The content of each item uses the current object as the data context, and its properties can be read directly:

```html
<ul @for="{Items}">
  <li>{{ Name }} × {{ Quantity }}</li>
</ul>
```

The final output HTML code:

```html
<ul>
  <li>Sword × 1</li>
  <li>Potion × 3</li>
</ul>
```

### Subscript access

When reading data at a specific position, use integer subscripts, and you can also continue to access properties within the object:

```html
<p>First number: {{ Numbers[0] }}</p>
<p>First item: {{ Items[0].Name }}</p>
```

Subscripts start from `0`, and must be within the valid range. Subscripts represent the current position. After inserting, deleting, or moving data, the same subscript may correspond to different data items.

## Map: Data organized by keys

### Traverse the keys and values

Assume that the default data context provides the following Map:

=== "C++"

    ```cpp
    #include <algorithm>
    #include <cstdint>
    #include <memory>
    #include <string>
    #include <vector>
    #include <map>
    #include <set>
    #include <markupui/binding/modeling/object_model.h>

    class StatsObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        using StatMap = MarkupUI::Binding::Modeling::ObservableMap<std::string, int32_t>;

        StatsObject()
        {
            InitializeType<StatsObject>();
            SetStats(StatMap::From(std::map<std::string, int32_t>{{"Health", 100}, {"Mana", 50}}));
        }

        MARKUPUI_PROPERTY(StatsObject, StatMap, Stats)
    };
    ```

=== "C#"

    ```csharp
    using MarkupUI.Sdk.Binding;
    using System.ComponentModel;

    public class StatsObject : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public ObservableDictionary<string, int> Stats { get; } = new ObservableDictionary<string, int>
        {
            { "Health", 100 },
            { "Mana", 50 }
        };
    }
    ```

During the Map iteration, `@key` is the current key, and `@item` is the value corresponding to that key:

```html
<dl @for="{Stats}">
  <dt>{{ @key }}</dt>
  <dd>{{ @item }}</dd>
</dl>
```

Suppose this example iterates in the order of `Health` and `Mana`. The final HTML code output is as follows:

```html
<dl>
  <dt>Health</dt>
  <dd>100</dd>
  <dt>Mana</dt>
  <dd>50</dd>
</dl>
```

When the value of the Map is an object, the current data context is that object. You can directly use property paths like `{{ Name }}`. Keys are still retrieved using `@key`.

### Accessing by key

!!! warning "Type restrictions of Map keys"
    The keys of a Map can only be strings and integers. Boolean values, floating-point numbers, objects, or other types are not supported.

    - **Strings**: `String`.
    - **Signed integers**: `Int8`, `Int16`, `Int32`, `Int64`, which are 8, 16, 32, and 64-bit integers respectively.
    - **Unsigned integers**: `UInt8`, `UInt16`, `UInt32`, `UInt64`, which are 8, 16, 32, and 64-bit unsigned integers respectively.

String keys should be enclosed in quotes, while integer keys should be written as integers. For example:

```html
<!-- Stats uses string keys. -->
<p>Health: {{ Stats['Health'] }}</p>

<!-- PlayersById uses integer keys and stores player objects as values. -->
<p>Player: {{ PlayersById[1001].Name }}</p>
```

The type of the key must be consistent with the actual type of the key in the Map. `Stats['Health']` is used to retrieve the value. The integer key `[0]` in the Map represents the key `0`, and does not refer to the first item encountered.

!!! note "The traversal order of a Map"
    It should not be assumed that the keys of a Map are sorted in a certain order. When a fixed display order is required, the application should provide data arranged in the desired order, such as an Array.

## Set: Data that does not contain duplicate items

Sets are used to store non-duplicate data items. For example, the default data context provides the following set of tags:

=== "C++"

    ```cpp
    #include <algorithm>
    #include <cstdint>
    #include <memory>
    #include <string>
    #include <vector>
    #include <map>
    #include <set>
    #include <markupui/binding/modeling/object_model.h>

    class TagListObject final : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        using TagSet = MarkupUI::Binding::Modeling::ObservableSet<std::string>;

        TagListObject()
        {
            InitializeType<TagListObject>();
            SetTags(TagSet::From(std::set<std::string>{"Fire", "Ice"}));
        }

        MARKUPUI_PROPERTY(TagListObject, TagSet, Tags)
    };
    ```

=== "C#"

    ```csharp
    using MarkupUI.Sdk.Binding;
    using System.ComponentModel;

    public class TagListObject : INotifyPropertyChanged
    {
        public event PropertyChangedEventHandler PropertyChanged;

        public ObservableHashSet<string> Tags { get; } = new ObservableHashSet<string> { "Fire", "Ice" };
    }
    ```

Use `@for` to iterate through and `@item` to access the current item:

```html
<ul @for="{Tags}">
  <li>{{ @item }}</li>
</ul>
```

Assuming that the iteration is carried out in the order of `Fire` and `Ice`, the final HTML code produced will be:

```html
<ul>
  <li>Fire</li>
  <li>Ice</li>
</ul>
```

When the data items in a Set are objects, it is possible to directly access the properties of those objects. Whether the data items are unique is determined by the equality rules of the set itself.

!!! warning "Sets do not support subscript access."
    Paths such as `Tags[0]` and `Tags[1]` are invalid and cannot be used to access the first or second item in the Set. `@index` in the loop is merely the index number of the current iteration. It does not represent an index for accessing items in the Set, nor should it be used as a stable identifier for data items.

Incorrect usage cases:

```html
<!-- Invalid because Set does not support indexing. -->
<p>{{ Tags[0] }}</p>
```

This path cannot yield valid values, and the text interpolation results in an empty display.

```html
<p></p>
```

The display order of Set depends on the actual iteration order of the collection. It should not rely on fixed positions. When reading items by position or maintaining a fixed order is required, the application should provide an appropriate Array.

## Information about the current item and the collection

The following names can be used in the loop content:

| Names | Meaning |
| --- | --- |
| `@this` | The current data context, by default it refers to the current item. It points to the new context when switched through `@context` |
| `@item` | The data item being processed in the current loop. In a Map, it represents a value |
| `@index` | The traversal index of the current loop, starting from `0` |
| `@key` | The key of the current item in the Map |
| `@items` | The collection that is being traversed by the current loop |

## The property of the collection

Currently, the collection provides the `Count` property, which is supported by Array, Map, and Set.

| Property | Meaning | Access rights |
| --- | --- | --- |
| `Count` | The number of data items in the collection. In Map, it represents the number of key-value pairs. | Read-only |

The number can be read through the collection's property path:

```html
<p>Items: {{ Items.Count }}</p>
<p>Stats: {{ Stats.Count }}</p>
<p>Tags: {{ Tags.Count }}</p>
```

The `Count` of an empty collection is `0`. When the collection value is `null`, it is not possible to read the `Count`. This situation should not be confused with an empty collection.

Within the loop, you can read the total number of items in the current collection using `@items.Count`:

```html
<ul @for="{Items}">
  <li>{{ Name }} / {{ @items.Count }}</li>
</ul>
```

`Count` represents the total number of items in the collection, not the index of the current item. When the number of items in the collection changes, it is necessary to notify the extension property to update the content bound to `Count`.

## Templates and nested collections

### No additional container elements are added

If no additional container is needed, `@for` can be placed directly on `template`. `template` itself does not generate any visible elements. The internal content is repeated based on the items in the collection.

```html
<ul>
  <li>Inventory</li>
  <template @for="{Items}">
    <li>{{ Name }} × {{ Quantity }}</li>
  </template>
</ul>
```

The fixed title is displayed only once, and subsequent entries are generated based on `Items`.

### Nested traversal and aliases

Collection items can contain another collection. For example, each object in `Groups` has `Name` and `Items`. Using `@item-as` to declare an alias for the outer item makes it easier to access the inner item:

```html
<section @for="{Groups}" @item-as="group">
  <article>
    <h2>{{ Name }}</h2>
    <ul @for="{Items}">
      <li>{{ @group.Name }}: {{ Name }}</li>
    </ul>
  </article>
</section>
```

The `Name` of the inner item comes from the current item, while `@group.Name` comes from the group it belongs to. The `@item`, `@index`, and `@items` in the inner structure correspond to the inner loop.

When a collection item itself is a collection, you can use `@for="{@this}"` to iterate through the current collection item.

## Changes in collections and updates to the interface

Changes in the collection structure, changes in the properties of collection items, and replacing the entire collection require separate notifications:

| Changes | Example | Update method |
| --- | --- | --- |
| Changes in the collection structure | Insertion or removal of items in the Array, updating the value of a key in the Map, adding or removing items from the Set | The collection sends corresponding change notifications, updating the corresponding duplicate content |
| Changes in the properties of collection items | Changing the `Quantity` of a certain item from `1` to `2` | The item object notifies the change in `Quantity`, updating the text of that item |
| Replacement of collection properties | Replace the `Items` in the data context with another collection | The data context notifies changes to `Items`, and the binding is redirected to the new collection |

Notifications of array movements will update the display order, and the relevant `@index` will also change accordingly. Changes in Map and Set are handled according to their own supported operations, and the subscript rules of Array cannot be applied.

!!! note "A regular container is not equal to a notifyable collection"
    Being able to read and traverse collections does not mean that the interface will automatically update after the container is directly modified. Applications should use the collection notification methods supported by the platform. Changes in the properties of collection item objects also need to be notified separately. For more details, please refer to the documentation of each platform.

## Empty collection

When the collection is empty or its value is `null`, the loop does not generate any items. The ordinary container remains intact, and the loop template declared within the container is not displayed as placeholder content.

```html
<!-- When Items is empty -->
<ul @for="{Items}">
  <li>{{ Name }}</li>
</ul>
```

The final output HTML code:

```html
<ul></ul>
```
