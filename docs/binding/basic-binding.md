---
icon: bootstrap/link-45deg
---

# 基础绑定

基础绑定从数据上下文读取单个值，将其用于文本、HTML 属性或 CSS 样式。读取的值可以是字符串、数值或布尔值，也可以是对象中的某个属性。对象本身则可以用作一组元素的数据上下文。

## 标量值与对象

以下代码定义玩家、武器和武器所有者；将创建的 `player` 作为文档默认数据上下文。标量值、对象及其支持范围见[数据类型](data-types.md)。

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
         * 参数 1：WeaponObject，声明该属性的类。
         * 参数 2：std::weak_ptr<OwnerObject>，不延长所有者生命周期的弱引用。
         * 参数 3：WeaponOwner，C++ 属性标识符，用于生成
         *         GetWeaponOwner() 和 SetWeaponOwner() 访问器。
         * 参数 4："WeaponOwner"，HTML 绑定使用的属性名称，
         *         例如 Weapon.WeaponOwner.Name 中的 WeaponOwner。
         * 参数 5（可选）：属性默认值；本例省略，对象引用初始为空。
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

    创建对象并连接嵌套属性：

    ```cpp
    auto owner = std::make_shared<OwnerObject>();

    auto weapon = std::make_shared<WeaponObject>();
    weapon->SetWeaponOwner(std::weak_ptr<OwnerObject>{owner});

    auto player = std::make_shared<PlayerObject>();
    player->SetWeapon(weapon);
    ```

    `WeaponOwner` 的绑定名称为 `WeaponOwner`，因此 HTML 中使用 `Weapon.WeaponOwner.Name`，C++ 中通过 `SetWeaponOwner()` 设置该业务属性。

    武器对所有者使用弱引用，不延长所有者的生命周期。示例中的 `owner` 强引用应由应用保留；所有者销毁后，弱引用失效。C++ 业务代码访问弱引用时，应通过 `lock()` 取得临时强引用并检查结果。

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
        // C# GC 可以回收不再可达的循环引用对象。
        // 本例使用 WeakReference<T> 仅用于说明 SDK 也支持弱引用属性。
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

    创建对象：

    ```csharp
    var owner = new OwnerObject();
    var player = new PlayerObject();
    var weapon = player.Weapon;
    weapon.WeaponOwner = new WeakReference<OwnerObject>(owner);
    ```

    `WeaponOwner` 是直接声明为 `WeakReference<OwnerObject>` 的弱引用属性，绑定可以继续访问其目标对象，例如 `Weapon.WeaponOwner.Name`，无需在可观察对象中额外定义返回强引用的包装属性。应用应保留 `owner` 的强引用；目标被回收后，绑定路径无法取得目标对象。弱引用失效本身不会发出属性通知，业务上解除所有者关系时应显式设置 `WeaponOwner = null` 并通知绑定。

- `Name`、`Health`、`AvatarPath` 和 `IsReady` 是标量属性。
- `Weapon` 是对象属性，包含 `Name` 和 `Damage`。
- `Weapon.Name` 是属性路径，最终读取的是字符串 `"Sword"`。

!!! note "对象属性与 HTML 属性"
    数据上下文中的属性属于业务对象，例如 `PlayerObject.Name`；HTML 属性属于元素，例如 `img` 的 `src`。绑定将前者的值用于后者，两者不要求同名。

## 绑定标量值

### 显示文本

文本插值将标量值插入元素的文本内容，可与固定文字组合：

```html
<h1>{{ Name }}</h1>
<p>Health: {{ Health }}</p>
```

最终输出的 HTML 代码：

```html
<h1>Alice</h1>
<p>Health: 100</p>
```

也可以使用 `@text` 绑定整个文本内容：

```html
<h1 @text="{Name}">Player name</h1>
```

`Player name` 是设计时占位文本，运行时由绑定结果替换。文本绑定用于显示文字，不将字符串中的 HTML 标签作为页面结构解析。

### 设置 HTML 属性

使用 `@属性名` 将值绑定到 HTML 属性。下面将 `AvatarPath` 用于图片的 `src`，将 `Name` 用于输入框的 `value`：

```html
<img @src="{AvatarPath}" alt="Player avatar">
<input @value="{Name}">
```

绑定目标决定值的用途：图片路径按[资源路径](../authoring/resource-paths.md)规则解析；输入框显示字符串，并可按绑定模式将输入写回 `Name`。

### 设置样式

使用 `@style.属性名` 设置单个 CSS 样式属性。例如，数据上下文提供数值属性 `Opacity` 时：

```html
<div @style.opacity="{Opacity}">Player information</div>
```

绑定结果必须符合目标的类型和取值范围。`opacity` 需要有效的透明度值；长度、颜色等其他样式也需要相应的值。绑定不会自动为任意数值选择 CSS 单位。

## 访问对象中的属性

使用点号连接属性名称，可以逐级读取对象中的值：

```html
<p>Weapon: {{ Weapon.Name }}</p>
<p>Damage: {{ Weapon.Damage }}</p>
```

路径从当前数据上下文开始：先读取 `PlayerObject` 的 `Weapon`，再读取武器对象的 `Name` 或 `Damage`。

最终输出的 HTML 代码：

```html
<p>Weapon: Sword</p>
<p>Damage: 25</p>
```

`Name` 与 `Weapon.Name` 指向不同属性：前者是玩家名称，后者是武器名称。属性名称**区分**大小写，应与应用提供的名称保持一致。

### 多级属性路径

属性路径可以通过多个点号访问更深层的对象。例如，`Weapon.WeaponOwner.Name` 从当前数据上下文依次读取 `Weapon`、武器的 `Owner`，最后读取所有者的 `Name`：

```html
<p>Owner: {{ Weapon.WeaponOwner.Name }}</p>
```

最终输出的 HTML 代码：

```html
<p>Owner: Alice</p>
```

路径中的每一级名称都属于前一级读取到的对象，不是包含点号的单个属性名称。中间对象必须存在，才能继续读取后续属性。

多级路径也可以用于 HTML 属性绑定。例如，武器的 `Owner` 对象提供 `AvatarPath` 时：

```html
<img @src="{Weapon.WeaponOwner.AvatarPath}" alt="Weapon owner avatar">
```

路径从当前数据上下文开始解析。使用 `@context="{Weapon}"` 后，同一个所有者名称应写为 `WeaponOwner.Name`：

```html
<section @context="{Weapon}">
  <p>Owner: {{ WeaponOwner.Name }}</p>
</section>
```

对于 `Weapon.WeaponOwner.Name`，修改所有者名称时，由所有者对象通知 `Name` 变化；替换所有者时，由武器对象通知 `Owner` 变化；替换武器时，由玩家对象通知 `Weapon` 变化。绑定据此重新读取受影响的路径，后续更新使用替换后的对象。

## 将对象作为数据上下文

当一组元素都显示同一个对象的属性时，可以通过 `@context` 使用该对象作为数据上下文：

```html
<section @context="{Weapon}">
  <h2>{{ Name }}</h2>
  <p>Damage: {{ Damage }}</p>
</section>
```

`Weapon` 从外层数据上下文读取。指定上下文后，元素自身和其子元素将使用指定的数据上下文，因此这里的 `Name` 和 `Damage` 都属于武器对象。

两种写法的用途不同：

| 写法 | 含义 | 适用场景 |
| --- | --- | --- |
| `{{ Weapon.Name }}` | 从当前上下文读取嵌套属性 | 只显示对象中的少量属性 |
| `@context="{Weapon}"`，内部使用 `{{ Name }}` | 使用对象作为数据上下文，再读取属性 | 一组元素共同显示该对象 |

!!! note "对象不是自动生成的界面"
    `Weapon` 表示对象，`Weapon.Name` 才表示武器名称。不要用 `{{ Weapon }}` 代替 `{{ Weapon.Name }}` 来显示名称，也不要依赖它自动展开对象字段。需要展示哪些属性，应在 HTML 中明确声明。

直接将对象用于文本插值时，绑定使用对象提供的字符串表示；未提供时使用 `[Object]`。该字符串不等于对象的 `Name` 属性，也不是所有字段的序列化结果。

错误用例：希望显示武器名称，却直接绑定了武器对象。假设该对象未提供字符串表示：

```html
<!-- 错误：Weapon 是对象，不能用它代替 Weapon.Name 显示武器名称 -->
<p>Weapon: {{ Weapon }}</p>
```

最终输出的 HTML 代码：

```html
<p>Weapon: [Object]</p>
```

命名上下文、嵌套作用域和外层别名见[数据上下文](../concepts/data-context.md)。

## 属性变化与对象替换

绑定持续更新需要相应的变更通知。对于 `Weapon.Name`，应区分以下两种操作：

| 操作 | 示例 | 所需通知与结果 |
| --- | --- | --- |
| 修改对象内部的属性 | 将当前武器的 `Name` 从 `Sword` 改为 `Bow` | 武器对象通知 `Name` 变化，相关文本重新读取名称 |
| 替换对象属性 | 将玩家的 `Weapon` 替换为另一把武器 | 玩家对象通知 `Weapon` 变化，绑定重新解析后续路径，读取新武器的属性 |

替换 `Weapon` 后，`Weapon.Name` 以及使用 `@context="{Weapon}"` 的区域都会转向新对象。后续应由新武器的属性通知驱动更新，旧武器的变化不再决定该区域的内容。

对于直接绑定的 `Health` 等标量属性，同样需要通知对应属性发生变化。单纯修改业务对象中的值，不等于已经通知界面更新。

以上持续更新行为适用于需要监听数据变化的绑定；`oneTime` 不持续监听后续变化。模式与输入写回规则见[数据绑定概述](getting-started.md)，各平台的通知方式请阅读对应平台文档。

## 空对象与缺失属性

当 `Weapon` 为空时，`Weapon.Name` 无法读取武器名称；当属性不存在时，也无法得到有效值。文本插值在这些情况下显示为空，不会自动使用外层同名属性。

```html
<!-- Weapon 为空时，此处不显示武器名称 -->
<p>Weapon: {{ Weapon.Name }}</p>
```

之后为 `Weapon` 设置有效对象并发送对应通知，绑定可以重新取得名称。

不要将空结果视为数值 `0` 或布尔值 `false`；也不要假定文本、图片、样式和输入目标对空值的处理完全相同。业务上需要缺省文字或隐藏区域时，应明确设置相应的表达式或显示条件。

