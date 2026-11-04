---
icon: bootstrap/puzzle
---

# 扩展属性

UE 插件内置了一组[扩展属性](../../binding/extension-properties.md)，将对象名称、Actor 位置和组件变换等信息作为普通绑定属性提供给页面。插件启动时自动注册，无需在业务类中重复声明。

!!! abstract "调用线程"
    所有扩展属性背后的 Get/Set 函数都会在**游戏线程**调用。

!!! note "蓝图节点不等于可绑定属性"
    蓝图中能看到某个节点，不代表对象上存在同名的 `UPROPERTY` 或符合属性访问约定的 `UFUNCTION`。例如，**Get Actor Location** 对应的反射函数实际名为 `K2_GetActorLocation`，而 C++ 的 `GetActorLocation()` 不是 `UFUNCTION`，对象上也没有名为 `ActorLocation` 的 `UPROPERTY`。因此，仅凭蓝图节点名称无法直接进行属性绑定；插件通过内置扩展属性补充了 `ActorLocation`，页面才能以该名称读取位置。

## 内置属性

以下属性均为只读，适用于对应类型及其派生类：

| 对象类型 | 属性名称 | UE 值类型 | 可访问性 | 说明 |
| --- | --- | --- | --- | --- |
| `UObject` | `DisplayName` | `FString` | 只读 | 对象显示名称，使用 UE 的 `GetDisplayName` 结果 |
| `UObject` | `ObjectName` | `FString` | 只读 | 对象名称 |
| `UObject` | `ObjectPathString` | `FString` | 只读 | 对象的完整路径字符串 |
| `AActor` | `ActorLocation` | `FVector` | 只读 | Actor 的世界空间位置 |
| `AActor` | `ActorRotation` | `FRotator` | 只读 | Actor 的世界空间旋转 |
| `USceneComponent` | `WorldLocation` | `FVector` | 只读 | 组件的世界空间位置 |
| `USceneComponent` | `WorldRotation` | `FRotator` | 只读 | 组件的世界空间旋转 |
| `USceneComponent` | `WorldTransform` | `FTransform` | 只读 | 组件的世界空间变换 |

> 普通属性优先于同名扩展属性。派生类无需再次注册基类的扩展属性。

!!! warning "更新扩展属性需要发送通知"
    扩展属性的值变化后，必须调用属性通知，界面才会重新读取并更新显示。具体用法见[属性更改通知](property-binding.md#property-change-notification)。

## 绑定 ActorLocation

将一个 Actor 实例设置为页面的数据上下文后，可以直接绑定 `ActorLocation`，无需额外定义位置属性：

```html
<!doctype html>
<html>
<body>
    <!-- 当前数据上下文需要是 AActor 或其派生类的实例。 -->
    <h2>{{ ObjectName }}</h2>
    <p>世界位置：{{ ActorLocation }}</p>
    <p>X：{{ ActorLocation.X }}</p>
    <p>Y：{{ ActorLocation.Y }}</p>
    <p>Z：{{ ActorLocation.Z }}</p>
</body>
</html>
```

例如，Actor 位于 `(100, 200, 300)` 时，三个分量分别显示 `100`、`200`、`300`。若数据上下文通过 `TargetActor` 属性引用 Actor，也可以使用 `TargetActor.ActorLocation.X` 等路径。

## 位置变化通知

扩展属性在读取时获取当前值，不会自动监听 Actor 移动。需要页面随位置变化刷新时，在位置更新后发送属性通知：

```cpp
#include "CoreMinimal.h"
// 必须引入 UE 专用 SDK 头文件，提供 UE 类型适配并支持编译期类型检查。
#include "MarkupUISdk.h"

// TargetActor 是页面绑定的 Actor 实例。
MarkupUI::Binding::NotifyPropertyChanged(TargetActor, TEXT("ActorLocation"));
```

通知方式与普通属性相同，详见[属性绑定](property-binding.md)。`ActorLocation` 是只读扩展属性，不能通过双向绑定移动 Actor；移动操作由业务代码执行。
## 自定义 UObject 扩展属性

可以用 C++ 为 `UObject` 及其派生类注册自定义扩展属性，无需在原有类中添加 `UPROPERTY`。注册后，页面像访问普通属性一样读取它，派生类也可使用。

例如，为 `AActor` 增加 `ActorSpeed` 属性，读取当前速度向量的长度。示例同时提供一个空 setter，仅用于展示可写属性的注册方式：

```cpp
#include "CoreMinimal.h"
// 必须引入 UE 专用 SDK 头文件，提供 UE 类型适配并支持编译期类型检查。
#include "MarkupUISdk.h"
#include "Extension/ExtensionProperty.h"
#include "GameFramework/Actor.h"

class FActorBindingExtensions final
{
private:
    static double GetActorSpeed(const AActor& Actor)
    {
        return Actor.GetVelocity().Size();
    }

    static void SetActorSpeed(AActor& Actor, const double& Value)
    {
        // 仅作为可写扩展属性的例子；实际写入该属性没有意义，此处不修改 Actor。
    }

public:
    // 在游戏线程调用，并在打开使用该属性的页面之前完成注册。
    static bool Register()
    {
        return MarkupUI::Binding::RegisterExtensionProperty(
            TEXT("ActorSpeed"), &GetActorSpeed);

        // 如需支持写入，传入 Setter 函数：
        // return MarkupUI::Binding::RegisterExtensionProperty(
        //     TEXT("ActorSpeed"), &GetActorSpeed, &SetActorSpeed);
    }
};
```

在应用或模块初始化流程中调用 `#!cpp FActorBindingExtensions::Register()` 一次，检查返回值是否为 `true`。注册接口根据访问器推导对象类型和属性值类型；同一类型重复注册相同名称会失败。

- getter 必须是可转换为函数指针的访问器，接收 `const TObject&` 并返回属性值。
- 如需支持写入，可传入第三个参数 setter，其签名为 `void(TObject&, const TValue&)`；不提供 setter 时只读。
- 访问器无需声明为 `UFUNCTION`，值类型应符合插件支持的[数据类型](data-types.md)。

将 Actor 实例作为数据上下文后，页面可以直接绑定：

```html
<!-- 当前数据上下文是 AActor 或其派生类的实例。 -->
<p>速度：{{ ActorSpeed }}</p>
```

速度变化后，业务代码发送扩展属性通知，页面才会重新读取：

```cpp
MarkupUI::Binding::NotifyPropertyChanged(TargetActor, TEXT("ActorSpeed"));
```

SDK 不自动推断 getter 的数据依赖，setter 也不会自动发送通知；可写扩展属性需要在成功修改数据后通知对应属性变化。扩展属性注册不会保留 `UObject` 实例，其生命周期仍由业务代码按 UE 规则管理。
