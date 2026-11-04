---
icon: bootstrap/list-ul
---

# 集合绑定

集合绑定通过 `@for` 遍历数据上下文中的集合，为每个数据项生成对应的 HTML 内容。集合项可以是标量值、对象，也可以是另一个集合。

## 支持的集合类型

Markup UI 支持以下三类集合：

| 类型 | 数据组织方式 | 单项访问 | 常见用途 |
| --- | --- | --- | --- |
| `Array`（数组或列表） | 按位置排列的数据项 | 从 `0` 开始的整数下标，如 `Items[0]` | 背包物品、任务列表 |
| `Map`（映射或字典） | 键与值的对应关系，键不可重复 | 按键读取，如 `Stats['Health']` | 按名称或标识查找数据 |
| `Set`（集合） | 不包含重复项的数据集合 | 不支持下标访问，使用遍历读取数据项 | 标签、已解锁能力 |

这些名称表示绑定所识别的集合类型，各平台使用对应的实际容器类型。集合是否能在修改后自动更新界面，还取决于平台是否提供相应的变更通知。

下面每组示例分别定义一个可观察对象，按所选示例创建 `player` 并提供为文档默认数据上下文：

=== "C++"

    ```cpp
    // 以 NumberListObject 为例，其他示例使用对应的类名。
    auto player = std::make_shared<NumberListObject>();
    ```

=== "C#"

    ```csharp
    // 以 NumberListObject 为例，其他示例使用对应的类名。
    var player = new NumberListObject();
    ```

集合自身负责增删通知；对象项的属性设置器负责项内属性通知。C# 示例的集合属性只读，仍可通过集合操作增删内容；需要替换整个集合时，应增加设置器并通知属性变化。

## Array：按位置排列的数据

### 遍历标量项

假设默认数据上下文提供以下数组：

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
            // SetNumbers 函数由 MARKUPUI_PROPERTY 宏生成。
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

在容器上声明 `@for`，其子内容作为每一项的模板。使用 `@item` 读取当前项，`@index` 读取从 `0` 开始的遍历序号：

```html
<ul @for="{Numbers}">
  <li>{{ @index }}: {{ @item }}</li>
</ul>
```

最终输出的 HTML 代码：

```html
<ul>
  <li>0: 10</li>
  <li>1: 20</li>
  <li>2: 30</li>
</ul>
```

`ul` 保留一份，内部的 `li` 为每个数据项生成一份。

### 遍历对象项

假设 `Items` 包含两个对象：

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

每一项的内容以当前对象作为数据上下文，可以直接读取它的属性：

```html
<ul @for="{Items}">
  <li>{{ Name }} × {{ Quantity }}</li>
</ul>
```

最终输出的 HTML 代码：

```html
<ul>
  <li>Sword × 1</li>
  <li>Potion × 3</li>
</ul>
```

### 下标访问

读取特定位置的数据时，使用整数下标，也可以继续访问对象中的属性：

```html
<p>First number: {{ Numbers[0] }}</p>
<p>First item: {{ Items[0].Name }}</p>
```

下标从 `0` 开始，应位于有效范围内。下标代表当前位置；插入、删除或移动数据后，同一下标可能对应不同数据项。

## Map：按键组织的数据

### 遍历键和值

假设默认数据上下文提供以下 Map：

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

Map 循环中，`@key` 是当前键，`@item` 是该键对应的值：

```html
<dl @for="{Stats}">
  <dt>{{ @key }}</dt>
  <dd>{{ @item }}</dd>
</dl>
```

假设本例按 `Health`、`Mana` 的顺序遍历，最终输出的 HTML 代码：

```html
<dl>
  <dt>Health</dt>
  <dd>100</dd>
  <dt>Mana</dt>
  <dd>50</dd>
</dl>
```

Map 的值为对象时，当前数据上下文是该值对象，可以直接使用 `{{ Name }}` 等属性路径；键仍通过 `@key` 读取。

### 按键访问

!!! warning "Map 键的类型限制"
    Map 的键仅支持字符串和整数，不支持布尔值、浮点数、对象或其他类型。

    - **字符串**：`String`。
    - **有符号整数**：`Int8`、`Int16`、`Int32`、`Int64`，分别为 8、16、32、64 位。
    - **无符号整数**：`UInt8`、`UInt16`、`UInt32`、`UInt64`，分别为 8、16、32、64 位。

字符串键使用引号，整数键使用整数。例如：

```html
<!-- Stats 使用字符串键 -->
<p>Health: {{ Stats['Health'] }}</p>

<!-- PlayersById 使用整数键，其值为玩家对象 -->
<p>Player: {{ PlayersById[1001].Name }}</p>
```

键的类型必须与 Map 的实际键类型一致。`Stats['Health']` 按键查找值；整数键 Map 中的 `[0]` 表示键 `0`，不表示遍历到的第一项。

!!! note "Map 的遍历顺序"
    不应假定 Map 按键名或插入顺序排序。需要固定显示顺序时，应由应用提供按所需顺序排列的数据，例如 Array。

## Set：不包含重复项的数据

Set 用于保存不重复的数据项。例如，默认数据上下文提供以下标签集合：

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

使用 `@for` 遍历，并通过 `@item` 读取当前项：

```html
<ul @for="{Tags}">
  <li>{{ @item }}</li>
</ul>
```

假设本例按 `Fire`、`Ice` 的顺序遍历，最终输出的 HTML 代码：

```html
<ul>
  <li>Fire</li>
  <li>Ice</li>
</ul>
```

Set 的数据项为对象时，可以直接访问该对象的属性。数据项是否重复，由集合自身的相等性规则决定。

!!! warning "Set 不支持下标访问"
    `Tags[0]`、`Tags[1]` 等路径无效，不能用来读取 Set 中的第一项或第二项。循环中的 `@index` 只是本次遍历的序号，不表示 Set 提供下标访问，也不应作为数据项的稳定标识。

错误用例：

```html
<!-- 错误：Set 不支持下标访问 -->
<p>{{ Tags[0] }}</p>
```

该路径无法取得有效值，文本插值显示为空：

```html
<p></p>
```

Set 的显示顺序取决于实际集合的遍历顺序，不应依赖固定位置。需要按位置读取或固定排序时，应由应用提供相应的 Array。

## 当前项与集合信息

循环内容中可以使用以下名称：

| 名称 | 含义 |
| --- | --- |
| `@this` | 当前数据上下文，默认是当前项；通过 `@context` 切换后指向新上下文 |
| `@item` | 当前循环的数据项；Map 中是值 |
| `@index` | 当前循环从 `0` 开始的遍历序号 |
| `@key` | Map 当前项的键 |
| `@items` | 当前循环所遍历的集合 |

## 集合属性

目前集合提供 `Count` 属性，Array、Map 和 Set 均支持。

| 属性 | 含义 | 访问权限 |
| --- | --- | --- |
| `Count` | 集合中的数据项数量；Map 中为键值对数量 | 只读 |

通过集合的属性路径读取数量：

```html
<p>Items: {{ Items.Count }}</p>
<p>Stats: {{ Stats.Count }}</p>
<p>Tags: {{ Tags.Count }}</p>
```

空集合的 `Count` 为 `0`。集合值为 `null` 时，无法读取 `Count`，不应将这种情况与空集合混同。

循环内部可以通过 `@items.Count` 读取当前集合的总项数：

```html
<ul @for="{Items}">
  <li>{{ Name }} / {{ @items.Count }}</li>
</ul>
```

`Count` 是集合总数，不是当前项的序号。集合数量变化后，需要相应的属性变更通知才能更新绑定到 `Count` 的内容。

## 模板与嵌套集合

### 不增加容器元素

如果不需要额外容器，可以将 `@for` 写在 `template` 上。`template` 自身不生成显示元素，内部内容按集合项重复：

```html
<ul>
  <li>Inventory</li>
  <template @for="{Items}">
    <li>{{ Name }} × {{ Quantity }}</li>
  </template>
</ul>
```

这里的固定标题只显示一次，后续条目按 `Items` 生成。

### 嵌套遍历与别名

集合项可以包含另一个集合。例如，`Groups` 的每个对象都有 `Name` 和 `Items`。使用 `@item-as` 为外层当前项声明别名，便于在内层访问：

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

内层的 `Name` 来自当前物品，`@group.Name` 来自所属分组。内层 `@item`、`@index` 和 `@items` 对应内层循环。

集合项本身就是集合时，可以使用 `@for="{@this}"` 遍历当前集合项。

## 集合变化与界面更新

集合结构变化、集合项的属性变化与替换整个集合，需要分别提供对应通知：

| 变化 | 示例 | 更新方式 |
| --- | --- | --- |
| 集合结构变化 | Array 插入或移除项、Map 更新某个键的值、Set 添加或移除项 | 集合发出相应变化通知，更新对应的重复内容 |
| 集合项的属性变化 | 将某个物品的 `Quantity` 从 `1` 改为 `2` | 物品对象通知 `Quantity` 变化，更新该项的文本 |
| 集合属性替换 | 将数据上下文的 `Items` 替换为另一个集合 | 数据上下文通知 `Items` 变化，绑定转向新集合 |

Array 的移动通知会更新显示顺序，相关 `@index` 也随位置变化。Map 和 Set 的变化按其自身支持的操作处理，不能套用 Array 的下标规则。

!!! note "普通容器不等于可通知集合"
    能读取和遍历集合，并不代表直接修改容器后界面一定自动更新。应用应使用平台支持的集合通知方式；集合项对象的属性变化也需要单独通知。详细信息请阅读各平台文档。

## 空集合

集合为空或集合值为 `null` 时，循环不生成任何项。普通容器仍保留，容器内声明的循环模板不作为占位内容显示：

```html
<!-- Items 为空时 -->
<ul @for="{Items}">
  <li>{{ Name }}</li>
</ul>
```

最终输出的 HTML 代码：

```html
<ul></ul>
```
