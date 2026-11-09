---
icon: bootstrap/braces
---

# Data Types

Observable objects provide data to the page through properties. Each property has a specific type, which determines which expression operations it can participate in, whether it can be used as a key in a collection, and how it can be used for text or other binding targets.

This chapter introduces the data types supported by the SDK. Native types of platforms such as Unreal Engine and Unity are supported by corresponding platform plugins. For specific type mappings and usage restrictions, please refer to the documentation for each platform.

!!! note "Type support vs. target support"
    The fact that data can be used in binding expressions does not mean that any HTML property or CSS style can receive it. The matrix can be directly bound to `style.transform`. Other binding results must also meet the requirements of the target property or style.

## A list of types

| Classification | Type |
| --- | --- |
| Boolean Value | `Bool` |
| Integer | `Int8`, `UInt8`, `Int16`, `UInt16`, `Int32`, `UInt32`, `Int64`, `UInt64` |
| Floating Point Number | `Float`, `Double` |
| Text | `String` |
| Color | `Color`, `ColorF` |
| Vector | `Vector2`, `Vector3` |
| Matrix | `Matrix4x4` |
| Object | `Object` |
| Collection | `Array`, `Map`, `Set` |
| Key-Value Pairs | `KeyValue` |
| Null Values | `Null` |

Objects and collections are provided to the binding through references. Strong references maintain the lifecycle of the target object. Weak references do not extend the lifecycle of the target object. The binding can access the properties of the target object when it is still valid.

=== "C++"

    Use `std::shared_ptr<T>` Represents strong reference, use `std::weak_ptr<T>` Represents weak reference.`T` For observable objects or corresponding collection types. Objects are typically represented as follows: `std::make_shared<T>()` Represents applying B first, then A. Scaling first, followed by rotation, and finally translation is written as

=== "C#"

    Using references to object instances, it is also possible to hold objects through properties of the `object` type; `System.WeakReference<T>` represents weak references. `object` is the language type that carries object references, and the actual object must still meet the requirements of the SDK for observable objects or collections.

    C# GC can recycle circularly referenced objects that are no longer reachable. There is no need to use weak references to break circular references. Weak references are suitable for scenarios where it is not desired to extend the lifecycle of the target object through properties.

Strong references and weak references are different ways of referencing the same target. They do not change the classification of `Object`, `Array`, `Map`, or `Set` corresponding to the target. After the weak reference target is recycled, the binding cannot read the target through that reference anymore. The failure of the weak reference itself does not send notifications of property changes.

## Boolean Value

`Bool` represents `true` or `false`, and is suitable for states, condition judgments, and checkboxes.

| C++ | C# | Expression literals |
| --- | --- | --- |
| `#!cpp bool` | `#!csharp bool` | `true`, `false` |

Boolean values support logical operations, equality comparisons, and string concatenation, but do not implicitly convert to numbers. `true + 1` cannot perform numerical addition, and `true == 1` results in `false`.

```html
<p>{{ 'Ready: ' + IsReady }}</p>
<p @if="{IsReady}">Ready</p>
```

When using boolean values for text, lowercase `true` or `false` is used for output.

## Integer

The SDK supports four bit widths for signed and unsigned integers:

| SDK type | Range | C++ | C# |
| --- | --- | --- | --- |
| `Int8` | −128 ～ 127 | `#!cpp int8_t` | `#!csharp sbyte` |
| `UInt8` | 0 ～ 255 | `#!cpp uint8_t` | `#!csharp byte` |
| `Int16` | −32,768 ～ 32,767 | `#!cpp int16_t` | `#!csharp short` |
| `UInt16` | 0 ～ 65,535 | `#!cpp uint16_t` | `#!csharp ushort` |
| `Int32` | −2³¹ ～ 2³¹−1 | `#!cpp int32_t` | `#!csharp int` |
| `UInt32` | 0 ～ 2³²−1 | `#!cpp uint32_t` | `#!csharp uint` |
| `Int64` | −2⁶³ ～ 2⁶³−1 | `#!cpp int64_t` | `#!csharp long` |
| `UInt64` | 0 ～ 2⁶⁴−1 | `#!cpp uint64_t` | `#!csharp ulong` |

Integers can be used for counting, indexing, identification, and numerical calculations. Array subscripts start at `0`; Maps support all eight types of integers as keys.

### Operation results

Addition, subtraction, multiplication, modulo operations, and the unary negative sign for integers are handled using precise integer arithmetic. The results are stored as `Int64` or `UInt64`, without preserving the narrower input types:

- Negative results are stored as `Int64`.
- When the revert result does not exceed the maximum value of `Int64`, use `Int64`. When the result is larger, use `UInt64`.
- Results that exceed the range of −2⁶³ to 2⁶⁴−1 are returned as `Null`. There is no rounding, no truncation, and no automatic conversion to floating-point numbers.

Integer division results in `Double`. For example, `5 / 2` yields `2.5`. The sign of the remainder follows the dividend. For example, `-9 % 4` results in `-1`.

## Floating Point Number

| SDK type | Precision | C++ | C# |
| --- | --- | --- | --- |
| `Float` | 32-bit single-precision | `#!cpp float` | `#!csharp float` |
| `Double` | 64-bit double-precision | `#!cpp double` | `#!csharp double` |

Floating-point numbers are suitable for values that change in proportion, transparency, and continuity. Decimals and scientific notation literals in expressions are represented as `Double`, such as `0.5`, `1e3`.

Ordinary numerical arithmetic involving `Float` or `Double` is calculated using `Double`, and the result is also `Double`. When dealing with zero, modulus operations, arithmetic involving non-finite values, or situations that produce non-finite results, `Null` is returned.

!!! warning "The precision of converting large integers to floating-point numbers"
    Not all integers with an absolute value exceeding 2⁵³ can be accurately represented by `Double`. When large integers are involved in floating-point calculations or when structure values are scaled, precision may be lost. Data that requires precise storage, such as identifiers, should avoid such conversions.

## Strings

`String` is used to store text.

| SDK type | C++ | C# | Expression literals |
| --- | --- | --- | --- |
| `String` | `#!cpp std::string`, `#!cpp std::string_view`, `#!cpp MarkupUI::String`, `#!cpp MarkupUI::StringView` | `#!csharp string` | Use single quotes, for example, `'Player'` |

String literals in expressions should be enclosed in single quotes:

```html
<p>{{ 'Player: ' + Name }}</p>
<p>{{ Health + ' HP' }}</p>
```

When `+` is on either side of a string, text concatenation is performed. Numerical texts are not automatically converted to numbers: `'1' + 2` results in the string `12`, while `'6' / 2` returns `Null`.

Strings support equality comparisons. Size comparisons are done according to the UTF-8 byte order, not the local language sorting order. HTML tags within strings are displayed as text and are not automatically converted into interface structures due to data binding.

## Color

| SDK type | C++ | C# |
| --- | --- | --- |
| `Color` | `#!cpp MarkupUI::Color` | `#!csharp MarkupUI.Sdk.Core.Color` |
| `ColorF` | `#!cpp MarkupUI::ColorF` | `#!csharp MarkupUI.Sdk.Core.ColorF` |

- `Color` contains four `UInt8` components: `R`, `G`, `B`, and `A`. Each component ranges from 0 to 255.
- `ColorF` contains four `Float` components: `R`, `G`, `B`, and `A`. For normal normalized colors, a range of 0 to 1 is used.

`A` represents the transparency component. The two color types are not automatically normalized to 255 regardless of their similar names. Components should be provided according to the corresponding types when used.

Colors support equality and inequality comparisons of the same type. Arithmetic operations, size comparisons, or direct text concatenation are not supported. When color text needs to be provided in CSS, the application or converter should specify the format acceptable by the target system.

## Vector

| SDK type | C++ | C# |
| --- | --- | --- |
| `Vector2` | `#!cpp MarkupUI::Vector2` | `#!csharp System.Numerics.Vector2` |
| `Vector3` | `#!cpp MarkupUI::Vector3` | `#!csharp System.Numerics.Vector3` |

- `Vector2` contains `X` and `Y` components, while `Vector3` contains `X`, `Y`, and `Z` components.
- In the SDK, vector components are stored as `Double`. In `System.Numerics`, vector components are stored as `float`. When entering the SDK, these values are converted to `Double`, and when writing back, they are converted back to `float`. This may lead to rounding errors.

Vectors are provided as properties of observable objects in expressions. Expressions do not provide constructors like `Vector3(...)` or vector literals.

### Supported operations

| Operations | Behaviors |
| --- | --- |
| Addition and subtraction of vectors of the same dimension `+`, `-` | Addition and subtraction of corresponding components |
| Same-dimensional vectors `*`, `/` | Corresponding components are multiplied and divided. All divisors must be non-zero |
| Vector `*` numbers, numbers `*` vectors | Each component is multiplied by the number |
| Vector `/` numbers | Each component is divided by a non-zero number |
| Unit `-` | Take the negative of each component |

Retain the vector dimension of the result. Vector multiplication is performed component by component, not dot product or cross product.

```html
<!-- Velocity is a Vector3 and Speed is a number. -->
<p>{{ Velocity * Speed }}</p>
```

If `Velocity` is `(1, 2, 3)` and `Speed` is `2`, the text output will be `Vector3(2, 4, 6)`. This text is used to display values and is not an input format that can be reversely parsed.

Mixed operations between Vector2 and Vector3, addition and subtraction of vectors and numbers, division of numbers by vectors, modulus of vectors, and mixed operations between vectors and matrices are not supported. The SDK does not automatically add dimensions, normalize, convert units, or transform the coordinate system.

## Matrix {#matrix}

The matrices in the SDK are used to provide interface transformations for HTML/CSS. They **uniformly follow the CSS column vector semantics**[^css-matrix-semantics]. `Matrix4x4` is a 4x4 matrix that can represent translations, scaling, rotations, and combinations of these. The sixteen components of the SDK's built-in type are all of type `Double`. Matrices are created in the application code and then provided to the page through the properties of observable objects.

| SDK type | C++ | C# |
| --- | --- | --- |
| `Matrix4x4` | `#!cpp MarkupUI::Matrix4x4` | `#!csharp MarkupUI.Sdk.Core.Matrix4x4`, `#!csharp System.Numerics.Matrix4x4` |

### CSS transformation conventions

- The formula for transforming using column vectors, points, or directions is `p' = M * p`.
- In `Mij`, `i` represents the row, and `j` represents the column. Fields are arranged in rows according to the SDK's sixteen-parameter constructor.
- The translation components are located in `M14`, `M24`, `M34`, corresponding to the X, Y, and Z axes of CSS.
- `A * B` It indicates that B is applied first, followed by A. The sequence is: scale first, then rotate, and finally translate. `Translation * Rotation * Scaling`.
- In CSS, the X-axis of screen coordinates is directed to the right, and the Y-axis is directed downward. The rotation around the Z-axis is clockwise when displayed on the screen.

```text
M11  M12  M13  M14
M21  M22  M23  M24
M31  M32  M33  M34
M41  M42  M43  M44
```

Fields arranged in rows and those arranged using column vectors are two different concepts. When outputting the CSS `matrix3d(...)` function, the SDK will arrange the parameters in the order required by CSS, without the need for manual adjustment.

### Identity matrices and translations

The identity matrix does not change the input points, and its four diagonal components are `1`, other components are `0` Used in C++ `#!cpp MarkupUI::Matrix4x4::Identity()`, used in C# `#!csharp MarkupUI.Sdk.Core.Matrix4x4.Identity`.

For example, translating by `10`, `20`, and `30` along the X, Y, and Z axes of CSS respectively:

=== "C++"

    ```cpp
    #include <markupui/core/matrix4x4.h>

    MarkupUI::Matrix4x4 translation = MarkupUI::Matrix4x4::Identity();
    translation.M14 = 10;
    translation.M24 = 20;
    translation.M34 = 30;
    ```

=== "C#"

    ```csharp
    var translation = new MarkupUI.Sdk.Core.Matrix4x4(
        1, 0, 0, 10,
        0, 1, 0, 20,
        0, 0, 1, 30,
        0, 0, 0, 1);
    ```

!!! warning "The zero matrix is not the identity matrix."
    A zero matrix initialized with all components being `0` does not mean "no transformation". The identity matrix should be used when an initial transformation is required.

### Supported operations

| Operations | Behaviors |
| --- | --- |
| Matrix `*` matrix | The full 4 × 4 matrix multiplication supports combinations of two-dimensional and three-dimensional transformations. |
| Matrix `==`, `!=` matrix | Compare each component precisely. Do not use floating-point tolerances. |

Matrix addition and subtraction, multiplication between matrices and scalars, unary negation, modulus operation, size comparison, or mixed operations between vectors and matrices are not supported. Scaling should be performed using a scaling matrix.

### Bind to CSS transform

`style.transform` can be directly bound to matrix properties or matrix products. The SDK automatically outputs the result as CSS `matrix3d(...)`. After the bound properties receive a change notification, the page recalculates and updates the transformation.

```html
<!-- The current data context provides a Transform matrix property. -->
<div @style.transform="{Transform}">内容</div>

<!-- Scale first, then rotate, then translate. -->
<div @style.transform="{Translation * Rotation * Scaling}">内容</div>
```

Matrix multiplication is generally not commutative. Changing the order will change the result. When rotating around a central point `q`, the combination order is `T(q) * R * T(-q)`. The translation matrix and rotation matrix are prepared by the application; `T(...)` is not a bound expression function.

### C# types and platform mapping

- `#!csharp MarkupUI.Sdk.Core.Matrix4x4` uses `double` components and directly follows the SDK’s CSS column vector conventions.
- `#!csharp System.Numerics.Matrix4x4` Use `float` Convention for components and row vectors. When mapped to the SDK, it will be transposed and upgraded `Double`; When written back, it will be transposed again and converted `float`, rounding errors may occur.

When using `System.Numerics.Matrix4x4`, the application code still constructs matrices according to the rules of that type itself. For example, the following code first scales, then rotates, and finally translates, maintaining the same transformation meaning after mapping:

```csharp
var matrix = System.Numerics.Matrix4x4.CreateScale(2, 3, 1)
    * System.Numerics.Matrix4x4.CreateRotationZ((float)System.Math.PI / 2)
    * System.Numerics.Matrix4x4.CreateTranslation(10, 20, 0);
```

The Mapper in Unreal Engine and Unity plugins is responsible for performing bidirectional coordinate axis mapping between platform-native types and SDK matrices. For example, the positive Roll in Unreal Engine is mapped to a positive Z-axis rotation in CSS. Matrices and matrix products in the page are uniformly used according to CSS semantics, and the multiplication conventions of engine-native matrices should not be directly applied.

## Objects, Collections

| Type | Meaning | C++ | C# |
| --- | --- | --- | --- |
| `Object` | Object | `#!cpp MarkupUI::Binding::IObject` | `#!csharp System.ComponentModel.INotifyPropertyChanged` |
| `Array` | Ordered List | `#!cpp MarkupUI::Binding::IArray<T>` | `#!csharp System.Collections.Generic.IList<T>` |
| `Map` | Dictionary | `#!cpp MarkupUI::Binding::IMap<TKey, TValue>` | `#!csharp System.Collections.Generic.IDictionary<TKey, TValue>` |
| `Set` | Collection | `#!cpp MarkupUI::Binding::ISet<T>` | `#!csharp System.Collections.Generic.ISet<T>` |
| `KeyValue` | Key-Value Pairs | `#!cpp MarkupUI::Binding::KeyValue<TKey, TValue>` | `#!csharp System.Collections.Generic.KeyValuePair<TKey, TValue>` |

The objects and collection types in the table list the most commonly used interfaces. One row of `KeyValue` lists the key-value pair structure type.

### Collection change notification interface

| Notification | C++ | C# |
| --- | --- | --- |
| Property changes | `#!cpp MarkupUI::Binding::INotifyPropertyChanged` | `#!csharp System.ComponentModel.INotifyPropertyChanged` |
| Changes in Array and Set data items | `#!cpp MarkupUI::Binding::INotifyCollectionChanged<T>` | `#!csharp System.Collections.Specialized.INotifyCollectionChanged` |
| Changes in Map key-value pairs | `#!cpp MarkupUI::Binding::INotifyCollectionChanged<MarkupUI::Binding::KeyValue<TKey, TValue>>` | `#!csharp System.Collections.Specialized.INotifyCollectionChanged` |

C++'s `IArray`, `IMap`, and `ISet` inherit the corresponding collection notification interfaces. C#'s standard collection interfaces do not include change notification contracts, and the notification interfaces need to be implemented separately by the specific collections.

### Commonly observable implementations

| Type | C++ | C# |
| --- | --- | --- |
| Object base class | `#!cpp MarkupUI::Binding::Modeling::ObservableObject` | `#!csharp System.ComponentModel.INotifyPropertyChanged` |
| Array | `#!cpp MarkupUI::Binding::Modeling::ObservableArray<T>` | `#!csharp System.Collections.ObjectModel.ObservableCollection<T>` |
| Map | `#!cpp MarkupUI::Binding::Modeling::ObservableMap<TKey, TValue>` | `#!csharp MarkupUI.Sdk.Binding.ObservableDictionary<TKey, TValue>` |
| Set | `#!cpp MarkupUI::Binding::Modeling::ObservableSet<T>` | `#!csharp MarkupUI.Sdk.Binding.ObservableHashSet<T>` |

`ObservableCollection<T>` belongs to the .NET standard library. The C# observable dictionary and observable Set mentioned in the table are provided by the SDK. They are concrete collection classes, not interfaces like `IObservableCollection` or `IObservableDictionary`.

Objects and collections do not undergo arithmetic operations item by item, nor are all fields or contents recursively compared due to equality comparisons.

For accessing objects and properties, refer to [Basic Binding](basic-binding.md). For collection operations, refer to [Collection Binding](collection-binding.md). Commands use a separate interaction protocol and do not belong to the aforementioned property value types.

## Null values and invalid results

`Null` indicates that there is no value, which is different from `0`, `false`, or an empty string. The path cannot obtain a value, or the expression may result in null or unavailable results due to type mismatch, zero division, out-of-bound arithmetic operations, etc.

```html
<p>{{ Weapon.Name ?? 'No weapon' }}</p>
<p>{{ (Amount / Divisor) ?? 0 }}</p>
```

`??` Default values are provided for results that are either empty or unavailable, without replacing them `0`, `false` Or an empty string.`Unknown` Represents types that are not specified or not supported. They are not values that can be used in business calculations.

## Comparison and logical judgment

- **Numbers** can be compared numerically across integer widths, signedness, and floating-point types; Boolean values do not belong to the category of numbers.
- **Colors, vectors, matrices** Supports exact equality comparisons for the same type, per component. No floating-point tolerance is used. Size comparisons are not supported.
- **Different non-numeric types** Does not automatically convert to the same type, such as strings `'1'` Not equal to numerical values `1`.
- In **logical judgment**, null values are considered false. Boolean values use their own values. Finite numbers with a non-zero value are considered true, and strings with a non-empty value are considered true. Valid objects and sets are considered true, including empty sets.
- **Color, vector, and matrix** are always false during logical evaluations. Their truth or falsity is determined not by whether their components are non-zero. Boolean properties or comparison expressions should be explicitly provided.

The operators, priorities, and short-circuit rules of expressions are described in [Binding Syntax](binding-syntax.md).

[^css-matrix-semantics]: The native matrix conventions used in Unity and Unreal Engine are not completely consistent with CSS. When bound to a page, the adaptation on each platform is converted to CSS semantics. When the matrix is written back to the native types of the platform, the conversion is reversed.
