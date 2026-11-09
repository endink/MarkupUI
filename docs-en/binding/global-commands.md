---
icon: bootstrap/globe2
---

# Global Commands

A global command is registered for an SDK library instance. A page calls it with `@sys.command-name`, independently of the current data context. Use global commands for actions shared by multiple pages, such as playing a sound effect.

The application registers and manages global commands separately from [commands in the data context](events-and-commands.md). In the following example, the application defines the `PlaySound` command and its playback logic.

## Definition and registration

First, create a strongly typed command object, and then register its name. When registering, only the name needs to be specified, for example, `'PlaySound'`. The name should not include the `@sys.` prefix. Names are case-sensitive, with the first character being either an ASCII letter or an underscore. Subsequent characters can be digits.

All of the following examples accept a string parameter. In `PlaySound`, the audio service of the application or engine is used. The registration code is executed once during application initialization, and the registered handle is retained during the page usage period.

=== "C++"

    ```cpp
    #include <cstdio>
    #include <memory>
    #include <markupui/binding/data_binding.h>
    #include <markupui/binding/delegate_command.h>

    void PlaySound(MarkupUI::StringView name)
    {
        // Call the application's audio service to play the sound identified by name.
    }

    // Run this during application initialization and let the application lifetime owner hold the variable.
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

    It is necessary to pass a shared pointer to the strongly typed `ICommand<TArgs...>`. It is not possible to pass a raw pointer or a function pointer directly, nor can only `ICommandBase` pointer be provided. In this example, `std::shared_ptr` is used to hold `DelegateCommand`.

=== "C#"

    ```csharp
    using System;
    using MarkupUI.Sdk.Binding;

    static void PlaySound(string name)
    {
        // Call the application's audio service to play the sound identified by name.
    }

    // Run this during application initialization and let the application lifetime owner hold the variable.
    var command = new DelegateCommand<string>(PlaySound);
    var registration = DataBindingUtilities.RegisterGlobalCommand(
        "PlaySound", command)
        ?? throw new InvalidOperationException(
            "Could not register PlaySound.");
    ```

    The registration entry receives `ICommand` or generic `ICommand<T1, ...>`. First, wrap the business function with `DelegateCommand`, or provide an existing command object, and then pass it to `DataBindingUtilities.RegisterGlobalCommand`.

Duplicate or invalid names can lead to registration failures: C++ returns an invalid handle, while C# returns `null`. Commands with the same name will not replace already registered commands.

## Page invocation

### Element events

Use `@sys.PlaySound` to specify global commands, with parameters passed through `parameter`. The sound with the name `'click'` is played when the button is clicked. No data context needs to be set:

```html
<button @onclick="{@sys.PlaySound, parameter={'click'}}">开始</button>
```

Corresponding non-inline notation:

```html
<button
    @onclick="{@sys.PlaySound}"
    @onclick.parameter="{'click'}">
    开始
</button>
```

Commands come from the global registry, and parameters can still come from the current element's data context. For example, when the current context provides the `SoundName` property:

```html
<button @onclick="{@sys.PlaySound, parameter={SoundName}}">播放</button>
```

## Parameters and execution rules

- Global commands support 0 to 10 strongly typed parameters. The number, type of parameters, and [data type compatibility](events-and-commands.md) rules are consistent with those of commands in the data context. The business function is only executed after all parameter checks are successful.
- The `CanExecute()` function checks commands without parameters before page execution. If it returns `false`, the execution is skipped.
- Each execution searches for the currently registered commands. If the command name is not found, a diagnostic is recorded and the execution is skipped. The system does not revert to the data context to search for commands with the same name.
- `@sys` is a reserved name used to directly specify global commands. It cannot be used for ordinary property binding, command parameters, or access to any static members.
- Commands are executed in the data thread of the document. When business operations require the main thread of the engine, the application is responsible for scheduling them.

## Unregister commands

!!! warning "Generally, there is no need to unregister global commands"
    Global commands are typically registered during application initialization and remain active throughout the application's operation. They should not be revoked when the page is closed. Registration is only revoked when the application exits, the related module is uninstalled, or the command is no longer provided. After revocation, no page can call the command using that name anymore.

The registration handle retains the command object. To revoke it, use the following interface:

=== "C++"

    ```cpp
    registration.Reset();
    command.reset();
    ```

    The registration handle is also automatically revoked during its destruction.

=== "C#"

    ```csharp
    registration.Dispose();
    ```

After revocation, the command will no longer be found during subsequent searches. However, the calls that have already started can still be completed. It is possible to re-register commands with the same name after revocation. Stopping or restarting the SDK during operation will not automatically revoke the registration. It is the application that should manage the registration handle.

!!! warning "Global command lifecycle"
    Keep the registration handle active until the command needs to be called on the page. Revoke the registration before uninstalling the module that contains business callbacks, and ensure that all ongoing calls have been completed.
