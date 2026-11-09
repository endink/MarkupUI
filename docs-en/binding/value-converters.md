---
icon: bootstrap/arrow-left-right
---

# Value Converters

Value converters transform values between the data context and the binding target. After the binding reads a property, `Convert` returns a value the target can use. When a two-way binding submits input, `ConvertBack` converts it to the source property's type before writeback.

The examples format a `Name` structure as a string. The page displays `Ada, Lovelace`. If the user submits `Grace, Hopper`, the model receives a new `Name` with `FirstName` set to `"Grace"` and `LastName` set to `"Hopper"`.

## Define a Converter

=== "C++"

    `Name` uses `MARKUPUI_MEMBER` to expose both members to the converter.

    ```cpp
    #include <markupui/binding/data_binding.h>
    #include <markupui/binding/modeling/object_model.h>
    #include <markupui/binding/modeling/struct_value.h>
    #include <cstdint>
    #include <limits>
    #include <memory>
    #include <string>
    #include <string_view>
    #include <utility>

    struct Name
    {
        std::string FirstName = "Ada";
        std::string LastName = "Lovelace";

        MARKUPUI_SUPPORT_BEGIN(Name)
            MARKUPUI_MEMBER(FirstName)
            MARKUPUI_MEMBER(LastName)
        MARKUPUI_SUPPORT_END()
    };

    class NameConverter final : public MarkupUI::Binding::IValueConverter
    {
        using Value = MarkupUI::Binding::Value;
        using TypeInfo = MarkupUI::Binding::Metadata::TypeInfo;

    public:
        Value Convert(const Value& value, const TypeInfo&, const Value&) override
        {
            Name name;
            if (!value.GetStructValue(name))
            {
                return Value::Null();
            }

            const std::string text = name.FirstName + ", " + name.LastName;
            if (text.size() > (std::numeric_limits<std::uint32_t>::max)())
            {
                return Value::Null();
            }
            return Value::String({text.data(), static_cast<std::uint32_t>(text.size())});
        }

        Value ConvertBack(const Value& value, const TypeInfo& targetType, const Value&) override
        {
            Name replacement;
            MarkupUI::StringView input{};
            if (!value.GetString(input) || input.Size == 0 ||
                !(targetType == MarkupUI::Binding::Modeling::GetStructTypeInfo(replacement)))
            {
                return Value::Null();
            }

            const std::string_view text(input.Data, input.Size);
            const auto comma = text.find(", ");
            if (comma == std::string_view::npos || comma == 0 || comma + 2 == text.size() ||
                text.find(',') != comma || text.find(',', comma + 1) != std::string_view::npos)
            {
                return Value::Null();
            }

            replacement.FirstName = text.substr(0, comma);
            replacement.LastName = text.substr(comma + 2);
            return Value::StructValue(std::move(replacement));
        }
    };
    ```

    `value.GetStructValue(name)` copies a structure of the matching type into `name` and returns `true`. If the type differs or the source is unavailable, it returns `false` and leaves `name` as it was. The example joins the names with `std::string`, then `Value::String` copies the UTF-8 text. `Value::StructValue` returns an owned `Name` for the binding to write to `FullName` as a whole.

=== "C#"

    Define `Name` as a regular C# `struct`. The converter uses a type check to read `Name` and returns a new `Name` when reverse conversion succeeds.

    ```csharp
    using System;
    using MarkupUI.Sdk.Binding;

    public struct Name
    {
        public string FirstName;
        public string LastName;
    }

    public sealed class NameConverter : IValueConverter
    {
        public object? Convert(object? value, Type targetType, object? parameter)
        {
            if (value is Name name)
            {
                return name.FirstName + ", " + name.LastName;
            }

            return null;
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter)
        {
            if (!(value is string text) || targetType != typeof(Name))
            {
                return null;
            }

            int comma = text.IndexOf(", ", StringComparison.Ordinal);
            if (comma <= 0 || comma + 2 == text.Length ||
                text.IndexOf(',') != comma || text.IndexOf(',', comma + 1) >= 0)
            {
                return null;
            }

            Name name = default;
            name.FirstName = text.Substring(0, comma);
            name.LastName = text.Substring(comma + 2);
            return name;
        }
    }
    ```

    `Convert` returns a `string`. Return `null` if conversion fails.

!!! note "Input Format"
    Enter two nonempty fields separated by a comma and a space `", "`. The fields themselves must be free of commas. `Grace, Hopper` follows this format. `Grace Hopper` lacks the separator.

## Register the Converter

Register the converter once after initializing the SDK and before opening a page that uses it. Check the result. Register `Name` as the source type and string as the target type. The name `FormatName` is case-sensitive. Duplicate registration returns `false`.

=== "C++"

    ```cpp
    bool RegisterNameConverter()
    {
        Name sample;
        return MarkupUI::Binding::RegisterValueConverter(
            MarkupUI::Binding::Modeling::GetStructTypeInfo(sample),
            MarkupUI::Binding::Metadata::TypeInfo::Create(MarkupUI::ValueType::String),
            std::make_shared<NameConverter>(),
            MARKUPUI_STR_VIEW("FormatName"));
    }
    ```

    `RegisterValueConverter` accepts a `SharedPointerLike` pointer to an `IValueConverter`, such as `std::shared_ptr` or `MarkupSharedPtr`. After successful registration, the SDK shares ownership of the converter.

=== "C#"

    ```csharp
    bool registered = DataBindingConfig.RegisterValueConverter<Name, string>(
        new NameConverter(), "FormatName");
    ```

## Use It in HTML

Define a model that exposes `FullName` and set an instance as the page's [data context](../concepts/data-context.md).

=== "C++"

    Derive from `ObservableObject` and use `MARKUPUI_PROPERTY` to expose `FullName` as a value property. See [Structures](observable-objects.md#observable-struct) for structure declarations and change notifications.

    ```cpp
    class ProfileObject : public MarkupUI::Binding::Modeling::ObservableObject
    {
    public:
        ProfileObject()
        {
            InitializeType<ProfileObject>();
        }

        MARKUPUI_PROPERTY(ProfileObject, Name, FullName)
    };
    ```

=== "C#"

    Expose `FullName` as a public property. The setter stores the new structure and raises a property change notification.

    ```csharp
    using System.ComponentModel;

    public sealed class ProfileObject : INotifyPropertyChanged
    {
        private Name _fullName;

        public event PropertyChangedEventHandler? PropertyChanged;

        public ProfileObject()
        {
            _fullName.FirstName = "Ada";
            _fullName.LastName = "Lovelace";
        }

        public Name FullName
        {
            get => _fullName;
            set
            {
                _fullName = value;
                PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(FullName)));
            }
        }
    }
    ```

Both examples use the same HTML. The text binding calls `Convert` to display the name. The input uses the same converter to display the current value and calls `ConvertBack` when it loses focus and submits an edit.

```html
<p @text="{FullName, converter=FormatName}"></p>
<label>
    Name
    <input type="text"
           @value="{FullName, converter=FormatName, mode=twoWay, update=blur}">
</label>
```

`converter` selects a registered name. See [Binding Syntax](binding-syntax.md#value-converters) for optional converter parameters. This example omits the parameter, so both conversion methods receive a null third argument.

!!! note "Whole-Structure Writeback"
    The binding path is `FullName`. The leaf property must be writable and support whole-structure replacement. The returned structure must match the property's type. Use `FullName.FirstName` to read an individual member. C# structure member paths are read-only, so point two-way bindings at the outer `FullName` property.

See [Input and Two-Way Binding](input-and-two-way-binding.md) for update timing and control behavior.
