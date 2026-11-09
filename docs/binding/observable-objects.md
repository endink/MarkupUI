---
icon: bootstrap/diagram-3
---

# 可观察对象

可观察对象的属性可以提供其他对象或集合，集合项也可以继续包含对象或集合。例如，背包对象包含物品列表，每个物品包含属性对象；任务列表中的每个任务又包含自己的目标列表。

!!! note "平台原生类型"
    各平台插件还支持各自的原生类型，例如 Unreal Engine 的 `UObject` 和 `TArray`。具体支持范围与使用方式请参阅各平台文档。

嵌套方式决定 SDK 的变更通知粒度和绑定路径的读取起点。类型和语言表示见[数据类型](data-types.md)，集合的 HTML 遍历语法见[集合绑定](collection-binding.md)。

## 对象

可观察对象提供可绑定属性，并在属性变化时发送通知。C++ 可以使用 `ObservableObject`、为已有类添加宏支持，或直接实现 `MarkupUI::Binding::IObject`；C# 使用 `INotifyPropertyChanged`。

**属性更改通知**

| 创建方式 | 更改方式 | 通知 |
| --- | --- | --- |
| `ObservableObject` 与属性宏 | `player->SetHealth(80)` | 自动发送 |
| `ObservableObject` 与手动注册属性 | `SetValue(HealthProperty, value)` | 自动发送 |
| 成员宏 | `player->Health = 80` | 随后调用 `NotifyPropertyChanged` |
| 自定义 `IObject` | 自定义属性设置函数 | 由实现发送属性事件 |
| C# `INotifyPropertyChanged` | `player.Health = 80` | 由设置器触发 `PropertyChanged` |

通知名称必须与绑定属性名一致。直接修改字段不会自动等同于属性通知。


### C++ 实现

#### ObservableObject

继承 `ObservableObject`，使用 `MARKUPUI_PROPERTY` 声明属性并生成访问函数。调用生成的设置函数时，SDK 负责发送属性变更通知。

```cpp
#include <cstdint>
#include <memory>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    PlayerObject()
    {
        InitializeType<PlayerObject>();
    }

    MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 100)
    MARKUPUI_PROPERTY(PlayerObject, int32_t, Mana, 50)
};
```

下面是不使用属性宏的等效代码：

```cpp
#include <cstdint>
#include <memory>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    using Property = MarkupUI::Binding::Modeling::Property;

    inline static const Property HealthProperty =
        Property::Register<PlayerObject, int32_t>("Health", 100);

    inline static const Property ManaProperty =
        Property::Register<PlayerObject, int32_t>("Mana", 50);

    PlayerObject()
    {
        InitializeType<PlayerObject>();
    }

    int32_t GetHealth() const
    {
        return *GetValue<int32_t>(HealthProperty);
    }

    void SetHealth(int32_t value)
    {
        SetValue(HealthProperty, value);
    }

    int32_t GetMana() const
    {
        return *GetValue<int32_t>(ManaProperty);
    }

    void SetMana(int32_t value)
    {
        SetValue(ManaProperty, value);
    }
};
```

通过设置函数更新属性时，自动发送属性更改通知：

```cpp
auto player = std::make_shared<PlayerObject>();

player->SetHealth(80); // 通知 Health 变化。
player->SetMana(40);   // 通知 Mana 变化。
```

!!! note "必须初始化类型"
    继承 `ObservableObject` 时，必须在构造函数中调用 `InitializeType<T>()`，其中 `T` 为当前类的类型，例如 `InitializeType<PlayerObject>()`。

#### 普通可观察类

已有类可以通过 `MARKUPUI_SUPPORT_BEGIN`、`MARKUPUI_MEMBER` 和 `MARKUPUI_SUPPORT_END` 宏公开成员，不必改变继承关系。成员赋值后需要主动通知。

```cpp
#include <cstdint>
#include <memory>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final
{
public:
    int32_t Health = 100;
    int32_t Mana = 50;

    MARKUPUI_SUPPORT_BEGIN(PlayerObject)
        MARKUPUI_MEMBER(Health)
        MARKUPUI_MEMBER(Mana)
    MARKUPUI_SUPPORT_END()
};
```

更新属性后，手动发送属性更改通知：

```cpp
auto player = std::make_shared<PlayerObject>();

player->Health = 80;
MarkupUI::Binding::NotifyPropertyChanged(*player, "Health");

player->Mana = 40;
MarkupUI::Binding::NotifyPropertyChanged(*player, "Mana");
```

推荐使用 Get/Set 包装属性访问，将赋值和变更通知集中在 Set 中，避免调用方遗漏通知。使用成员宏时可以这样编写：

```cpp
#include <cstdint>
#include <memory>
#include <markupui/binding/modeling/object_model.h>

class PlayerObject final
{
private:
    int32_t Health = 100;
    int32_t Mana = 50;

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

    int32_t GetMana() const
    {
        return Mana;
    }

    void SetMana(int32_t value)
    {
        using MarkupUI::Binding::NotifyPropertyChanged;

        if (Mana != value)
        {
            Mana = value;
            NotifyPropertyChanged(*this, "Mana");
        }
    }

    MARKUPUI_SUPPORT_BEGIN(PlayerObject)
        MARKUPUI_MEMBER(Health)
        MARKUPUI_MEMBER(Mana)
    MARKUPUI_SUPPORT_END()
};

auto player = std::make_shared<PlayerObject>();
player->SetHealth(80);
player->SetMana(40);
```

### C# 实现

相比 C++，C# 的实现更简单：类只需实现 `INotifyPropertyChanged` 接口，并在属性变化时触发 `PropertyChanged` 事件，即可作为可观察对象使用。

#### 实现属性变更通知

```csharp
using System.ComponentModel;

public class PlayerObject : INotifyPropertyChanged
{
    private int _health = 100;
    private int _mana = 50;

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
                    this, new PropertyChangedEventArgs("Health"));
            }
        }
    }

    public int Mana
    {
        get { return _mana; }
        set
        {
            if (_mana != value)
            {
                _mana = value;
                PropertyChanged?.Invoke(
                    this, new PropertyChangedEventArgs("Mana"));
            }
        }
    }
}
```

通过属性设置器更新属性时，发送属性更改通知：

```csharp
var player = new PlayerObject();

player.Health = 80;
player.Mana = 40;
```

## 集合

集合接口定义读取、写入和变更通知的约定；内置可观察集合提供这些接口的实现。创建集合不需要属性宏，只有将集合公开为对象属性时才涉及属性声明。

**集合更改通知**

| 操作 | 通知内容 |
| --- | --- |
| `Add()`、`Insert()` | 元素新增 |
| `RemoveAt()` 或删除键、值 | 元素删除 |
| `Set()` 或 C# 索引赋值 | 元素替换 |
| 移动元素 | 元素位置变化，要求集合支持移动操作 |
| 清空或整体重置内容 | 集合变化；具体事件取决于集合实现 |

集合中对象的属性变化仍由该对象通知，不用将整个集合重新赋值。直接修改底层存储或绕过集合操作接口，不会自动产生相应的集合事件。


### C++ 实现

#### 创建可观察集合

使用 `From()` 移动已有容器：

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

`From()` 接收右值；命名容器使用 `std::move`，临时容器可以直接传入。

#### 集合帮助器函数

`MakeObservableArray`、`MakeObservableMap` 和 `MakeObservableSet` 可以从传入的元素或容器推导类型，简化集合创建：

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

`MakeObservableArray<std::vector>(10, 20)` 从元素推导类型；创建空集合时指定完整容器类型。`MakeObservableMap` 和 `MakeObservableSet` 支持移动对应的标准容器；`MakeObservableArray` 的容器参数重载适用于通过 `ContainerTraits` 适配的容器，已有 `std::vector` 可使用前面的 `From(std::move(...))`。

创建嵌套集合时，帮助器可以从共享子集合推导外层元素类型：

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

`rows` 的元素类型由 `firstRow` 和 `secondRow` 推导，外层集合通过共享指针保存两个可观察子集合。

!!! info "集合接口"
    可观察集合基于 `IArray<T>`、`IMap<TKey, TValue>` 和 `ISet<T>` 三个接口。SDK 的 `ObservableArray<T>`、`ObservableMap<TKey, TValue>` 和 `ObservableSet<T>` 分别实现对应接口。

#### 对象属性中的集合通知

集合可以通过属性宏或成员宏公开：

```cpp
class PlayerObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    template<class T>
    using ObservableArray = MarkupUI::Binding::Modeling::ObservableArray<T>;

    // 省略构造函数和其他属性。

    MARKUPUI_PROPERTY(PlayerObject, ObservableArray<int32_t>, Numbers)
};
```

```cpp
class PlayerObject final
{
public:
    template<class T>
    using ObservableArray = MarkupUI::Binding::Modeling::ObservableArray<T>;

    ObservableArray<int32_t> Numbers = ObservableArray<int32_t>::From(std::vector<int32_t>{});

    // 省略其他属性和成员函数。

    MARKUPUI_SUPPORT_BEGIN(PlayerObject)
        MARKUPUI_MEMBER(Numbers)
    MARKUPUI_SUPPORT_END()
};
```

通过集合接口修改内容时，由集合通知；替换整个集合属性时，由对象通知属性变化。

### C# 实现

#### ObservableCollection：列表

`ObservableCollection<T>` 是 .NET 提供的可观察列表：

```csharp
using System.Collections.ObjectModel;

var numbers = new ObservableCollection<int>();
numbers.Add(10);
numbers.Add(20);
numbers[0] = 30;
numbers.RemoveAt(1);
```

添加、删除、替换和移动元素时，集合发送 `CollectionChanged` 通知。

#### ObservableHashSet：集合

`ObservableHashSet<T>` 是 SDK 提供的可观察集合，不包含重复元素：

```csharp
using MarkupUI.Sdk.Binding;

var tags = new ObservableHashSet<string>();
tags.Add("Fire");
tags.Add("Ice");
tags.Remove("Fire");
```

添加或删除元素后，集合发送变更通知；重复添加已有元素不会改变集合。Set 不支持下标访问。

#### ObservableDictionary：字典

`ObservableDictionary<TKey, TValue>` 是 SDK 提供的可观察字典：

```csharp
using MarkupUI.Sdk.Binding;

var stats = new ObservableDictionary<string, int>();
stats.Add("Health", 100);
stats.Add("Mana", 50);
stats["Health"] = 80;
stats.Remove("Mana");
```

添加、删除或替换键对应的值时，字典发送变更通知。Map 的键支持字符串和整数类型。

通过 `IList<T>`、`ISet<T>` 或 `IDictionary<TKey, TValue>` 引用操作以上集合时，仍由对应实例发送通知。普通 `List<T>`、`HashSet<T>` 和 `Dictionary<TKey, TValue>` 不提供集合变更通知。

## 对象嵌套

对象属性引用另一个可观察对象时，可以沿属性路径继续访问，例如 `Player.Weapon.Name`。每一层对象负责通知自己的属性变化：

- 修改武器名称，由武器对象通知 `Name` 变化。
- 替换玩家的武器，由玩家对象通知 `Weapon` 变化。
- 将 `Weapon` 设置为空并通知后，绑定不能再通过原路径读取旧武器。

替换对象与修改对象内部属性是两种操作。修改 `Weapon.Name` 不需要将整个 `Player` 重新设置为数据上下文，但 `Weapon` 必须能够通知 `Name` 的变化。

=== "C++"

    使用 `std::shared_ptr<WeaponObject>` 提供嵌套对象，SDK 订阅武器对象的属性变化。

    ```cpp
    // PlayerObject 和 WeaponObject 的定义见“基础绑定”。
    auto weapon = std::make_shared<WeaponObject>();
    auto player = std::make_shared<PlayerObject>();
    player->SetWeapon(weapon);

    // 修改当前武器，由武器对象发送 Name 属性通知。
    weapon->SetName("Bow");

    // 替换武器，由玩家对象发送 Weapon 属性通知。
    player->SetWeapon(std::make_shared<WeaponObject>());
    ```

=== "C#"

    武器对象通过 `INotifyPropertyChanged` 通知内部属性变化；玩家对象通过同一接口通知武器替换。

    ```csharp
    // PlayerObject 和 WeaponObject 的定义见“基础绑定”。
    var weapon = new WeaponObject();
    var player = new PlayerObject();
    player.Weapon = weapon;

    // 修改当前武器，由武器对象发送 Name 属性通知。
    weapon.Name = "Bow";

    // 替换武器，由玩家对象发送 Weapon 属性通知。
    player.Weapon = new WeaponObject();
    ```

上面的对象定义及完整属性设置器见[基础绑定](basic-binding.md)。

## 按值嵌套与共享引用

先定义 `ParentCollection<T>` 和 `ChildCollection<T>`，分别表示外层集合和内层集合。两者都是 `ObservableArray<T>` 的类型别名：

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

下表省略 `CollectionTypes::` 前缀：

| 嵌套类型 | 变更通知 |
| --- | --- |
| `ParentCollection<ChildCollection<int32_t>>` | `ChildCollection` 按结构值处理，修改后整体提交；由 `ParentCollection` 通知该项整体变化，不能通知 `ChildCollection` 内某个整数的增删 |
| `ParentCollection<std::shared_ptr<ChildCollection<int32_t>>>` | `ChildCollection` 可以独立通知其中某个整数的新增、删除或替换，无需由 `ParentCollection` 通知整项变化 |

> `ParentCollection<ChildCollection<int32_t>>` 仅作示例，SDK 不允许按值嵌套集合。

!!! warning "整体替换与布局刷新范围"
    当内嵌集合按结构值处理、通过整体赋值提交变化时，绑定收到的是整个属性变化，不能将其理解为原集合中的某一项发生了增删。依赖该属性的集合显示需要重新读取，可能重建更多元素并扩大布局刷新范围。

    共享引用指向同一可观察集合时，集合可以发送新增、删除、替换或移动等细粒度通知。频繁更新的嵌套列表应优先保留集合实例，通过集合接口修改内容。

### 对象属性中的集合

对象上的集合属性应直接使用集合类型，不应使用共享指针集合。

```cpp
// 推荐：在可观察对象类内直接声明集合属性。
using NumberArray = MarkupUI::Binding::Modeling::ObservableArray<int32_t>;
MARKUPUI_PROPERTY(PlayerObject, NumberArray, Numbers)
```

不推荐的写法：

```cpp
// 在可观察对象类内使用共享指针声明集合属性。
using NumberArray = MarkupUI::Binding::Modeling::ObservableArray<int32_t>;
using SharedNumberArray = std::shared_ptr<NumberArray>;
MARKUPUI_PROPERTY(PlayerObject, SharedNumberArray, Numbers)
```

C# 集合通常是引用类型，例如 `ObservableCollection<ObservableCollection<int>>` 中的每个内层集合都可以独立通知变化。使用结构体实现集合接口时，不能直接套用这一行为。

## 集合嵌套

嵌套集合可以表达分组列表、表格行或任务与子目标。下面以二维整数列表为例，外层保存行，内层保存每一行的数字。

=== "C++"

    外层通过 `std::shared_ptr<NumberArray>` 保存子集合，使每一行保持独立实例及自己的集合通知。

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

    外层 `ObservableCollection<T>` 保存内层集合的引用。每个内层集合分别发送自己的变更通知。

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

将 `grid` 作为默认数据上下文后，可以用嵌套循环显示各行：

```html
<div @for="{Rows}">
  <div class="row" @for="{@item}">
    <span>{{ @item }}</span>
  </div>
</div>
```

输出：

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

修改某一行时，由该行集合通知；新增或移除一整行时，由 `Rows` 通知。若一行是可观察对象，并通过其属性提供子集合，则替换该子集合应由行对象通知对应属性变化。

## 为什么不推荐按值嵌套

集合嵌套时应使用 `std::shared_ptr` 引用 `ChildCollection`。按值嵌套、将 `ChildCollection` 作为结构处理，会有以下影响：

1. **不能单项写回或通知**：绑定不能直接写回 `ChildCollection` 中的某一项，只能整体覆盖 `ChildCollection`，并通知整项变化。
2. **增加路径读取开销**：读取嵌套项时，需要从最近的共享引用节点重新读取后续结构路径。
3. **可能扩大布局刷新范围**：整体通知可能使更多绑定重新求值，并重建更多界面元素。

```cpp
class GridObject final : public MarkupUI::Binding::Modeling::ObservableObject
{
public:
    // 省略 ParentCollection、ChildCollection 类型别名及初始化代码。

    // 按值嵌套仅用于对比，SDK 不允许此集合类型。
    ParentCollection<ChildCollection<int32_t>> ValueRows;

    // 推荐：每个 ChildCollection 是独立的共享可观察集合。
    ParentCollection<std::shared_ptr<ChildCollection<int32_t>>> SharedRows;

    // 省略属性注册及其他代码。
};
```

绑定读取第 `0` 行、第 `2` 项时，两种结构对应的访问路径为：

```html
<p>{{ ValueRows[0][2] }}</p>
<p>{{ SharedRows[0][2] }}</p>
```

两处数据均为 `30` 时，输出：

```html
<p>30</p>
<p>30</p>
```

### 按值嵌套需要重读结构路径

`ValueRows[0]` 按结构值处理，没有独立的共享引用读取起点。绑定重新读取 `[2]` 时，需要从路径上最近的共享引用节点出发，重新取得 `ValueRows`、第 `0` 个 `ChildCollection`，再读取第 `2` 项。

嵌套层级越深，重新读取时需要经过的结构路径越长。多个绑定分别访问同一 `ChildCollection` 中的不同项，也需要经过这些结构层级。

### 共享集合可以直接读取当前实例

`SharedRows[0]` 是独立的共享可观察集合。完成上层路径解析后，绑定可以从这个 `ChildCollection` 直接读取第 `2` 项，不必为这次项读取重新取得 `SharedRows[0]`。

| 绑定路径 | 后续读取方式 |
| --- | --- |
| `ValueRows[0][2]` | 从最近的共享引用节点重新经过 `ValueRows[0][2]` 的结构路径 |
| `SharedRows[0][2]` | 从已解析的 `ChildCollection` 直接读取 `[2]` |

!!! note "读取起点会随引用关系更新"
    `ParentCollection` 替换某个 `ChildCollection` 时，仍需通知对应项变化，让绑定切换到新的 `ChildCollection`。

### 按值嵌套不支持回写

!!! danger "按值子集合元素无法回写"
    按值嵌套时，双向绑定不能直接写回 `ValueRows[0][2]`，只能整体覆盖 `ValueRows[0]`。相应通知也是整项变化，可能使更多绑定重新求值、重建更多界面元素，扩大布局刷新范围。

    ```html
    <!-- ValueRows 表示按值嵌套；此写法不支持将输入值回写到元素。 -->
    <input type="number" @value="{ValueRows[0][2], mode=twoWay, update=blur}">
    ```

    输入框中的修改不能回写到 `ValueRows[0][2]`。

    **命令可能使用未更新的数据**

    若输入框的修改未能回写，下面的命令仍会读取 `ValueRows[0][2]` 的原值。不要将该参数视为用户刚刚输入的值，否则可能保存或提交错误的数据。

    ```html
    <button @onclick="{Save, parameter={ValueRows[0][2]}}">Save</button>
    ```

共享的 `ChildCollection` 可以通知具体项的新增、删除或替换，减少不相关项的重新读取和更新。实际布局范围仍取决于模板结构和变化内容。

## 变更通知范围

- **按值嵌套**：`Rows = ValueRows`。
- **共享引用嵌套**：`Rows = SharedRows`。

表中的操作统一用 `Rows` 表示，省略共享指针的解引用写法。

| 操作 | 按值嵌套 | 共享引用嵌套 |
| --- | --- | --- |
| `Rows[0][2] = 40` | `Rows[0]` 变更 | 通知 `Rows[0][2]` 变更 |
| `Rows[0].Add(40)` | `Rows[0]` 变更 | 由 `Rows[0]` 通知新增项 |
| `Rows[0].RemoveAt(2)` | `Rows[0]` 变更 | 由 `Rows[0]` 通知第 `2` 项被删除 |
| `Rows[0] = newRow` | 由 `Rows` 通知第 `0` 项被替换 | 由 `Rows` 通知第 `0` 项被替换 |
| `Rows = newRows` | 由 `GridObject` 通知 `ValueRows` 属性变更 | 由 `GridObject` 通知 `SharedRows` 属性变更 |

### 同一路径中的不同通知来源

路径可以同时经过按值结构、可观察集合和引用对象。对于 `Root.ByKey['main'].Rows[0].Target.Health`，需要根据变化发生的位置选择通知。

- 替换 `Root` 或修改其中的借用成员后，由数据对象发布 `Root` 属性通知。
- 替换 `ByKey['main']` 时，由可观察字典发布键对应的元素变化。替换或移动 `Rows[0]` 时，由可观察数组或列表发布对应的集合变化。
- 修改 `Target.Health` 时，由 `Target` 发布 `Health` 属性通知。替换 `Target` 引用本身时，由拥有该引用的属性或集合项发布通知。

修改集合时应使用原始可观察实例。按值结构中的引用可以指向具有独立通知能力的对象或集合，通知仍由该实例发出。Unreal Engine 反射结构中的内嵌原生集合通过其拥有者通知刷新。具体操作见 [Unreal Engine 属性绑定](../ue/binding/property-binding.md#nested-struct-notifications)。

## 共享对象与生命周期

共享引用允许多个父对象或集合使用同一子对象。删除一个集合中的项，只会移除该集合持有的引用；其他拥有方仍然可以保留并使用该对象。

=== "C++"

    由 `std::shared_ptr<T>` 保持对象或子集合的生命周期。需要反向引用父对象时，使用 `std::weak_ptr<T>` 避免循环强引用；不要让父子对象仅依靠互相持有的强引用存活。

=== "C#"

    GC 可以回收不再可达的循环引用对象。`WeakReference<T>` 用于不希望延长目标生命周期的引用，不是避免循环引用的必需措施。

弱引用失效本身不等于属性或集合变化通知。业务上需要立即移除界面内容时，应通过相应属性或集合操作解除关系并发送通知。
