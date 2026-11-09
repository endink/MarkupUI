---
icon: bootstrap/arrow-left-right
---

# Value Converters

In Unreal Engine, value converters typically turn structures into values that a page can display or edit. For example, a converter can format a first and last name as one string. When a two-way binding submits input, the converter can parse the string and return a structure of the same type for whole-property writeback.

!!! important "Supported Source Types"
    The Unreal Engine plugin's structure converter accepts reflected `USTRUCT` types as sources. Reverse conversion writes back the same `USTRUCT` type. This interface excludes plain C++ structs and `UObject` references as sources. Forward conversion can target `String` or another value type the page accepts.

For non-Unreal types, see [Markup UI C++ Value Converters](../../binding/value-converters.md) for definition and registration.

## Define Converter

### Data Model {#define-the-model}

Create `PlayerProfile.h` in your project's C++ module. Define `FPlayerName` with `USTRUCT` and expose the model's `FullName` with `UPROPERTY(BlueprintReadWrite)` so the binding can replace the whole structure.

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

### Converter Class {#define-and-register}

In `PlayerProfile.cpp`, derive from `TUnrealStructValueConverter<FPlayerName, ValueType::String>`. Implement `ConvertValue` to produce display text and `ConvertBackValue` to build a new `FPlayerName` from the input.

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

This example expects `first name, last name` and returns an empty `TOptional<FPlayerName>` if parsing fails.

## Register

Call `RegisterPlayerNameConverter()` once on the game thread. Check that registration succeeds before opening a page that uses it.

```cpp
bool RegisterPlayerNameConverter()
{
    return MarkupUI::Binding::RegisterUnrealStructValueConverter<FPlayerNameConverter>(
        MARKUPUI_STR_VIEW("FormatPlayerName"));
}
```

## Use It in HTML

Set a `UPlayerProfile` instance as the page's [data context](property-binding.md). Bind both the text and the input to `FullName` and use `converter` to select the registered name.

```html
<p @text="{FullName, converter=FormatPlayerName}"></p>
<label>
    Name
    <input type="text"
           @value="{FullName, converter=FormatPlayerName, mode=twoWay, update=blur}">
</label>
```

The page initially displays `Ada, Lovelace`. Enter `Grace, Hopper` and leave the input. The binding replaces `FullName` with a new structure whose `FirstName` is `Grace` and `LastName` is `Hopper`. See [Value Converters](../../binding/value-converters.md) and [Input and Two-Way Binding](../../binding/input-and-two-way-binding.md) for binding options and submission timing.
