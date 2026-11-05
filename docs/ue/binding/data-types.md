---
icon: bootstrap/boxes
---

# 数据类型

除 [SDK 支持的数据类型](../../binding/data-types.md)外，Markup UI 的 Unreal Engine 插件还映射了 UE 原生类型，扩大了可用于数据绑定的数据类型范围。业务代码可以继续使用 UE 字符串、数学类型和容器，无需逐项手动转换为 SDK 类型。

## 原生类型

插件提供以下 UE 类型到 SDK 标量的映射：

| UE 类型 | SDK 数据类型 | 说明 |
| --- | --- | --- |
| `FString`、`FUtf8String`、`FText`、`FName` | `String` | 字符串、文本和名称以字符串值传递 |
| `FColor` | `Color` | 整数颜色分量 |
| `FLinearColor` | `ColorF` | 浮点颜色分量 |
| `FVector2f`、`FVector2d` | `Vector2` | 二维向量 |
| `FVector3f`、`FVector3d` | `Vector3` | 三维向量 |
| `FQuat4f`、`FQuat4d` | `Matrix4x4` | 四元数旋转以矩阵传递 |
| `FRotator3f`、`FRotator3d` | `Matrix4x4` | 欧拉角旋转以矩阵传递 |
| `FMatrix44f`、`FMatrix44d` | `Matrix4x4` | 四阶矩阵 |
| `FTransform3f`、`FTransform3d` | `Matrix4x4` | 变换以矩阵传递 |

常用名称 `FVector2D`、`FVector`、`FQuat`、`FRotator`、`FMatrix`、`FTransform` 按其实际对应的类型使用映射。旋转和变换类型映射为遵循 CSS 列向量语义的矩阵，可直接绑定到 `style.transform`。Mapper 负责双向坐标轴映射，例如正 Roll 映射为 CSS 正 Z 轴旋转。矩阵组合与绑定示例参见[矩阵](../../binding/data-types.md#matrix)。

!!! warning "FTransform 不支持剪切"
    UE 的 `FTransform` 只能保存**平移、旋转和沿三个局部轴的缩放**，无法完整表示剪切。

    剪切会让原本互相垂直的轴变斜，例如将矩形的上边向右推，使其变成平行四边形。CSS 和 4 × 4 矩阵可以表达这种变换；**非等比缩放与旋转按某些顺序组合，也可能产生剪切**。

    将页面中的矩阵写回 UE 类型时：

    - **`FMatrix`**：可以完整保留包含剪切的矩阵。
    - **`FTransform`**：若矩阵包含剪切，Mapper 会拒绝转换并保留目标原值，避免静默丢失变换。
    - **可分解为平移、旋转和轴向缩放的矩阵**：可以正常写回 `FTransform`。

`bool`、`int8`、`uint8`、`int16`、`uint16`、`int32`、`uint32`、`int64`、`uint64`、`float`、`double` 使用对应的 SDK 布尔或数字类型。

## 枚举、对象与集合

- **枚举**：支持 SDK 已支持的 C++ 枚举形式，并适配 `TEnumAsByte<TEnum>`，后者按其实际存储的单字节整数传递。
- **对象**：数据对象上的 `UObject` 引用和弱对象引用可作为对象读取，通过属性路径继续访问其成员；对象引用当前不支持通过普通属性绑定替换。
- **结构体**：反射属性中的 `USTRUCT` 可以作为对象访问其受支持的成员。它与原生标量映射是不同的访问方式。
- **数组**：`TArray<T>` 映射为 SDK 的数组访问接口。
- **映射**：`TMap<TKey, TValue>` 映射为 SDK 的 Map 访问接口。
- **集合**：`TSet<T>` 映射为 SDK 的 Set 访问接口。
- **共享与弱指针**：SDK C++ 数据模型适配 `TSharedPtr<T, ESPMode::ThreadSafe>` 和 `TWeakPtr<T, ESPMode::ThreadSafe>`；非线程安全模式不在此适配范围内。

容器的元素、键和值仍需满足对应类型支持规则。集合变更需要通知页面，具体用法见[属性绑定](property-binding.md)。共享指针适配用于 SDK C++ 数据模型，不替代 `UObject` 的垃圾回收规则。

## C++ 使用

```cpp
#include "CoreMinimal.h"
// 必须引入 UE 专用 SDK 头文件，提供 UE 类型适配并支持编译期类型检查。
#include "MarkupUISdk.h"
```

使用插件的 C++ SDK 接口时，应先引入 `MarkupUISdk.h`，再使用相关模板，确保 UE 类型适配已声明。

> 原生标量映射用于 SDK C++ 模型和受支持的命令参数。`UObject` 反射属性中的结构体按对象路径访问，不意味着所有结构体属性都会自动作为 SDK 标量处理。属性是否可写及变更通知规则见[属性绑定](property-binding.md)，命令参数规则见[命令绑定](command-binding.md)。
