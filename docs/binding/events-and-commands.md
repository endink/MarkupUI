---
icon: bootstrap/lightning
---

# 事件与命令

- **事件**：点击、输入或焦点变化等界面操作。
- **命令**：应用提供的业务操作。

事件绑定将 HTML 元素的事件关联到数据上下文中的命令；事件发生且过滤条件匹配时，读取参数并执行命令。

## 命令

命令是应用向数据绑定提供的业务操作，由名称、参数声明和执行逻辑组成。C++ 可以注册成员函数或提供 `ICommand` 对象；C# 通过 `BindingInfo.Commands<TModel>` 配置命令注册。

!!! note "C++ ICommand 规范"
    通过 `ICommand` 注册 C++ 命令时，命令字段必须使用 `std::shared_ptr<ICommand<TArgs...>>` 。   
    例如:    
    `std::shared_ptr<MarkupUI::Binding::ICommand<int32_t, bool>>`。   
    无参数命令:   
    `std::shared_ptr<MarkupUI::Binding::ICommand<>>`。


### 定义命令


以下代码定义了一个 `Save` 命令，依次接收目标生命值和确认状态两个参数。确认状态为真时，将 `Health` 更新为目标生命值。

=== "C++ (函数命令)"

    继承 `ObservableObject`，通过 `RegisterCommand` 注册业务方法为命令：

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <markupui/binding/modeling/object_model.h>

    class PlayerObject final
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        PlayerObject()
        {
            InitializeType<PlayerObject>();
        }

        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 80)
        MARKUPUI_PROPERTY(PlayerObject, int32_t, TargetHealth, 100)
        MARKUPUI_PROPERTY(PlayerObject, bool, Confirmed, true)

        void Save(int32_t targetHealth, bool confirmed)
        {
            if (confirmed)
            {
                SetHealth(targetHealth);
            }
        }

        inline static const auto SaveCommand =
            MarkupUI::Binding::Metadata::RegisterCommand<
                PlayerObject, &PlayerObject::Save>(MARKUPUI_STR_VIEW("Save"));
    };
    ```

    创建对象：

    ```cpp
    auto player = std::make_shared<PlayerObject>();
    ```

    `Save` 按声明顺序接收 `int32_t` 和 `bool` 参数。

    注册名称为 `Save`，`SaveCommand` 保存注册定义。

=== "C++ (ICommand)"

    继承 `ObservableObject`，通过 `RegisterCommand` 注册 `ICommand<int32_t, bool>` 成员，使用 `DelegateCommand<int32_t, bool>` 提供执行逻辑：

    ```cpp
    #include <cstdint>
    #include <memory>
    #include <markupui/binding/delegate_command.h>
    #include <markupui/binding/modeling/object_model.h>

    class PlayerObject final
        : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        std::shared_ptr<MarkupUI::Binding::ICommand<int32_t, bool>> SaveCommand;

        PlayerObject()
        {
            InitializeType<PlayerObject>();

            SaveCommand = std::make_shared<
                MarkupUI::Binding::DelegateCommand<int32_t, bool>>(
                [this](int32_t targetHealth, bool confirmed)
                {
                    if (confirmed)
                    {
                        SetHealth(targetHealth);
                    }
                });
        }

        MARKUPUI_PROPERTY(PlayerObject, int32_t, Health, 80)
        MARKUPUI_PROPERTY(PlayerObject, int32_t, TargetHealth, 100)
        MARKUPUI_PROPERTY(PlayerObject, bool, Confirmed, true)

        inline static const auto SaveInfo =
            MarkupUI::Binding::Metadata::RegisterCommand<
                PlayerObject, &PlayerObject::SaveCommand>(MARKUPUI_STR_VIEW("Save"));
    };
    ```
    
    > 无参命令接口
    > ```cpp
        MarkupUI::Binding::ICommand<>
    > ```

    创建对象：

    ```cpp
    auto player = std::make_shared<PlayerObject>();
    ```

    注册名称为 `Save`，`SaveCommand` 保存命令对象，`SaveInfo` 保存注册定义。

    `player` 由应用持有，`PlayerObject` 通过 `SaveCommand` 持有命令对象。回调捕获的 `this` 不延长 `PlayerObject` 的生命周期；如果另行保存命令对象，必须保证执行回调时 `PlayerObject` 仍然有效。

=== "C#"

    使用 `DelegateCommand` 包装业务操作，通过 `BindingInfo.Commands<TModel>` 集中注册命令：

    ```csharp
    using System.ComponentModel;
    using MarkupUI.Sdk.Binding;

    public class PlayerObject : INotifyPropertyChanged
    {
        private int _health = 80;
        private readonly int _targetHealth = 100;
        private readonly bool _confirmed = true;

        public event PropertyChangedEventHandler PropertyChanged;

        // Markup UI SDK 不依赖反射，必须在静态构造函数中注册命令。
        static PlayerObject()
        {
            BindingInfo.Commands<PlayerObject>(commands =>
            {
                commands.Register("Save", model => model.Save);
            });
        }

        public PlayerObject()
        {
            Save = new DelegateCommand<int, bool>(ExecuteSave);
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

        public int TargetHealth
        {
            get { return _targetHealth; }
        }

        public bool Confirmed
        {
            get { return _confirmed; }
        }

        public ICommand<int, bool> Save { get; }

        private void ExecuteSave(int targetHealth, bool confirmed)
        {
            if (confirmed)
            {
                Health = targetHealth;
            }
        }
    }
    ```

    创建对象：

    ```csharp
    var player = new PlayerObject();
    ```

    `BindingInfo.Commands<PlayerObject>` 指定模型类型，可在配置委托中多次调用 `commands.Register` 注册不同命令。`"Save"` 是注册名称，`model => model.Save` 从当前模型读取命令对象，命令参数类型由该对象的接口推导。必须在静态构造函数中注册命令，读取委托不应捕获具体模型实例。

    `DelegateCommand` 绑定成员方法 `ExecuteSave`，按相同顺序接收两个参数。这里的 `ICommand` 属于 `MarkupUI.Sdk.Binding`，不是 `System.Windows.Input.ICommand`。
    
    
    ??? info "C# 完成 ICommand 接口"

        C# 命令接口均位于 `MarkupUI.Sdk.Binding` 命名空间：
        
        | 参数数量 | 接口 |
        | --- | --- |
        | 0 | `#!csharp ICommand` |
        | 1 | `#!csharp ICommand<T1>` |
        | 2 | `#!csharp ICommand<T1, T2>` |
        | 3 | `#!csharp ICommand<T1, T2, T3>` |
        | 4 | `#!csharp ICommand<T1, T2, T3, T4>` |
        | 5 | `#!csharp ICommand<T1, T2, T3, T4, T5>` |
        | 6 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6>` |
        | 7 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7>` |
        | 8 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7, T8>` |
        | 9 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7, T8, T9>` |
        | 10 | `#!csharp ICommand<T1, T2, T3, T4, T5, T6, T7, T8, T9, T10>` |

### 命令参数

#### C++ 参数类型与接收形式

当前 C++ 强类型命令支持 **0～10 个参数**，可通过成员函数签名或 `ICommand<TArgs...>` 声明。无参数命令使用 `ICommand<>`。表中的 `T` 表示对应的具体类型。

| 参数类型 | 支持的接收形式 | 说明 |
| --- | --- | --- |
| `bool` | `bool`、`const bool&` | 布尔值 |
| `int8_t`、`uint8_t`、`int16_t`、`uint16_t`、`int32_t`、`uint32_t`、`int64_t`、`uint64_t` | `T`、`const T&` | 整数；按命令声明的目标类型检查范围并转换 |
| `float`、`double` | `T`、`const T&` | 浮点数 |
| 枚举 | `T`、`const T&` | 仅限支持的枚举类型 |
| `String`、`StringView` | `String`、`const String&`、`StringView`、`const StringView&` | 字符串 |
| `Color`、`ColorF`、`Vector2`、`Vector3`、`Matrix4x4` | `T`、`const T&` | SDK 结构 |
| Platform Scalar[^command-platform-scalar] | `T`、`const T&` | 平台支持的原生标量类型 |
| Object[^command-object] | `T*`、`const T*`、`T&`、`const T&` | 借用原实例 |
| Array、Map、Set | `T*`、`const T*`、`T&`、`const T&` | 集合；借用原实例 |
| 共享对象、共享集合[^command-shared] | `T*`、`const T*`、`T&`、`const T&` | `T` 为所指对象或集合的类型，不是共享指针类型 |
| 弱对象、弱集合[^command-weak] | `T*`、`const T*`、`T&`、`const T&` | `T` 为所指对象或集合的类型；仅在目标有效时接收 |
| `Null` | 原始指针 | 接收为 `nullptr`；引用参数不接受 |

例如，共享子集合可以通过以下任一种签名接收：

```cpp
void Save(MarkupUI::Binding::IArray<int32_t>* items);
void Save(const MarkupUI::Binding::IArray<int32_t>& items);
```

以下接收形式当前不支持：

```cpp
void Save(FMyObject object);                   // 未映射业务对象按值
void Save(ObservableArray<int32_t> items);     // 原生集合按值
void Save(std::shared_ptr<FMyObject> object);  // 共享指针本身
void Save(const std::shared_ptr<FMyObject>& object);
```

标量和 Mapper 的 `const T&` 引用本次解码的临时值；对象、集合的引用借用原实例。独立共享实例在调用期间可临时保活，内嵌集合仍受所属存储有效期约束。不要跨调用保存借用的指针或引用。弱引用目标失效时，不调用业务方法。

C# 提供无参数 `ICommand` 和接收 1～10 个参数的泛型 `ICommand<T1, ...>`，`DelegateCommand` 提供对应形式。参数支持已注册的 Mapper 和可空类型。

### 数据类型兼容

命令参数以接收方声明的类型为准。C++ 和 C# 使用相同的数字转换规则，适用于数据上下文中的命令、全局命令和触发器的 `do:command` 行为。

SDK 支持的十种数字类型（`Int8`、`UInt8`、`Int16`、`UInt16`、`Int32`、`UInt32`、`Int64`、`UInt64`、`Float`、`Double`）可以相互转换，转换前检查目标类型的范围：

| 来源与目标 | 转换规则 |
| --- | --- |
| 整数 → 整数 | 检查目标上下界；负数不能传给无符号整数参数 |
| 浮点数 → 整数 | 向零取整后检查范围，例如 `17.875` 转为 `17`，`-17.875` 转为 `-17` |
| 整数 → 浮点数 | 允许目标精度产生的正常舍入 |
| 浮点数 → 浮点数 | 检查目标范围，允许正常精度舍入；下溢时可能舍入为零 |

表达式先独立求值，再转换为命令参数类型。例如，整数字面量 `17` 的求值类型是 `Int64`，仍可传给 C++ 的 `int32_t` 或 C# 的 `int` 参数。此规则仅适用于命令参数，不改变属性写入、集合键或表达式内部的类型规则。

例如，来源值为浮点数 `17.875`，命令声明接收整数参数时，SDK 向零取整后传入 `17`：

=== "C++"

    ```cpp
    // 假设来源参数求值为 double 类型的 17.875。
    void SetAge(int32_t age)
    {
        // SDK 转换后调用此函数，age 为 17。
    }
    ```

=== "C#"

    ```csharp
    // 假设来源参数求值为 double 类型的 17.875。
    void SetAge(int age)
    {
        // SDK 转换后调用此函数，age 为 17。
    }
    ```

这里的转换发生在 SDK 调用命令之前；直接在业务代码中调用函数时，不经过命令参数转换。

!!! warning "无效数字会阻止整条命令执行"
    数值越界、NaN 或正负无穷均转换失败，SDK 记录错误，不会钳制到边界或回绕。所有参数检查和转换成功后才调用业务函数；即使只有后面的参数失败，也不会执行部分业务逻辑。

其他类型仍按声明类型检查，不参与数字转换：

- 布尔值和字符串不会自动转为数字，例如 `true`、`'17'` 不能作为数字参数。
- 颜色、向量、矩阵和对象不参与数字转换；对象和集合还需要满足接收类型及存活条件。
- 已注册数字 Mapper 的类型先按其映射的标量类型转换，再还原为声明类型。
- 空值仍遵循接收类型的可空规则；C++ 原始指针可接收 `nullptr`，引用不能接收空值，C# 可空类型保留其空值语义。

参数数量、类型、数值范围或对象存活检查失败时，业务函数不会执行。错误日志会指出参数序号、期望类型及实际值类型，便于定位不兼容的参数。

### 执行条件

`ICommand` 提供无参数的 `CanExecute()` 查询。直接调用 `Execute` 不会自动查询执行条件，调用方应根据查询结果决定是否执行。`CanExecuteChanged` 提供本地可用状态通知。

## 事件 {#command-events}

事件是 HTML UI 元素在用户交互过程中发出的通知。例如，用户修改文本输入框 `<input>` 的值后，提交更改时会触发 `change` 事件，通常发生在输入框失去焦点时。

Markup UI 支持在 HTML 中使用命令绑定语法，将元素事件关联到命令。UI 事件触发且过滤条件匹配、命令允许执行时，调用绑定的命令，执行其定义的回调函数。

使用 `@事件名="{命令绑定描述}"` 将元素事件绑定到命令，通过 `parameter` 按顺序传入参数。`mk:` 前缀与 `@` 等价，例如 `@onclick` 和 `mk:onclick` 等价。

假设 `Save` 命令函数如下，三个参数依次接收姓名、年龄和选中状态：

=== "C++"

    ```cpp
    void Save(std::string name, int32_t age, bool selected);
    ```

=== "C#"

    ```csharp
    void Save(string name, int age, bool selected);
    ```

### 语法

将命令名称和参数列表放在同一个绑定表达式中：

> `@事件名` 这里的事件名通常和标准 HTML 语法中的事件名相同。   
> 例如:   
> `#!html <input onclick>` （这是浏览器中 javascript 处理事件的写法）   
> 对应的 Markup UI 绑定语法：   
> `#!html <input @onclick>`


```xml
<button @onclick="{Save, parameter={Name, Age, Selected}}">
    保存
</button>
```

也可以用非内联写法，通过独立的 `@onclick.parameter` 属性声明参数列表：

```xml
<button
    @onclick="{Save}"
    @onclick.parameter="{Name, Age, Selected}">
    保存
</button>
```

两种写法等价，均在点击时依次读取 `Name`、`Age` 和 `Selected`，传给 `Save` 命令。

### 绑定命令

将“定义命令”中的 `PlayerObject` 实例作为数据上下文后，可绑定其 `Save` 命令：

```html
<button @onclick="{Save, parameter={TargetHealth, Confirmed}}">Save</button>
```

对应的非内联写法：

```html
<button
    @onclick="{Save}"
    @onclick.parameter="{TargetHealth, Confirmed}">
    Save
</button>
```

### 传递命令参数

#### 参数表达式

通过 `parameter={...}` 按顺序传入表达式：

```html
<button @onclick="{Save, parameter={Name}}">Save name</button>
<button @onclick="{MoveItem, parameter={@this, TargetIndex}}">Move</button>
```

第一例传入一个参数，第二例依次传入当前对象和 `TargetIndex`。内联与非内联写法见[事件](#command-events)。

参数列表可以使用属性路径、字面量、计算表达式和作用域名称：

```html
<button @onclick="{Adjust, parameter={Health + 10, 'bonus', true}}">
  Apply bonus
</button>
```

参数在事件匹配后、实际执行命令时按声明顺序求值，不是在页面加载时固定取值。SDK 根据命令声明检查参数数量、类型与是否为空；检查失败时不调用业务方法。

#### 无参数与空值参数

以下两种写法均不传参数：

```html
<button @onclick="{Save}">Save</button>
```
等价于
```html
<button @onclick="{Save, parameter={}}">Save</button>
```

!!! warning "空值参数不等于无参数"
    `parameter={null}` 传入一个空值参数，与没有参数不同。

### 命令路径与作用域

命令路径可以访问子对象或已声明的外层别名：

```html
<button @onclick="{Settings.Save}">Save settings</button>

<section @context="player" @as="player">
  <ul @for="{Items}">
    <li>
      <span>{{ Name }}</span>
      <button @onclick="{@player.RemoveItem, parameter={@this}}">Remove</button>
    </li>
  </ul>
</section>
```

循环中的命令通过 `@player` 定位玩家对象，参数 `@this` 是当前物品。命令与参数可以来自不同的作用域。

!!! note "命令路径不是函数调用"
    使用 `{Save}`，不写 `{Save()}` 或 `{Save(Name)}`。模板不执行 JavaScript；`onclick="Save()"` 也不会自动成为命令绑定。参数通过 `parameter` 声明。

### 参数转换器写法 {#command-parameter-converters}

参数列表中的单个参数可以使用嵌套绑定表达式声明转换器；转换器自身的参数放在其 `parameter` 中。以下示例展示语法形式。

!!! warning "命令参数暂不执行转换器"
    以下写法仅用于说明语法。当前版本在调用命令前不执行参数中的转换器。用于文本显示和输入写回的转换器见[值转换器](value-converters.md)。

内联写法：

```xml
<button @onclick="{Save, parameter={
    {Name, converter=Trim},
    {Age, converter={ToInt, parameter={10}}},
    Selected
}}">
    保存
</button>
```

非内联写法：

```xml
<button
    @onclick="{Save}"
    @onclick.parameter="{
        {Name, converter=Trim},
        {Age, converter={ToInt, parameter={10}}},
        Selected
    }">
    保存
</button>
```

`converter=Trim` 为 `Name` 声明转换器；`converter={ToInt, parameter={10}}` 为 `Age` 声明转换器，并向转换器传入 `10`。`Selected` 未声明转换器。这些转换器名称仅用于展示语法，不表示当前提供对应的内置实现。

### 命令执行条件

命令路径必须定位当前上下文中的有效命令。命令缺失或命令字段为空时，当前调用会跳过并记录警告，不影响其他绑定；之后上下文或命令变化，后续事件仍可重新解析。

!!! note "CanExecute 与控件状态"
    模板事件在执行前查询无参数的 `CanExecute()`，返回 `false` 时跳过执行。直接调用 `Execute` 不会自动查询 `CanExecute()`。当前 `CanExecuteChanged` 仅提供本地通知，不会自动更新控件状态；需要通过显式属性绑定表达可用状态。

例如，应用提供布尔属性 `CanSave` 和 `Save` 命令：

```html
<button @disabled="{!CanSave}" @onclick="{Save}">Save</button>
```

`CanSave` 变化时需要属性通知。命令自身仍应校验当前业务状态，不能仅依赖按钮外观判断是否可以执行。

### 输入写回与命令顺序 {#command-update-order}

**按事件触发时机执行，HTML 属性前后顺序不影响结果。同一次事件同时触发回写和命令时，先回写，再执行命令。**

以文本框为例，用户编辑后失去焦点，且回写成功时：

| 回写设置 | `oninput` 命令 | `onchange` 命令 | `onblur` 命令 |
| --- | --- | --- | --- |
| `update=input` | 新值 | 新值 | 新值 |
| `update=change` | <span class="text-warning">:bootstrap-exclamation-triangle: 旧值</span> | 新值 | 新值 |
| `update=blur` | <span class="text-warning">:bootstrap-exclamation-triangle: 旧值</span> | 新值 | 新值 |
| 省略 `update`（默认 `blur`） | <span class="text-warning">:bootstrap-exclamation-triangle: 旧值</span> | 新值 | 新值 |
| `update=explicit` | <span class="text-warning">:bootstrap-exclamation-triangle: 旧值</span> | <span class="text-warning">:bootstrap-exclamation-triangle: 旧值</span> | <span class="text-warning">:bootstrap-exclamation-triangle: 旧值</span> |

- 复选框的 `@checked`、选择框的值默认按 `change` 回写：同一次 `change` 中先回写，再执行 `onchange` 命令。
- 点击、键盘等命令按各自事件发生时执行，不会强制提前提交等待 `blur`、`change` 或显式提交的值。
- 命令参数在命令执行时读取数据上下文。如果回写转换或写入失败，读取的是数据上下文中的实际值。

下面两种写法行为相同：

```html
<input @value="{Name, update=input}" @oninput="{Save, parameter={Name}}">
<input @oninput="{Save, parameter={Name}}" @value="{Name, update=input}">
```

#### 集合元素回写

将输入绑定指向可写的集合元素，并绑定同一输入事件的命令：

```html
<input type="number"
  @value="{Numbers[0], mode=twoWay, update=input}"
  @oninput="{Save, parameter={Numbers[0]}}">
```

先将输入值赋给 `Numbers[0]`，再执行 `Save`，因此命令参数读取的是更新后的 `Numbers[0]`。

嵌套集合也采用相同顺序：

```html
<input type="number"
  @value="{SharedRows[0][2], mode=twoWay, update=input}"
  @oninput="{Save, parameter={SharedRows[0][2]}}">
```

`SharedRows[0]` 必须是可写的共享可观察集合。按值嵌套的子集合元素不支持回写，命令不能取得本次输入后的值，详见[按值嵌套不支持回写](observable-objects.md)。

### 支持的事件

| 事件绑定 | 触发含义 |
| --- | --- |
| `@onclick` | 点击或激活 |
| `@oninput` | 编辑过程中输入值变化 |
| `@onchange` | 用户提交一次实际的控件值变化 |
| `@onsubmit` | 表单提交 |
| `@onfocus` | 获得焦点 |
| `@onblur` | 失去焦点 |
| `@onkeydown` | 按键按下 |
| `@onkeyup` | 按键释放 |
| `@onpointerdown` | 指针按下 |
| `@onpointerup` | 指针抬起 |

这是当前模板命令绑定支持的完整事件集合。`@ondblclick`、`@oncontextmenu`、`@onreset`、`@onwheel`、`@onscroll` 以及指针移动、进入、离开、取消等事件尚未开放为模板命令绑定，不能仅凭标准 HTML 中存在相应名称就直接使用。

#### 输入与焦点事件

```html
<input
  @value="{Name, update=input}"
  @oninput="{NameEdited, parameter={Name}}"
  @onfocus="{BeginEditing}"
  @onblur="{EndEditing}">
```

`input` 表示编辑值变化，不等于一次按键；删除、粘贴及输入法组字都可能产生输入变化。`change` 表示实际变化的提交，文本编辑通常在编辑结束并失焦、且值确实变化时产生。单纯获得或失去焦点分别对应 `focus`、`blur`。

事件绑定与 `update` 的用途不同：`@oninput` 调用命令，`update=input` 决定何时写回输入值。两者可以分别配置，详见[输入与双向绑定](input-and-two-way-binding.md)。

### 事件过滤

过滤条件必须是静态值，不接受 `{Expression}`。条件值忽略大小写，选项名使用小写；重复名称、未知修饰键或空组合无效。未匹配的事件不求值参数、不执行命令，也不会阻止其他监听者或取消默认动作。

#### 键盘事件

`@onkeydown` 和 `@onkeyup` 支持静态 `key`、`modifiers` 过滤，只在匹配时执行命令：

```html
<input
  @onkeydown="{Save}"
  @onkeydown.key="s"
  @onkeydown.modifiers="Control">
```

也可以将条件写在绑定内：

```html
<input @onkeyup="{Save, key='Enter', modifiers=Control+Shift}">
```

| 选项 | 含义 | 省略时 |
| --- | --- | --- |
| `key` | 匹配逻辑按键名称，如 `Enter`、`Escape`、`s` | 不限制按键 |
| `modifiers` | 精确匹配修饰键组合 | 不限制修饰键 |

`key` 匹配逻辑 Key，不是物理键盘 Code；名称忽略大小写。空格可写 `key=' '`，加号可写 `key='+'`。

`modifiers` 支持 `Control`、`Shift`、`Alt`、`Windows`、`Meta`，多个名称用 `+` 连接，顺序不影响匹配。`Meta` 与 `Windows` 表示同一修饰键，不能同时填写。`Control` 不匹配额外按住 `Shift` 的 `Control+Shift`。

!!! note "none 表示不限制"
    `key=none`、`modifiers=none` 与省略对应选项相同，表示不过滤，不表示“没有按键”或“必须不按修饰键”。`none` 不能与其他修饰键组合。

#### 鼠标事件

`@onclick`、`@onpointerdown`、`@onpointerup` 支持 `button` 和 `modifiers`：

```html
<button @onclick="{Save, button=Left, modifiers=Control}">Save</button>

<div
  @onpointerdown="{Select}"
  @onpointerdown.button="Right">
  Select with right button
</div>
```

`button` 支持 `Left`、`Middle`、`Right`、`Back`、`Forward` 和 `none`，忽略大小写。它匹配本次事件触发的鼠标键，不是当前所有按住的键。省略或写 `none` 表示不限制，修饰键规则与键盘过滤相同。

`key` 仅用于键盘事件，`button` 仅用于这三种鼠标或指针事件，不能互换。

!!! note "过滤不会产生新的事件"
    `@onclick` 仍依赖平台实际产生的点击事件，`button=Right` 不会自动生成右键菜单事件。处理右键按下或抬起可使用 `@onpointerdown`、`@onpointerup`。

### 选项与平台限制

- 事件绑定本身不支持 `converter`、`update` 或双向绑定模式。参数表达式中的转换器写法见[参数转换器写法](#command-parameter-converters)。
- `template` 不生成可交互元素，不能在其上绑定元素事件；应将事件写在实际生成的按钮等元素上。
- 当前没有通过模板取消默认动作或阻止事件传播的语法，命令返回值也不作为这些操作的开关。

事件是否产生、焦点与输入法如何接入，以及命令处理中的平台操作，应以各平台插件的实际能力为准。模板支持事件名称，不代表浏览器中的所有默认行为均已实现。

[^command-platform-scalar]: Platform Scalar 指各平台（如 Unity、Unreal Engine）支持的原生标量类型。

[^command-object]: Object 指可观察对象或平台特定的支持对象。

[^command-shared]: C++ 使用 `std::shared_ptr<T>`；C# 使用引用类型。

[^command-weak]: C++ 使用 `std::weak_ptr<T>`；C# 使用 `WeakReference<T>`。
