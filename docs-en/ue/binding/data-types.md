---
icon: bootstrap/boxes
---

# Data Types

In addition to the data types supported by [SDK](../../binding/data-types.md), the Markup UI plugin for Unreal Engine also maps UE native types, expanding the range of data types that can be used for data binding. Business code can continue to use UE strings, mathematical types, and containers, without the need to manually convert them to SDK types for each individual case.

## Native types

The plugin provides the following mappings from UE types to SDK scalars:

| UE types | SDK data types | Description |
| --- | --- | --- |
| `FString`, `FUtf8String`, `FText`, `FName` | `String` | Strings, texts, and names are passed as string values. |
| `FColor` | `Color` | Integer color components. |
| `FLinearColor` | `ColorF` | Floating-point color components. |
| `FVector2f`, `FVector2d` | `Vector2` | Two-dimensional vectors. |
| `FVector3f`, `FVector3d` | `Vector3` | Three-dimensional vectors. |
| `FQuat4f`, `FQuat4d` | `Matrix4x4` | Quaternion rotations are passed as matrices. |
| `FRotator3f`, `FRotator3d` | `Matrix4x4` | Euler angles are passed as matrices. |
| `FMatrix44f`, `FMatrix44d` | `Matrix4x4` | Fourth-order matrices |
| `FTransform3f`, `FTransform3d` | `Matrix4x4` | Transformations are carried out using matrices |

Common names like `FVector2D`, `FVector`, `FQuat`, `FRotator`, `FMatrix`, `FTransform` should be used according to their actual types. Rotations and transformation types are mapped to matrices that follow the CSS column vector semantics, and can be directly bound to `style.transform`. The Mapper is responsible for the bidirectional coordinate axis mapping. For example, a positive Roll is mapped to a positive Z-axis rotation in CSS. For examples of matrix combinations and bindings, see [Matrices](../../binding/data-types.md#matrix).

!!! warning "FTransform does not support cutting"
    UE's `FTransform` can only store **translation, rotation, and scaling along three local axes**, and cannot fully represent shear transformations.

    Shearing can make the axes that are originally perpendicular become oblique. For example, pushing the upper edge of a rectangle to the right turns it into a parallelogram. CSS and 4 × 4 matrices can represent such transformations. **Non-equational scaling and rotations combined in certain orders can also result in shearing.**

    When writing the matrices from the page back to the UE type:

    - **`FMatrix`**: It is possible to fully retain the matrix that contains the cuts.
    - **`FTransform`**: If the matrix contains shearing, Mapper will refuse the conversion and retain the original values of the target, to prevent the transformation from being silently lost.
    - **A matrix that can be decomposed into translation, rotation, and axial scaling**: Can be written back to `FTransform` normally.

`bool`, `int8`, `uint8`, `int16`, `uint16`, `int32`, `uint32`, `int64`, `uint64`, `float`, `double` Use the corresponding SDK boolean or numerical types.

## Enumeration, Objects, and Collections

- **Enumeration**: Supports the C++ enumeration formats already supported by the SDK, and adapts to `TEnumAsByte<TEnum>`. The latter passes values in their actual single-byte integer form.
- **Object**: On the data object, `UObject` references and weak object references can be used to access the object. Its members can be accessed through the property path. Currently, object references do not support being replaced by ordinary property bindings.
- **Structures**: The `USTRUCT` in reflective properties allows access to its supported members as an object. This is a different way of accessing compared to native scalar mappings.
- **Arrays**: `TArray<T>` Array access interface mapped to the SDK.
- **Mapping**: `TMap<TKey, TValue>` Map access interface mapped to the SDK.
- **Collection**: `TSet<T>` The Set access interface mapped to the SDK.
- **Sharing and weak pointers**: Adaptation of SDK C++ data model `TSharedPtr<T, ESPMode::ThreadSafe>` And `TWeakPtr<T, ESPMode::ThreadSafe>`; The non-thread-safe mode is not within the scope of this adaptation.

The elements, keys, and values of containers still need to meet the corresponding type support rules. Changes to the collection need to be notified to the page. For specific usage, see [Property Binding](property-binding.md). Shared pointers are used for adapting the SDK C++ data model. They do not replace the garbage collection rules of `UObject`.

## C++ usage

```cpp
#include "CoreMinimal.h"
// Include the Unreal Engine SDK header for Unreal type adapters and compile-time type checking.
#include "MarkupUISdk.h"
```

When using the C++ SDK interface of the plugin, you should first include `MarkupUISdk.h`, and then use the relevant templates to ensure that the UE type adaptation is properly declared.

> Native scalar mapping is used for the SDK C++ models and supported command parameters. The structures in the `UObject` reflection properties are accessed based on the object path. This does not mean that all structure properties will automatically be processed as SDK scalars. Information about whether a property is writable and the rules for change notifications can be found in [Property Binding](property-binding.md). Information about command parameter rules can be found in [Command Binding](command-binding.md).
