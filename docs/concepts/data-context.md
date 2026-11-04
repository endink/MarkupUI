---
icon: bootstrap/database
---

# 数据上下文

**数据上下文（Data Context）**是页面绑定表达式读取数据时使用的对象。例如，玩家信息面板可以将玩家对象作为数据上下文，通过对象的 `Name`、`Health` 等属性显示角色信息。

数据上下文由应用通过平台插件提供。HTML 负责声明使用哪些数据，不需要将当前角色名称、生命值等业务数据固定写入页面。

## 可观察对象

Markup UI 的数据上下文统一以**可观察对象**的形式提供。可观察对象包含供 HTML 绑定读取的业务属性，并在属性变化时发出通知，使界面能够更新。将可观察对象提供给文档或某个元素后，该对象就是对应的数据上下文。

以下示例定义玩家对象 `PlayerObject` 和武器对象 `WeaponObject`。两者均提供属性变更通知，既可以更新玩家的 `Health`，也可以更新 `Weapon.Name`，或替换整个 `Weapon` 对象。

=== "C++"

    1. 继承 SDK 提供的 `ObservableObject` 基类。
    2. 使用 `MARKUPUI_PROPERTY` 声明可绑定属性。
    3. 在构造函数中调用 `InitializeType<T>()`，其中 `T` 为当前类的类型。
    4. 使用 `std::make_shared<T>()` 创建对象。

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
         * 参数 1：WeaponObject，声明该属性的类。
         * 参数 2：std::string，属性的数据类型。
         * 参数 3：Name，属性名称，也是 HTML 绑定使用的名称；
         *         同时生成 GetName() 和 SetName() 访问器。
         * 参数 4："Sword"，属性的默认值。
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

    创建玩家及其武器：

    ```cpp
    auto weapon = std::make_shared<WeaponObject>();

    auto player = std::make_shared<PlayerObject>();
    player->SetWeapon(weapon);
    ```

    宏生成 `GetName()`、`SetName()` 等访问器。通过 `SetHealth()`、`SetWeapon()` 等生成的设置方法修改属性时，由可观察对象处理变更通知。HTML 中使用的是声明的属性名 `Health`、`Weapon`，不是访问器名称。

=== "C#"

    SDK 支持标准的 `INotifyPropertyChanged` 接口，通过公开属性读取数据，通过 `PropertyChanged` 接收变更通知。下面两个类直接实现该接口，在属性设置器中发送通知。

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

    创建玩家及其武器：

    ```csharp
    var player = new PlayerObject();
    var weapon = player.Weapon;
    ```

    属性设置器在值变化时发送与属性同名的通知。例如，设置 `Health` 会通知 `Health` 变化，设置 `Weapon` 会通知武器对象被替换。

    !!! tip "使用现成的 ObservableObject 基类"
        项目已引用相应工具包时，可以让业务类继承 [ObservableObject](https://learn.microsoft.com/dotnet/api/microsoft.toolkit.mvvm.componentmodel.observableobject){ target="_blank" rel="noopener noreferrer" }。它实现了 `INotifyPropertyChanged`，并提供 `SetProperty` 等辅助方法，可减少属性变更通知的重复代码。

        链接中的类型属于 `Microsoft.Toolkit.Mvvm` 包，不是 .NET Standard 内置类型。仅使用其属性通知能力，无需采用特定的应用架构。

!!! note "每个对象通知自身的属性变化"
    修改 `Weapon.Name` 时，由武器对象通知 `Name` 变化；替换 `PlayerObject.Weapon` 时，由玩家对象通知 `Weapon` 变化。只让玩家对象可观察，不能替代武器内部属性的通知。

## 从数据上下文读取属性

将上例中的 `player` 对象提供为文档默认数据上下文。具体设置入口请阅读各平台文档。

以该对象作为数据上下文时，可以在 HTML 中引用属性：

```html
<h1>{{ Name }}</h1>
<p>Health: {{ Health }}</p>
<p>Weapon: {{ Weapon.Name }}</p>
```

最终输出的 HTML 代码：

```html
<h1>Alice</h1>
<p>Health: 100</p>
<p>Weapon: Sword</p>
```

`{{ ... }}` 表示文本插值。`Name` 从当前数据上下文读取角色名称，`Weapon.Name` 则沿属性路径读取武器名称。C++ 和 C# 示例提供相同的属性名称，因此使用同一份 HTML。

数据上下文提供查找属性的起点；具体属性路径决定绑定读取的值。显示在哪个元素、写入文本还是元素属性，由绑定声明决定。

## 默认与命名数据上下文

一个文档允许配置多个数据上下文（DataContext），其中最多只有一个**默认数据上下文**，它没有名称。其他数据上下文通过名称区分，各名称在同一文档内必须唯一。

### 默认数据上下文

默认情况下，所有 HTML 元素都以文档的默认数据上下文作为自己的数据上下文。通过 `@context` 指定上下文后，元素自身和其子元素将使用指定的数据上下文。

```html
<!-- 使用文档的默认数据上下文 -->
<p>{{ Name }}</p>

<!-- 改变数据上下文：使用默认数据上下文的 Weapon 属性作为上下文 -->
<section @context="{Weapon}">
  <h1>{{ Name }}</h1>
  <p>Damage: {{ Damage }}</p>
</section>

<!-- 改变数据上下文：使用名为 "player" 的上下文 -->
<section @context="player">
  <h1>{{ Name }}</h1>
  <p>Health: {{ Health }}</p>
</section>
```

### 命名数据上下文

当一个页面需要多个独立业务对象时，应用可以按名称登记数据上下文。例如，将玩家对象登记为 `player`，将设置对象登记为 `settings`。

```html
<section @context="player">
  <h1>{{ Name }}</h1>
  <p>Health: {{ Health }}</p>
</section>

<section @context="settings">
  <p>Volume: {{ Volume }}</p>
</section>
```

`@context="player"` 选择应用已登记的 `player` 对象，`@context="settings"` 选择 `settings` 对象。页面可以只使用命名数据上下文，不设置默认对象。

!!! note "名称需要由应用登记"
    在 HTML 中填写 `player` 不会创建玩家对象，也不会自动寻找同名游戏对象。名称**区分**大小写；应用未登记对应名称时，该区域使用空上下文，不回退到父级或默认对象。

静态名称使用非空的 ASCII 字母、数字、下划线或连字符组合。`mk:context` 与 `@context` 等价，可按页面书写习惯选择一种形式。

## 嵌套上下文与当前对象

### 通过属性切换上下文

在当前上下文中取得一个子对象，可将其作为某个区域的新上下文：

```html
<section @context="player">
  <h1>{{ Name }}</h1>
  <div @context="{Weapon}">
    <p>{{ Name }}</p>
    <p>Damage: {{ Damage }}</p>
  </div>
</section>
```

外层的 `Name` 表示玩家名称；进入 `Weapon` 后，内部的 `Name` 与 `Damage` 分别表示武器名称和伤害。该切换作用于声明元素及其后代，不改变外部兄弟区域的上下文。

| 写法 | 含义 |
| --- | --- |
| 不写 `@context` | 继承父级上下文，最外层使用默认上下文 |
| `@context="player"` | 选择应用登记的命名上下文 |
| `@context="{Weapon}"` | 从当前上下文求值 `Weapon` 属性，使用其结果 |

!!! note "名称与属性表达式不同"
    `@context="Weapon"` 选择名称为 `Weapon` 的上下文；`@context="{Weapon}"` 读取当前对象的 `Weapon` 属性。两者不能互换。

### 当前对象

`@this` 表示当前数据上下文。普通属性路径 `Name` 相当于 `@this.Name`；切换上下文后，`@this` 的指向也随之改变。

## 数据上下文别名

`@as` 可以在任意 HTML 元素上使用，为该元素的数据上下文创建别名。通过 `@别名` 访问对应对象，不需要同时声明 `@context`。

### 为继承的上下文创建别名

`@as="page"` 为继承的当前上下文创建别名：

```html
<section @as="page">
  <p>{{ @page.Name }}</p>
</section>
```

`@page` 指向该 `section` 继承的数据上下文，`@as` 本身不切换上下文。

### 为切换后的上下文创建别名

同时声明 `@context` 和 `@as` 时，别名指向切换后的上下文：

```html
<section @as="page">
  <div @context="{Child}" @as="child">
    <p>Child: {{ @child.Name }}</p>
    <p>Page: {{ @page.Name }}</p>
  </div>
</section>
```

`@child` 指向 `Child` 属性提供的对象，`@page` 仍指向外层上下文。

### 循环容器的上下文别名

`@for="{Items}" @as="page"` 为循环容器的数据上下文创建别名；集合元素使用 `@item-as` 创建别名：

```html
<ul @for="{Items}" @as="page" @item-as="item">
  <li>{{ @page.Name }}: {{ @item.Name }}</li>
</ul>
```

`@page` 指向提供 `Items` 的上下文，`@item` 指向当前集合元素。`@as` 不会为集合元素创建别名。循环规则见[集合绑定](../binding/collection-binding.md)。

别名在声明区域及其子区域中使用，不影响外部兄弟区域。它是模板内的名称，不是由应用登记的命名数据上下文。

## 数据变化与上下文替换

修改上例中已有对象的属性：

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

两种写法均通过对象的通知机制更新绑定。原来的 HTML 随后显示 `Health: 80` 和 `Weapon: Bow`。

修改业务对象的属性与替换整个数据上下文是不同操作：

- **属性变化**：例如将当前玩家的 `Health` 从 `100` 改为 `80`，对象本身未替换。应用应通过相应的变更通知更新绑定。
- **上下文替换**：例如选择另一名玩家，将页面使用的玩家对象替换为新对象，相关绑定随后从新对象读取数据。

默认上下文与各命名上下文分别管理。替换默认对象不会自动改写已登记的 `player`、`settings` 等命名对象。

!!! tip "界面没有更新时"
    先检查上下文是否已提供、名称是否一致、属性路径是否正确，以及数据变化是否发送了对应通知。单纯修改 HTML 中的上下文名称不能代替应用侧的数据配置。

## 平台提供数据的方式

默认上下文、命名上下文和页面内作用域属于公共概念；业务对象的类型、设置入口、引用管理和变更通知由平台接入方式决定。详细信息请阅读各平台文档。

相关章节：[数据绑定概述](../binding/getting-started.md)、[基础绑定](../binding/basic-binding.md)、[绑定语法](../binding/binding-syntax.md)、[事件与命令](../binding/events-and-commands.md)。
