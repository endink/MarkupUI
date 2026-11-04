---
icon: bootstrap/globe2
---

# 全局命令

全局命令是在 SDK 库实例范围内注册的命令，页面通过 `@sys.命令名` 调用，不依赖当前数据上下文。适用于播放音效等供多个页面共用的业务操作。

与[数据上下文中的命令](events-and-commands.md)不同，全局命令由应用统一注册和管理。SDK 不提供内置的 `PlaySound` 命令，下面的名称和播放逻辑均由应用定义。

## 定义与注册

先创建强类型命令对象，再注册名称。注册时只填写名称，例如 `'PlaySound'`，不包含 `@sys.` 前缀。名称区分大小写，首字符只能为 ASCII 字母或下划线，后续可以包含数字。

以下示例均接收一个字符串参数。`PlaySound` 中接入应用或引擎的音频服务；注册代码在应用初始化时执行一次，并在页面使用期间保留注册句柄。

=== "C++"

    ```cpp
    #include <cstdio>
    #include <memory>
    #include <markupui/binding/data_binding.h>
    #include <markupui/binding/delegate_command.h>

    void PlaySound(MarkupUI::StringView name)
    {
        // 调用业务音频服务，播放 name 对应的音效。
    }

    // 在应用初始化流程中执行，变量由应用生命周期管理对象持有。
    auto command = std::make_shared<
        MarkupUI::Binding::DelegateCommand<MarkupUI::StringView>>(&PlaySound);

    auto registration = MarkupUI::Binding::RegisterGlobalCommand(
        MARKUPUI_STR_VIEW("PlaySound"), command);

    if (!registration.IsValid())
    {
        std::fputs("Could not register PlaySound.\n", stderr);
        return;
    }
    ```

    必须传入指向强类型 `ICommand<TArgs...>` 的共享指针。不能直接传入裸指针或函数指针，也不能只提供 `ICommandBase` 指针。本例使用 `std::shared_ptr` 持有 `DelegateCommand`。

=== "C#"

    ```csharp
    using System;
    using MarkupUI.Sdk.Binding;

    static void PlaySound(string name)
    {
        // 调用业务音频服务，播放 name 对应的音效。
    }

    // 在应用初始化流程中执行，变量由应用生命周期管理对象持有。
    var command = new DelegateCommand<string>(PlaySound);
    var registration = DataBindingUtilities.RegisterGlobalCommand(
        "PlaySound", command)
        ?? throw new InvalidOperationException(
            "Could not register PlaySound.");
    ```

    注册入口接收 `ICommand` 或泛型 `ICommand<T1, ...>`。先使用 `DelegateCommand` 包装业务函数，或提供已有命令对象，再传给 `DataBindingUtilities.RegisterGlobalCommand`。

重复或非法名称会导致注册失败：C++ 返回无效句柄，C# 返回 `null`。同名注册不会替换已注册的命令。

## 页面调用

### 元素事件

使用 `@sys.PlaySound` 指定全局命令，通过 `parameter` 传入参数。以下按钮点击时播放名称为 `'click'` 的音效，无需设置数据上下文：

```html
<button @onclick="{@sys.PlaySound, parameter={'click'}}">开始</button>
```

对应的非内联写法：

```html
<button
    @onclick="{@sys.PlaySound}"
    @onclick.parameter="{'click'}">
    开始
</button>
```

命令来自全局注册表，参数仍可来自当前元素的数据上下文。例如，当前上下文提供 `SoundName` 属性时：

```html
<button @onclick="{@sys.PlaySound, parameter={SoundName}}">播放</button>
```

## 参数与执行规则

- 全局命令支持 0～10 个强类型参数，参数数量、类型和[数据类型兼容](events-and-commands.md)规则与数据上下文中的命令一致。全部参数检查成功后才执行业务函数。
- 页面执行前查询命令的无参数 `CanExecute()`；返回 `false` 时跳过执行。
- 每次执行都查找当前注册的命令。找不到名称时记录诊断并跳过，不回退到数据上下文查找同名命令。
- `@sys` 是保留名称，用于直接指定全局命令，不能用于普通属性绑定、命令参数或任意静态成员访问。
- 命令在文档的数据线程执行。业务操作要求引擎主线程时，由应用负责调度。

## 撤销注册

!!! warning "通常无需撤销全局命令"
    全局命令通常在应用初始化时注册，并在应用运行期间持续保留，不应随页面关闭而撤销。仅在应用退出、卸载相关模块或明确停止提供该命令时撤销注册；撤销后，所有页面都无法再通过该名称调用命令。

注册句柄持续保留命令对象。需要撤销时，使用以下接口：

=== "C++"

    ```cpp
    registration.Reset();
    command.reset();
    ```

    注册句柄析构时也会自动撤销注册。

=== "C#"

    ```csharp
    registration.Dispose();
    ```

撤销后，后续查找不再找到该命令，已经开始的调用仍可完成。撤销后可以重新注册同名命令。SDK 运行时停止或重新启动不会自动撤销注册，应由应用管理注册句柄。

!!! warning "全局命令生命周期"
    在页面仍需调用命令时保留注册句柄。卸载包含业务回调的模块前，先撤销注册，并确保所有在途调用已经结束。
