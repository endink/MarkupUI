---
icon: bootstrap/puzzle
---

# Extension Properties

The UE plugin comes with a set of [Extension Properties](../../binding/extension-properties.md). Information such as object names, Actor positions, and component transformations is provided to the page as ordinary binding properties. These properties are automatically registered when the plugin is activated, eliminating the need for repeated declarations in the business class.

!!! abstract "Call thread"
    All extension properties are accessed via Get/Set functions, which are executed on the **game thread**.

!!! note "A blueprint node does not equal a bindable property."
    The fact that a node can be seen in the blueprint does not mean that there exists a `UPROPERTY` with the same name or an `UFUNCTION` that follows the property access convention on the object. For example, the reflection function corresponding to **Get Actor Location** is actually named `K2_GetActorLocation`. The C++ `GetActorLocation()` function is not marked as `UFUNCTION`, and there is no `UPROPERTY` named `ActorLocation` on the object. Therefore, property binding cannot be done directly based on the blueprint node name. The plugin uses built-in extension properties to supplement `ActorLocation`, allowing the page to read the position using this name.

## Built-in properties

The following properties are read-only and apply to the corresponding types and their derived classes:

| Object type | Property name | UE value type | Accessibility | Description |
| --- | --- | --- | --- | --- |
| `UObject` | `DisplayName` | `FString` | Read-only | Object display name, obtained using UE's `GetDisplayName` function |
| `UObject` | `ObjectName` | `FString` | Read-only | Object Name |
| `UObject` | `ObjectPathString` | `FString` | Read-only | The complete path string of the object |
| `AActor` | `ActorLocation` | `FVector` | Read-only | The world space position of the Actor |
| `AActor` | `ActorRotation` | `FRotator` | Read-only | The world space rotation of the Actor |
| `USceneComponent` | `WorldLocation` | `FVector` | Read-only | The world space position of the component |
| `USceneComponent` | `WorldRotation` | `FRotator` | Read-only | The world space rotation of the component |
| `USceneComponent` | `WorldTransform` | `FTransform` | Read-only | The world space transformation of the component |

> Ordinary properties take precedence over extension properties with the same name. Derived classes do not need to re-register the extension properties of the base class.

!!! warning "Updating an extension property requires sending a notification."
    After the value of an extension property changes, it is necessary to call the property notification so that the interface can read and update the display again. For specific usage, see [Property Change Notification](property-binding.md#property-change-notification).

## Bind to ActorLocation

After setting an Actor instance as the data context of a page, you can directly bind to `ActorLocation` without defining additional location properties.

```html
<!doctype html>
<html>
<body>
    <!-- The current data context must be an instance of AActor or a subclass. -->
    <h2>{{ ObjectName }}</h2>
    <p>世界位置：{{ ActorLocation }}</p>
    <p>X：{{ ActorLocation.X }}</p>
    <p>Y：{{ ActorLocation.Y }}</p>
    <p>Z：{{ ActorLocation.Z }}</p>
</body>
</html>
```

For example, when the Actor is located at `(100, 200, 300)`, the three components will be displayed as `100`, `200`, and `300` respectively. If the data context references the Actor through the `TargetActor` property, you can also use paths such as `TargetActor.ActorLocation.X`.

## Location Change Notification

Extension properties obtain the current value when read, and do not automatically monitor the Actor's movement. When the page needs to be refreshed as the position changes, send a property notification after the position is updated.

```cpp
#include "CoreMinimal.h"
// Include the Unreal Engine SDK header for Unreal type adapters and compile-time type checking.
#include "MarkupUISdk.h"

// TargetActor is the Actor instance bound to the page.
MarkupUI::Binding::NotifyPropertyChanged(TargetActor, TEXT("ActorLocation"));
```

The notification method is the same as that of regular properties. For more details, see [Property Binding](property-binding.md). `ActorLocation` is a read-only extension property, and the Actor cannot be moved through two-way binding. The movement operation is performed by the business code.
## Customizing UObject extension properties

C++ can be used to register custom extension properties for `UObject` and its derived classes. There is no need to add `UPROPERTY` to the original class. After registration, the property can be read just like a regular property, and derived classes can also use it.

For example, adding the `ActorSpeed` property to `AActor` to read the length of the current speed vector. The example also provides an empty setter, which is only used to demonstrate how to register writable properties.

```cpp
#include "CoreMinimal.h"
// Include the Unreal Engine SDK header for Unreal type adapters and compile-time type checking.
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
        // This example illustrates a writable extension property. The Actor stays as it is.
    }

public:
    // Register on the game thread before opening pages that use the property.
    static bool Register()
    {
        return MarkupUI::Binding::RegisterExtensionProperty(
            TEXT("ActorSpeed"), &GetActorSpeed);

        // Pass a setter function to support writes.
        // return MarkupUI::Binding::RegisterExtensionProperty(
        //     TEXT("ActorSpeed"), &GetActorSpeed, &SetActorSpeed);
    }
};
```

Call `#!cpp FActorBindingExtensions::Register()` once during the application or module initialization process. Check whether the return value is `true`. The registration interface determines the object type and property value type based on the accessor. Repeating registration of the same name for the same type will fail.

- The getter must be an accessor that can be converted into a function pointer, which receives `const TObject&` and returns the property value.
- If support for writing is required, the third parameter setter can be passed. Its signature is: `void(TObject&, const TValue&)` When the setter is not provided, it acts as a read-only function.
- The accessor does not need to be declared as `UFUNCTION`. The value type should comply with the [Data Types](data-types.md) supported by the plugin.

After using the Actor instance as the data context, the page can be directly bound to it.

```html
<!-- The current data context is an instance of AActor or a subclass. -->
<p>速度：{{ ActorSpeed }}</p>
```

After the speed changes, the business code sends a notification for the extension property, and the page will be read again.

```cpp
MarkupUI::Binding::NotifyPropertyChanged(TargetActor, TEXT("ActorSpeed"));
```

The SDK does not automatically infer the data dependencies of the getter, and the setter does not automatically send notifications. The extension property needs to notify the corresponding property changes after the data is successfully modified. The extension property registration does not retain the `UObject` instance, and its lifecycle is still managed by the business code according to UE rules.
