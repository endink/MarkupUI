---
icon: bootstrap/broadcast
---

# 触发器

命令和触发器用于连接 UI 与业务代码，区别在于通知的起点：

- **命令**：UI 事件通知业务代码执行逻辑。例如，用户点击保存按钮，通过绑定的命令执行保存操作。
- **触发器**：业务代码通知 UI 执行 HTML 中声明的行为。例如，应用收到“打开背包”输入动作后，触发 UI 更新，替换背包元素的 CSS 类。

应用中的输入动作、任务完成或其他业务事件不一定来自 HTML 元素。需要让这些事件驱动 UI 行为时，可以使用触发器，将事件来源与页面中的行为声明连接起来。触发器既可以更新元素属性，也可以执行页面绑定的命令。

![命令由 UI 事件通知业务代码，触发器由业务事件通知 UI 执行声明的行为](images/commands-and-triggers.svg)

## 语法

使用 `@trigger` 声明触发器，表达式由名称、参数和行为三部分构成：

- **名称**：`name` 指定已注册的触发器。
- **参数**：`parameter={...}` 保存触发器的自定义参数，可以包含多个字符串参数。
- **行为**：使用 `do:` 前缀声明触发后执行的行为。

```html
<!-- name：已注册的触发器名称 -->
<!-- 外层 parameter：传给触发器的自定义参数 -->
<!-- do:command 中的 parameter：传给 Save 命令的参数 -->
<section @trigger="{
    name='mytrigger',
    parameter={param1='value1', param2='value2'},
    do:command={Save, parameter={Name, Age, Selected}},
    do:class={value='active', op='append'}
}">
    <p>{{ Status }}</p>
</section>
```

非内联写法可以将自定义参数和行为拆成独立属性。

```html
<section
    @trigger="{name='mytrigger'}"
    @trigger.parameter="{param1='value1', param2='value2'}"
    @trigger.do.command="{Save, parameter={Name, Age, Selected}}"
    @trigger.do.class="{value='active', op='append'}">
    <p>{{ Status }}</p>
</section>
```

两种写法等价。非内联写法用 `@trigger.parameter` 声明自定义参数，用 `@trigger.do.command`、`@trigger.do.class` 声明行为。同一配置项或行为只能声明一次。

!!! warning "触发器名称必须写在主属性中"
    即使将参数和行为拆成独立属性，也必须在 `@trigger` 的属性值中声明 `name`，例如 `@trigger="{name='mytrigger'}"`。`@trigger.name` 不是合法的触发器属性。

!!! note "触发器参数"
    - 触发器可以定义多个参数。`param1`、`param2` 仅为示例名称；实际参数名称、含义和校验规则由具体触发器定义。
    - 参数只接受字符串字面量，例如 `param1='value1'`。语法也允许省略单引号；本文示例统一保留单引号。
    - 参数不支持数据绑定、属性路径求值或其他绑定表达式，不会随数据上下文变化而更新。

## 行为

行为声明触发后执行的操作。`do:command` 和 `do:class` 由 SDK 执行，不作为自定义参数传给触发器。

每组行为属于声明 `@trigger` 的当前元素。更新元素属性的行为只修改该元素，例如 `do:class` 不会修改父元素、子元素或其他声明了相同触发器的元素。`do:command` 则从该元素的有效数据上下文查找命令，业务代码执行后的影响由命令本身决定。

### 行为数据上下文

行为中的绑定表达式遵循当前元素的数据上下文和作用域规则。未指定命名上下文或别名时，命令路径、命令参数及属性绑定均从当前元素的默认数据上下文解析；该上下文可以由祖先元素继承，也可以通过 `@context` 指定。

例如，假设已注册 `mytrigger`，命名上下文 `player` 提供 `Save` 命令和 `Name` 属性：

```html
<section @context="player">
    <input
        @value="{Name}"
        @trigger="{
            name='mytrigger',
            parameter={param1='value1'},
            do:command={Save, parameter={Name}},
            do:class={value='saved', op='append'}
        }">
</section>
```

当这个 `<input>` 对应的触发器触发时：

1. 从 `<input>` 当前继承的 `player` 数据上下文读取 `Save` 和 `Name`。
2. 调用 `Save`，将读取到的 `Name` 作为命令参数；参数来自数据上下文，不是直接读取输入框的 DOM 值。
3. 向该 `<input>` 的 `class` 属性追加 `saved`，已存在时不重复追加，父级 `<section>` 不受此属性更新影响。

命令和绑定值在每次触发执行时重新读取。需要访问其他上下文时，可在表达式中使用已声明的命名上下文或作用域别名，详见[数据上下文](../concepts/data-context.md)。

### SDK 支持的行为

| 行为 | 用途 | 回弹 |
| --- | --- | --- |
| `do:command` | 执行绑定的命令；每次触发时重新读取命令和参数 | |
| `do:class` | 激活时追加或替换元素的 CSS 类；停用时恢复激活前的状态 | <span class="text-success" aria-label="支持">:bootstrap-check-circle-fill:</span> |

> 回弹的触发条件和恢复规则见本文后面的[回弹](#trigger-revert)小节。

### command 行为

`do:command` 可以执行当前元素数据上下文中的命令，也可以调用已注册的[全局命令](global-commands.md)：

- `{Save, parameter={Name}}`：从当前数据上下文查找 `Save`，并读取 `Name` 作为参数。
- `{@sys.PlaySound, parameter={'open'}}`：从全局注册表查找 `PlaySound`，不依赖当前数据上下文。

例如，假设已注册 `mytrigger` 触发器和 `PlaySound` 全局命令：

```html
<section @trigger="{
    name='mytrigger',
    do:command={@sys.PlaySound, parameter={'open'}}
}"></section>
```

全局命令的参数也可以来自当前元素的数据上下文，例如 `{@sys.PlaySound, parameter={SoundName}}`。命令来源与参数来源分别解析；使用 `@sys` 不会改变参数的数据上下文。

### class 行为

使用 `value` 指定 CSS 类，`op` 指定操作。`op` 省略时默认为 `'append'`。

| 字段 | 用途 |
| --- | --- |
| `value` | 必填；字符串字面量或绑定表达式，例如 `'active'` 或 `{ActiveClasses}` |
| `op` | `'append'` 追加尚不存在的类名；`'replace'` 替换完整的 `class` 属性 |

例如，元素最初具有 `panel` 类，触发器配置如下：

```html
<section class="panel" @trigger="{
    name='mytrigger',
    do:class={value='active', op='append'}
}"></section>
```

调用 `Activate()` 后，元素保留 `panel` 并追加 `active`。以下仅展示行为更新后的 HTML 属性：

```html
<section class="panel active"></section>
```

如果将操作改为 `op='replace'`，激活后会移除原有的 `panel`，结果为：

```html
<section class="active"></section>
```

两种操作在调用 `Deactivate()` 后都会恢复激活前的状态：

```html
<section class="panel"></section>
```

`value` 中的绑定只在 `Activate()` 时求值，不建立持续订阅。`op` 为固定字符串，不支持绑定表达式。字符串和单个表达式的简写仍可使用，例如 `do:class='active'`。

!!! warning "replace 会替换完整属性"
    `op='replace'` 会替换元素原有的全部 CSS 类；默认的 `op='append'` 保留原有类，并按空白分隔的独立类名去重追加。

外层 `parameter` 配置触发器参数；`do:command` 内的 `parameter` 配置命令参数，两者用途不同。命令路径、作用域和参数类型遵循[事件与命令](events-and-commands.md)的规则。

## 实现触发器

以下实现注册名为 `input` 的触发器，接收字符串参数 `action`。与之配套的 HTML 如下：

```html
<section @trigger="{
    name='input',
    parameter={action='inventory.open'},
    do:command={Save, parameter={Name, Age, Selected}},
    do:class={value='inventory-open', op='append'}
}">
    <p>{{ Status }}</p>
</section>
```

`input` 和 `action` 均由本例定义，可替换为实际项目的触发器名称和参数。

每个实际使用触发器的元素都有独立实例，包括条件分支和集合循环创建的元素。实现分为事件源、触发器和工厂三部分。

- 事件源：提供应用或引擎事件，以下使用可替换的示例事件源。
- 触发器：`Attach()` 校验参数并订阅事件，事件回调调用 `Activate()`，`Detach()` 解除订阅。
- 工厂：实现 `ISyntaxTriggerFactory`，为每个元素创建独立触发器。

!!! warning "在数据线程订阅和触发"
    工厂创建、`Attach()`、`Detach()` 和 `Activate()` 均在文档配置的数据线程执行。宿主事件来自其他线程时，先调度到该数据线程，再发布事件。

=== "C++"

    假设业务系统已提供以下事件源。这里只列出头文件声明；订阅管理和事件分发由业务系统实现，所有调用均在数据线程执行。

    ```cpp
    // input_events.h
    #pragma once

    #include <cstdint>
    #include <functional>
    #include <string>

    namespace Example
    {
        class InputEvents final
        {
        public:
            // 订阅指定动作，返回用于解除订阅的令牌。
            uint64_t Subscribe(
                std::string action,
                std::function<void()> callback);

            void Unsubscribe(uint64_t token);

            // 发布动作，调用匹配的订阅回调。
            void Publish(const std::string& action);
        };
    }
    ```

    触发器（`input_trigger.h`）：

    ```cpp
    // input_trigger.h
    #pragma once
    
    #include "input_events.h"
    
    #include <cstdio>
    #include <markupui/binding/syntax/syntax_trigger.h>
    
    #include <memory>
    #include <string>
    #include <utility>
    
    namespace Example
    {
        class InputTrigger final
            : public MarkupUI::Binding::Syntax::ISyntaxTrigger
        {
        public:
            explicit InputTrigger(std::shared_ptr<InputEvents> events)
                : Events(std::move(events))
            {
            }
    
            // 保留 noexcept；预期失败返回 false。
            bool Attach(
                const MarkupUI::Binding::Syntax::SyntaxTriggerContext& context,
                const MarkupUI::Binding::Syntax::SyntaxArguments& arguments)
                noexcept override
            {
                Detach();
    
                MarkupUI::StringView action;
                if (!arguments.TryGetString(
                        MARKUPUI_STR_VIEW("action"), action)
                    || action != MARKUPUI_STR_VIEW("inventory.open"))
                {
                    context.ReportError(
                        MARKUPUI_STR_VIEW(
                            "action must be 'inventory.open'."));
                    return false;
                }
    
                MarkupUI::Binding::Syntax::SyntaxTriggerRef trigger =
                    context.GetTrigger();
    
                if (!trigger.IsValid())
                {
                    return false;
                }
    
                // 参数视图只在 Attach 期间有效，订阅时复制名称。
                std::string actionName(action.Data, action.Size);
    
                SubscriptionToken = Events->Subscribe(
                    std::move(actionName),
                    [trigger]()
                    {
                        // 当前已经位于数据线程。
                        // SDK 负责执行 HTML 中声明的全部行为。
                        if (!trigger.Activate())
                        {
                            std::fputs("Trigger is unavailable; actions were not submitted.\n", stderr);
                        }
                    });
    
                return true;
            }
    
            // 保留 noexcept，清理过程不得向外抛出异常。
            void Detach() noexcept override
            {
                const uint64_t token = SubscriptionToken;
                SubscriptionToken = 0;
    
                if (token != 0)
                {
                    Events->Unsubscribe(token);
                }
            }
    
        private:
            std::shared_ptr<InputEvents> Events;
            uint64_t SubscriptionToken = 0;
        };
    }
    ```

    工厂（`input_trigger_factory.h`）：

    ```cpp
    // input_trigger_factory.h
    #pragma once
    
    #include "input_trigger.h"
    
    #include <markupui/binding/syntax/syntax_trigger_factory.h>
    
    #include <memory>
    #include <utility>
    
    namespace Example
    {
        class InputTriggerFactory final
            : public MarkupUI::Binding::Syntax::ISyntaxTriggerFactory
        {
        public:
            explicit InputTriggerFactory(
                std::shared_ptr<InputEvents> events)
                : Events(std::move(events))
            {
            }
    
            // 保留 noexcept。
            MarkupUI::SharedReference Create() noexcept override
            {
                return ShareTrigger(
                    std::make_shared<InputTrigger>(Events));

                // 预期失败返回空引用。
                // return nullptr;
            }
    
        private:
            std::shared_ptr<InputEvents> Events;
        };
    }
    ```



=== "C#"

    事件源：

    ```csharp
    using System;
    
    public sealed class InputSource
    {
        public event EventHandler? InventoryOpen;
    
        public void RaiseInventoryOpen()
        {
            InventoryOpen?.Invoke(this, EventArgs.Empty);
        }
    }
    ```

    触发器：

    ```csharp
    using System;
    using MarkupUI.Sdk.Binding.Syntax;
    
    public sealed class InputTrigger : ISyntaxTrigger
    {
        private readonly InputSource _input;
        private SyntaxTriggerRef? _trigger;
    
        public InputTrigger(InputSource input)
        {
            _input = input;
        }
    
        public bool Attach(
            SyntaxTriggerContext context,
            SyntaxArguments arguments)
        {
            if (!arguments.TryGetString("action", out string? action)
                || action != "inventory.open")
            {
                context.ReportError(
                    "action must be 'inventory.open'.");
                return false;
            }
    
            _trigger = context.GetTrigger();
            if (_trigger == null)
            {
                return false;
            }
    
            _input.InventoryOpen += OnInventoryOpen;
            return true;
        }
    
        public void Detach()
        {
            // Attach 部分失败时也可能调用，清理应允许重复执行。
            _input.InventoryOpen -= OnInventoryOpen;
    
            SyntaxTriggerRef? trigger = _trigger;
            _trigger = null;
            trigger?.Dispose();
        }
    
        private void OnInventoryOpen(object? sender, EventArgs args)
        {
            // 当前必须位于文档的数据线程。
            _trigger?.Activate();
        }
    }
    ```

    工厂：

    ```csharp
    using MarkupUI.Sdk.Binding.Syntax;
    
    public sealed class InputTriggerFactory : ISyntaxTriggerFactory
    {
        private readonly InputSource _input;
    
        public InputTriggerFactory(InputSource input)
        {
            _input = input;
        }
    
        public ISyntaxTrigger Create()
        {
            return new InputTrigger(_input);
        }
    }
    ```

    上下文和参数不能保存到字段或异步回调；保存 `GetTrigger()` 返回的引用，并在 `Detach()` 中释放。`Detach()` 也可能在 `Attach()` 部分失败后调用，清理应允许重复执行。

本例假设数据上下文已提供 `Name`、`Age`、`Selected`、`Status` 属性，以及依次接收姓名、年龄和选中状态的 `Save` 命令。命令定义方式见[事件与命令](events-and-commands.md)。触发器无需自行查找或执行命令。

## 注册与触发

在页面激活前注册扩展，并在应用或插件的生命周期管理对象中保留注册句柄。名称在 SDK 库实例内全局注册，同名注册失败。

=== "C++"

    ```cpp
    #include "input_trigger_factory.h"
    
    #include <markupui/binding/syntax/syntax_trigger_registration.h>
    
    #include <memory>
    
    std::shared_ptr<Example::InputEvents> inputEvents =
        std::make_shared<Example::InputEvents>();
    
    std::shared_ptr<Example::InputTriggerFactory> factory =
        std::make_shared<Example::InputTriggerFactory>(inputEvents);
    
    MarkupUI::Binding::Syntax::SyntaxTriggerRegistration registration =
        MarkupUI::Binding::Syntax::SyntaxTriggerRegistration::Register(
            MARKUPUI_STR_VIEW("input"),
            factory);
    
    if (!registration.IsValid())
    {
        // 注册失败，例如名称已被注册。
        return;
    }
    ```

    为文档设置数据上下文并打开包含上述 HTML 的页面。元素激活后，SDK 自动调用 `Attach()`；收到输入动作时，在数据线程发布事件：

    ```cpp
    inputEvents->Publish("inventory.open");
    ```

    先关闭使用扩展的页面，再撤销注册：

    ```cpp
    registration.Reset();
    factory.reset();
    inputEvents.reset();
    ```

=== "C#"

    以下代码假设 SDK 已初始化。变量应由应用或插件持有，不能在页面仍使用扩展时离开 `using` 作用域：

    ```csharp
    var input = new InputSource();
    var registration = SyntaxTriggerRegistration.Register(
        "input", new InputTriggerFactory(input))
        ?? throw new InvalidOperationException("Trigger registration failed.");
    var player = new PlayerObject();
    ```

    为现有文档设置 `player` 数据上下文并打开页面，等待文档就绪后再发布事件。`dataDispatcher` 是初始化时配置的数据线程 Dispatcher：

    ```csharp
    bool dispatched = dataDispatcher.Invoke(input.RaiseInventoryOpen);
    ```

    退出时先关闭页面，再撤销注册；页面使用期间保留数据对象：

    ```csharp
    await document.CloseAsync();
    GC.KeepAlive(player);
    registration.Dispose();
    ```

!!! warning "触发器生命周期"
    撤销注册只影响后续查找，不会主动停止已经创建的触发器。   
    使用该触发器的页面全部关闭、实例释放后，才能卸载包含回调代码的模块。

## 回弹 {#trigger-revert}

有些界面效果只需要在特定条件持续期间生效。例如，鼠标进入物品卡片时显示高亮边框，离开后恢复原来的外观。如果只有执行行为，就需要分别定义“添加高亮”和“取消高亮”两套操作，还要自行保留卡片原有的 CSS 类，避免取消高亮时丢失其他样式。

回弹让同一组行为支持激活与恢复：触发器在鼠标进入时调用 `Activate()`，应用高亮类；离开时调用 `Deactivate()`，SDK 恢复首次激活前的 `class` 状态。无需再定义一套反向的 class 行为，也无需由业务代码记录原有类名。

这里的鼠标事件由自定义触发器订阅。宿主仍需在对应的结束事件中调用 `Deactivate()`，恢复过程由 SDK 完成；例如按住按键期间显示操作提示，也可以在按下时激活、松开时回弹。

!!! note "回弹需要触发器与行为共同支持"
    - 触发器逻辑必须在适当时机调用 `Deactivate()`，否则不会回弹。
    - 行为本身必须支持回弹。`class` 行为支持恢复激活前的状态；`command` 行为不支持回弹，即使触发器调用了 `Deactivate()`，也不会再次执行命令或撤销已执行的业务逻辑。

假设元素原有 `class="panel"`，行为配置为 `do:class={value='active', op='append'}`：

| 操作 | 元素的 class | 说明 |
| --- | --- | --- |
| 首次调用 `Activate()` | `panel active` | 保存原始状态 `panel`，追加 `active` |
| 再次调用 `Activate()` | `panel active` | 不重复追加，也不覆盖已保存的原始状态 |
| 调用 `Deactivate()` | `panel` | 恢复首次激活前的状态 |
| 再次调用 `Deactivate()` | `panel` | 已停用，不再改变状态 |

- `'append'` 和 `'replace'` 都支持回弹。原本没有 `class` 属性时，停用后移除该属性。
- 激活期间普通绑定产生的 `class` 更新不会改变恢复目标。停用后再次激活，会重新保存当时的状态。
- 回弹仅恢复 `class`，不会撤销 `do:command` 已执行的业务逻辑，也不会在停用时再次执行命令。

以下调用均需在文档的数据线程执行，`trigger` 是 `Attach()` 中取得并保存的触发引用：

=== "C++"

    ```cpp
    // 业务事件开始，例如按下输入动作。
    trigger.Activate();

    // 业务事件结束，例如松开输入动作，恢复原有 class。
    trigger.Deactivate();
    ```

=== "C#"

    ```csharp
    // 业务事件开始，例如按下输入动作。
    trigger.Activate();

    // 业务事件结束，例如松开输入动作，恢复原有 class。
    trigger.Deactivate();
    ```

## 生命周期与执行结果

1. 元素激活时，SDK 查找工厂、创建实例并调用 `Attach()`。未注册的名称会导致激活失败并记录诊断。
2. 宿主事件发生后，触发器调用 `Activate()`。SDK 在执行时读取当前上下文中的命令和参数，不保存旧上下文的数据。
3. 页面关闭、条件分支移除或集合元素移除时，SDK 使触发引用失效并调用 `Detach()`。`Attach()` 失败时也会清理已完成的部分订阅。

`Activate()` 返回成功只表示行为已提交，不表示命令或页面更新已经完成。行为按声明顺序提交，遇到失败停止；`class` 的页面更新是异步提交。`Deactivate()` 只撤销 class 覆盖，不执行或撤销命令；重复停用无副作用。`Activate()` 和 `Deactivate()` 都必须在数据线程调用，返回成功仅表示提交成功。

`SyntaxTriggerRef` 不保活元素或文档。元素解绑后，旧引用的 `Activate()` 返回 `false`；C++ 的 `IsValid()` 仅表示引用包装存在，不能用于判断元素仍然有效。C# 引用包装被 `Dispose()` 后再次调用 `Activate()` 会抛出 `MarkupObjectDisposedException`。
