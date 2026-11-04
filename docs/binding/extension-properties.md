---
icon: bootstrap/puzzle
---

# 扩展属性

扩展属性是在可观察对象的类型定义之外注册的属性，通过 getter 读取值，也可以提供 setter 支持写入。无需向原有类添加同名属性，页面即可通过普通属性路径访问，适用于派生显示值或为已有模型补充绑定接口。

> 例如，模型提供 `Health`，可以在类外注册只读扩展属性 `HealthStatus`，返回健康状态枚举 `HealthState`。

## 定义与注册

确保在打开页面之前完成扩展属性的定义和注册。每个扩展属性只需注册一次。只提供 getter 时属性只读，同时提供 setter 时可以写入。

=== "C++"

    假设有以下可观察对象：

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

    为 `PlayerObject` 注册扩展属性：

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

        // 打开页面前调用，确保静态属性描述已初始化。
        static void Initialize()
        {
            (void)HealthStatusProperty;
        }
    };
    ```

    getter 接收 `const TObject&` 并返回 `TValue`；setter 接收 `TObject&` 和 `const TValue&`，返回 `void`。通过 `if (!PlayerExtensions::HealthStatusProperty)` 检查注册是否失败，例如名称非法或同一类型重复声明。

    创建实例后，将其作为页面数据上下文，应用负责保留对象生命周期：

    ```cpp
    PlayerExtensions::Initialize();
    std::shared_ptr<PlayerObject> player = std::make_shared<PlayerObject>();
    ```

=== "C#"

    假设有以下可观察对象：

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

    为 `PlayerObject` 注册扩展属性：

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

        // 在打开页面前调用，确保完成静态初始化。
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

    初始化后创建实例，将其作为页面数据上下文：

    ```csharp
    PlayerExtensions.Initialize();
    var player = new PlayerObject();
    ```

    非法名称、空访问器或不支持的类型会抛出参数异常；同一声明类型的同名重复注册抛出 `MarkupInvalidOperationException`。访问器使用静态方法或不捕获业务实例的委托。

## 页面使用

扩展属性不需要特殊的 HTML 语法，与普通属性使用相同的绑定路径：

```html
<!-- 确保当前数据上下文是上述示例中的 PlayerObject 实例。 -->
<p @if="{HealthStatus == 0}">健康</p>
<p @if="{HealthStatus == 1}">受伤</p>
<p @if="{HealthStatus == 2}">危急</p>
```

`Health` 大于或等于 `60` 时为 `Healthy`，大于 `20` 且小于 `60` 时为 `Injured`，小于或等于 `20` 时为 `Critical`。页面使用枚举对应的整数值判断并显示文字；初始 `Health` 为 `80`，因此显示“健康”。`HealthStatus` 只提供 getter，不能用于写回。

扩展属性同样可以通过子对象路径、命名上下文或已声明的别名访问，参见[数据上下文](../concepts/data-context.md)。

## 变更通知

getter 在读取时计算结果，不缓存，也不自动推断依赖。修改来源数据后，必须显式通知受影响的扩展属性；调用 setter 本身不会自动发送扩展属性通知。

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

C++ 的普通属性和扩展属性统一使用 `MarkupUI::Binding::NotifyPropertyChanged`，传入对象及属性名称。C# 也可以通过对象的 `PropertyChanged` 事件发送扩展属性名称，与 `NotifyChanged` 选择一种，避免重复通知。数据读写与通知遵循应用配置的数据线程访问约定。

## 继承

为 `PlayerObject` 注册的扩展属性同样适用于它的派生类，无需重复注册。例如，定义以下派生类型：

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

    // 在打开页面前初始化扩展属性。
    PlayerExtensions.Initialize();
    var player = new WarriorObject();
    ```

将 `WarriorObject` 实例作为数据上下文后，页面仍可读取 `HealthStatus`。getter 接收该实例对应的 `PlayerObject`，根据继承的 `Health` 计算状态。派生实例同样使用上面的通知方式：C++ 调用 `MarkupUI::Binding::NotifyPropertyChanged`，C# 调用扩展属性描述的 `NotifyChanged`。

读取或写入属性时，按下列顺序查找：

1. 查找对象自身及继承的普通属性。找到后使用普通属性，不再查找同名扩展属性。
2. 没有同名普通属性时，查找对象实际类型注册的扩展属性。本例首先查找 `WarriorObject`。
3. 当前类型没有声明时，沿继承链从最近的基类逐级查找。本例接着查找 `PlayerObject`，因此能找到已注册的 `HealthStatus`。
4. 整条继承链都没有匹配项时，按属性不存在处理。

因此，派生类注册的扩展属性优先于基类的同名扩展属性，但不能覆盖普通属性。

## 类型与名称规则

- 属性名称不能包含 `.`、`/`、`\`、`[`、`]` 等符号。
- getter 应只读取数据，不产生业务副作用。
- 属性写入遵循普通属性的类型检查规则，不采用命令参数的数字转换规则。

C++ 支持标量、字符串及已注册标量映射的读写；显式共享对象、弱对象返回值当前只读。按值返回集合不支持，共享集合返回值也不在当前支持范围内。

C# 支持标量、字符串、可空标量、对象、弱对象及已支持的集合类型。对象、弱对象、Map、Set 当前只读；支持按普通属性规则整体替换标量数组。集合内部的变更通知仍由集合本身发送。

!!! note "注册生命周期"
    扩展属性注册不持有业务对象实例。注册不能单独撤销，应在应用初始化阶段完成，并保证访问器代码在使用期间有效。
