---
icon: bootstrap/arrow-left-right
---

# 值转换器

Unreal Engine 中的值转换器通常用于将结构转换成界面可显示或编辑的值，例如把包含名和姓的结构格式化为一个字符串。双向绑定提交输入时，转换器可以解析字符串并返回同类型的结构，再由绑定整体写回属性。

!!! important "结构转换器的适用范围"
    Unreal Engine 插件的结构转换器仅接受 UE 反射可识别的 `USTRUCT` 类型作为正向转换的源。反向转换写回相同类型的 `USTRUCT`。普通 C++ 结构体和 `UObject` 引用不属于该接口的源类型。正向转换的目标可以是 `String` 等页面支持的值类型。

非 UE 类型的转换器定义与注册方式见 [Markup UI 的 C++ 值转换器](../../binding/value-converters.md)。

## 定义转换器

### 数据模型

在项目的 C++ 模块中创建 `PlayerProfile.h`。用 `USTRUCT` 定义 `FPlayerName`，再用 `UPROPERTY(BlueprintReadWrite)` 公开模型的 `FullName`，使绑定可以整体写回。

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "PlayerProfile.generated.h"

USTRUCT(BlueprintType)
struct FPlayerName
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Profile")
    FString FirstName = TEXT("Ada");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Profile")
    FString LastName = TEXT("Lovelace");
};

UCLASS()
class UPlayerProfile : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Profile")
    FPlayerName FullName;
};

bool RegisterPlayerNameConverter();
```

### 转换器实现

在 `PlayerProfile.cpp` 中继承 `TUnrealStructValueConverter<FPlayerName, ValueType::String>`。实现 `ConvertValue` 生成显示文本，实现 `ConvertBackValue` 从输入构造一个新的 `FPlayerName`。

```cpp
#include "PlayerProfile.h"
#include "MarkupUISdk.h"
#include "StringUtilities.h"

class FPlayerNameConverter final : public MarkupUI::Binding::TUnrealStructValueConverter<
    FPlayerName, MarkupUI::ValueType::String>
{
    using Value = MarkupUI::Binding::Value;

protected:
    Value ConvertValue(const FPlayerName& Input, const Value&) const override
    {
        const FString Text = Input.FirstName + TEXT(", ") + Input.LastName;
        return MarkupUI::StringUtilities::WithUtf8View(Text, [](MarkupUI::StringView Utf8)
        {
            return Value::String(Utf8);
        });
    }

    TOptional<FPlayerName> ConvertBackValue(const Value& Input, const Value&) const override
    {
        MarkupUI::StringView Utf8;
        if (!Input.GetString(Utf8))
        {
            return {};
        }

        const FString Text = MarkupUI::StringUtilities::ToString(Utf8);
        FPlayerName Name;
        if (!Text.Split(TEXT(", "), &Name.FirstName, &Name.LastName) ||
            Name.FirstName.IsEmpty() || Name.LastName.IsEmpty() ||
            Name.FirstName.Contains(TEXT(",")) || Name.LastName.Contains(TEXT(",")))
        {
            return {};
        }

        return Name;
    }
};
```

示例约定姓名格式为 `名, 姓`，无法解析时返回空的 `TOptional<FPlayerName>`。

## 注册

在游戏线程上调用 `RegisterPlayerNameConverter()` 一次。确认注册成功后，再打开使用该转换器的页面。

```cpp
bool RegisterPlayerNameConverter()
{
    return MarkupUI::Binding::RegisterUnrealStructValueConverter<FPlayerNameConverter>(
        MARKUPUI_STR_VIEW("FormatPlayerName"));
}
```

## 在 HTML 中使用

将 `UPlayerProfile` 实例设为页面的[数据上下文](property-binding.md)。将文本和输入框都绑定到 `FullName`，并通过 `converter` 指定注册名。

```html
<p @text="{FullName, converter=FormatPlayerName}"></p>
<label>
    Name
    <input type="text"
           @value="{FullName, converter=FormatPlayerName, mode=twoWay, update=blur}">
</label>
```

页面最初显示 `Ada, Lovelace`。输入 `Grace, Hopper` 并离开输入框后，绑定把 `FirstName` 为 `Grace`、`LastName` 为 `Hopper` 的新结构整体写回 `FullName`。有关绑定选项和提交时机，见[值转换器](../../binding/value-converters.md)与[输入与双向绑定](../../binding/input-and-two-way-binding.md)。
