---
icon: bootstrap/arrow-left-right
---

# 值转换器

值转换器在数据上下文与绑定目标之间转换值。页面读取属性后，`Convert` 将其转换成目标可用的类型。双向绑定提交输入时，`ConvertBack` 先把输入转换成源属性所需的类型，再写回数据上下文。

以下示例将 `Name` 结构格式化为字符串。页面显示 `Ada, Lovelace`。用户提交 `Grace, Hopper` 后，模型收到一个新的 `Name`，其 `FirstName` 为 `"Grace"`，`LastName` 为 `"Hopper"`。

## 定义转换器

=== "C++"

    `Name` 使用 `MARKUPUI_MEMBER` 暴露两个成员，供转换器读取。

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

    `value.GetStructValue(name)` 将同类型的结构复制到 `name`，成功时返回 `true`。类型不匹配或源值不可用时返回 `false`，`name` 保持原值。示例用 `std::string` 拼接文本，`Value::String` 会复制 UTF-8 内容。反向转换通过 `Value::StructValue` 返回拥有独立存储的 `Name`，由绑定一次性写入 `FullName`。

=== "C#"

    C# 可以直接定义普通 `struct`。转换器通过类型匹配读取 `Name`，反向转换成功时返回一个新的 `Name`。

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

    `Convert` 返回 `string`。无法转换时返回 `null`。

!!! note "示例的输入格式"
    输入由两个非空字段组成，中间使用逗号加一个空格 `", "`，字段内不含逗号。例如 `Grace, Hopper` 符合格式，`Grace Hopper` 缺少分隔符。

## 注册转换器

完成 SDK 初始化后，在打开使用该转换器的页面前注册一次，并检查返回值。下面把 `Name` 注册为源类型，把字符串注册为目标类型。注册名 `FormatName` 区分大小写，名称重复时注册返回 `false`。

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

    `RegisterValueConverter` 接收指向 `IValueConverter` 实现的 `SharedPointerLike`，例如 `std::shared_ptr` 或 `MarkupSharedPtr`。注册成功后，SDK 保留共享所有权。

=== "C#"

    ```csharp
    bool registered = DataBindingConfig.RegisterValueConverter<Name, string>(
        new NameConverter(), "FormatName");
    ```

## 在页面中使用

定义一个公开 `FullName` 的数据对象，并将它的实例设为页面的[数据上下文](../concepts/data-context.md)。

=== "C++"

    继承 `ObservableObject`，用 `MARKUPUI_PROPERTY` 公开按值存储的 `FullName`。结构声明和变更通知见[结构](observable-objects.md#observable-struct)。

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

    用公开属性提供 `FullName`，在设置器中保存新结构并发送属性变更通知。

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

两个语言示例使用相同的 HTML。文本绑定调用 `Convert` 显示姓名。文本输入框也使用同一转换器显示当前值，并在失去焦点时调用 `ConvertBack` 提交编辑。

```html
<p @text="{FullName, converter=FormatName}"></p>
<label>
    Name
    <input type="text"
           @value="{FullName, converter=FormatName, mode=twoWay, update=blur}">
</label>
```

`converter` 指定已注册的名称。转换器也可接收一个额外的绑定参数，写法见[绑定语法](binding-syntax.md)。本例未设置参数，两个转换函数的第三个参数收到空值。

!!! note "写回整个结构"
    绑定路径是 `FullName`，其叶属性必须可写并允许整结构替换。返回值的结构类型必须与该属性的类型一致。可用 `FullName.FirstName` 读取单个成员。C# 的按值结构成员通过该路径只读，双向绑定应指向外层 `FullName` 属性。

更新时机和控件行为见[输入与双向绑定](input-and-two-way-binding.md)。
