---
icon: bootstrap/braces
---

# 数据类型

可观察对象通过属性向页面提供数据。每个属性都有确定的类型，类型决定它可以参与哪些表达式运算、是否能作为集合的键，以及如何用于文本或其他绑定目标。

本章介绍 SDK 支持的数据类型。Unreal Engine、Unity 等平台的原生类型，由对应平台插件提供绑定支持；具体类型映射和使用限制请阅读各平台文档。

!!! note "类型支持与目标支持"
    数据可以进入绑定表达式，不代表任意 HTML 属性或 CSS 样式都能接收它。例如，支持矩阵计算不会自动增加 CSS `transform` 的矩阵输入能力。绑定结果仍须符合目标要求。

## 类型一览

| 分类 | 类型 |
| --- | --- |
| 布尔值 | `Bool` |
| 整数 | `Int8`、`UInt8`、`Int16`、`UInt16`、`Int32`、`UInt32`、`Int64`、`UInt64` |
| 浮点数 | `Float`、`Double` |
| 文本 | `String` |
| 颜色 | `Color`、`ColorF` |
| 向量 | `Vector2`、`Vector3` |
| 矩阵 | `Matrix4x4` |
| 对象 | `Object` |
| 集合 | `Array`、`Map`、`Set` |
| 键值对 | `KeyValue` |
| 空值 | `Null` |

对象和集合通过引用提供给绑定。强引用保持目标对象的生命周期；弱引用不延长目标对象的生命周期，目标仍有效时，绑定可以访问其属性。

=== "C++"

    使用 `std::shared_ptr<T>` 表示强引用，使用 `std::weak_ptr<T>` 表示弱引用。`T` 为可观察对象或相应的集合类型。对象通常通过 `std::make_shared<T>()` 创建，并由应用或其他拥有方保留强引用。

=== "C#"

    使用对象实例的引用，也可以通过 `object` 类型的属性持有对象；使用 `System.WeakReference<T>` 表示弱引用。`object` 是承载对象引用的语言类型，实际对象仍须符合 SDK 对可观察对象或集合的要求。

    C# GC 可以回收不再可达的循环引用对象，不要求为打破循环引用而使用弱引用。弱引用适用于不希望属性延长目标对象生命周期的场景。

强引用和弱引用是同一目标的不同引用方式，不会改变目标对应的 `Object`、`Array`、`Map` 或 `Set` 分类。弱引用目标被回收后，绑定无法再通过该引用读取目标；弱引用失效本身不会发出属性变更通知。

## 布尔值

`Bool` 表示 `true` 或 `false`，适用于状态、条件判断和复选框等输入。

| C++ | C# | 表达式字面量 |
| --- | --- | --- |
| `#!cpp bool` | `#!csharp bool` | `true`、`false` |

布尔值支持逻辑运算、相等比较及字符串拼接，不隐式转换为数字。`true + 1` 无法进行数值加法，`true == 1` 为 `false`。

```html
<p>{{ 'Ready: ' + IsReady }}</p>
<p @if="{IsReady}">Ready</p>
```

布尔值用于文本时输出小写的 `true` 或 `false`。

## 整数

SDK 支持四种位宽的有符号与无符号整数：

| SDK 类型 | 范围 | C++ | C# |
| --- | --- | --- | --- |
| `Int8` | −128 ～ 127 | `#!cpp int8_t` | `#!csharp sbyte` |
| `UInt8` | 0 ～ 255 | `#!cpp uint8_t` | `#!csharp byte` |
| `Int16` | −32,768 ～ 32,767 | `#!cpp int16_t` | `#!csharp short` |
| `UInt16` | 0 ～ 65,535 | `#!cpp uint16_t` | `#!csharp ushort` |
| `Int32` | −2³¹ ～ 2³¹−1 | `#!cpp int32_t` | `#!csharp int` |
| `UInt32` | 0 ～ 2³²−1 | `#!cpp uint32_t` | `#!csharp uint` |
| `Int64` | −2⁶³ ～ 2⁶³−1 | `#!cpp int64_t` | `#!csharp long` |
| `UInt64` | 0 ～ 2⁶⁴−1 | `#!cpp uint64_t` | `#!csharp ulong` |

整数可用于计数、索引、标识和数值计算。Array 下标是从 `0` 开始的整数；Map 支持以上八种整数作为键。

### 运算结果

整数的加、减、乘、取余及一元负号按精确整数运算处理，结果使用 `Int64` 或 `UInt64`，不保留较窄的输入类型：

- 负数结果使用 `Int64`。
- 非负结果不超过 `Int64` 最大值时使用 `Int64`，更大时使用 `UInt64`。
- 超出 −2⁶³ ～ 2⁶⁴−1 的结果返回 `Null`，不回绕、不截断，也不自动改用浮点数。

整数除法产生 `Double`，例如 `5 / 2` 得到 `2.5`。取余结果的符号跟随被除数，例如 `-9 % 4` 得到 `-1`。

## 浮点数

| SDK 类型 | 精度 | C++ | C# |
| --- | --- | --- | --- |
| `Float` | 32 位单精度 | `#!cpp float` | `#!csharp float` |
| `Double` | 64 位双精度 | `#!cpp double` | `#!csharp double` |

浮点数适用于比例、透明度和连续变化的数值。表达式中的小数及科学计数法字面量使用 `Double`，如 `0.5`、`1e3`。

包含 `Float` 或 `Double` 的普通数字算术按 `Double` 计算，结果也是 `Double`。除零、对零取余、非有限数值参与算术或产生非有限结果时，返回 `Null`。

!!! warning "大整数转换为浮点数的精度"
    绝对值超过 2⁵³ 的整数并非都能由 `Double` 精确表示。将大整数参与浮点计算或结构值缩放时，可能损失精度。需要精确保存的标识等数据应避免这类转换。

## 字符串

`String` 保存文本。

| SDK 类型 | C++ | C# | 表达式字面量 |
| --- | --- | --- | --- |
| `String` | `#!cpp std::string`、`#!cpp std::string_view`、`#!cpp MarkupUI::String`、`#!cpp MarkupUI::StringView` | `#!csharp string` | 使用单引号，例如 `'Player'` |

表达式中的字符串字面量使用单引号：

```html
<p>{{ 'Player: ' + Name }}</p>
<p>{{ Health + ' HP' }}</p>
```

`+` 的任一侧为字符串时，执行文本拼接。数字文本不会自动解析成数值：`'1' + 2` 得到字符串 `12`，`'6' / 2` 则返回 `Null`。

字符串支持相等比较；大小比较按 UTF-8 字节序进行字典序比较，不是本地语言排序。字符串中的 HTML 标签作为文本显示，不因数据绑定而自动解析成界面结构。

## 颜色

| SDK 类型 | C++ | C# |
| --- | --- | --- |
| `Color` | `#!cpp MarkupUI::Color` | `#!csharp MarkupUI.Sdk.Core.Color` |
| `ColorF` | `#!cpp MarkupUI::ColorF` | `#!csharp MarkupUI.Sdk.Core.ColorF` |

- `Color` 包含 `R`、`G`、`B`、`A` 四个 `UInt8` 分量，每个分量范围为 0～255。
- `ColorF` 包含 `R`、`G`、`B`、`A` 四个 `Float` 分量，常规归一化颜色使用 0～1。

`A` 为透明度分量。两种颜色类型不因名称相近而自动按 255 进行归一化换算；使用时应按对应类型提供分量。

颜色支持同类型的相等与不等比较，不支持算术、大小比较或直接文本拼接。需要向 CSS 提供颜色文本时，应由应用或转换器给出目标接受的格式。

## 向量

| SDK 类型 | C++ | C# |
| --- | --- | --- |
| `Vector2` | `#!cpp MarkupUI::Vector2` | `#!csharp System.Numerics.Vector2` |
| `Vector3` | `#!cpp MarkupUI::Vector3` | `#!csharp System.Numerics.Vector3` |

- `Vector2` 包含 `X`、`Y` 分量，`Vector3` 包含 `X`、`Y`、`Z` 分量。
- SDK 内置向量分量使用 `Double`；`System.Numerics` 向量分量使用 `float`，进入 SDK 时提升为 `Double`，写回时转换为 `float`，可能产生舍入。

向量作为可观察对象的属性提供给表达式。表达式不提供 `Vector3(...)` 这样的构造函数调用或向量字面量。

### 支持的运算

| 运算 | 行为 |
| --- | --- |
| 同维向量 `+`、`-` | 对应分量相加、相减 |
| 同维向量 `*`、`/` | 对应分量相乘、相除；除数各分量均须非零 |
| 向量 `*` 数字、数字 `*` 向量 | 各分量乘该数字 |
| 向量 `/` 数字 | 各分量除以非零数字 |
| 一元 `-` | 各分量取负 |

结果保留向量维数。向量乘向量是逐分量乘法，不是点积或叉积。

```html
<!-- Velocity 为 Vector3，Speed 为数字 -->
<p>{{ Velocity * Speed }}</p>
```

若 `Velocity` 为 `(1, 2, 3)`、`Speed` 为 `2`，文本输出为 `Vector3(2, 4, 6)`。该文本用于查看值，不是可反向解析的输入格式。

Vector2 与 Vector3 混算、向量与数字加减、数字除以向量、向量取余及向量与矩阵混算均不支持。SDK 不自动补维、归一化、换算单位或转换坐标系。

## 矩阵

`Matrix4x4` 是 4 行 4 列的矩阵，可表示平移、缩放、旋转及其组合。SDK 内置类型的十六个分量均为 `Double`。矩阵在应用代码中创建，再通过可观察对象的属性提供给页面。

| SDK 类型 | C++ | C# |
| --- | --- | --- |
| `Matrix4x4` | `#!cpp MarkupUI::Matrix4x4` | `#!csharp MarkupUI.Sdk.Core.Matrix4x4`、`#!csharp System.Numerics.Matrix4x4` |

矩阵使用以下约定：

- 字段与构造参数按行排列：`M11`～`M14`、`M21`～`M24`、`M31`～`M34`、`M41`～`M44`。
- 使用行向量，`p' = p * M`。
- 平移分量位于 `M41`、`M42`、`M43`。
- `A * B` 表示先应用 A，再应用 B。
- 先缩放、再旋转、最后平移写为 `S * R * T`，其中 S 为缩放矩阵、R 为旋转矩阵、T 为平移矩阵。

`MarkupUI.Sdk.Core.Matrix4x4` 和 `System.Numerics.Matrix4x4` 均遵循以上约定。

### 分量排列

`Mij` 中的 `i` 表示行，`j` 表示列。字段和十六参数构造函数均按以下行顺序排列：

```text
M11  M12  M13  M14
M21  M22  M23  M24
M31  M32  M33  M34
M41  M42  M43  M44
```

SDK 使用**行向量**约定，点或方向写作 `p = [x, y, z, w]`，应用矩阵的数学公式为 `p' = p * M`。按行排列说明数据顺序，行向量说明乘法方向，两者含义不同。

```text
x' = x*M11 + y*M21 + z*M31 + w*M41
y' = x*M12 + y*M22 + z*M32 + w*M42
z' = x*M13 + y*M23 + z*M33 + w*M43
w' = x*M14 + y*M24 + z*M34 + w*M44
```

点通常取 `w = 1`，方向取 `w = 0`，因此方向不受平移影响。这些公式用于解释矩阵含义，表达式目前不支持向量与矩阵相乘。

### 单位矩阵

单位矩阵不改变输入点，其四个对角分量为 `1`，其他分量为 `0`：

```text
1  0  0  0
0  1  0  0
0  0  1  0
0  0  0  1
```

C++ 使用 `MarkupUI::Matrix4x4::Identity()`，C# 使用 `MarkupUI.Sdk.Core.Matrix4x4.Identity`。

!!! warning "零矩阵不是单位矩阵"
    零初始化得到所有分量均为 `0` 的零矩阵，不表示“不做变换”。需要初始变换时应使用单位矩阵。

??? note "矩阵数学含义"

    ### 平移

    平移分量位于 **`M41`、`M42`、`M43`**，分别表示 X、Y、Z 方向的位移：

    ```text
     1   0   0  0
     0   1   0  0
     0   0   1  0
    tx  ty  tz  1
    ```

    例如，沿三个轴分别平移 `10`、`20`、`30`：

    === "C++"

        ```cpp
        #include <markupui/core/matrix4x4.h>

        auto translation = MarkupUI::Matrix4x4::Identity();
        translation.M41 = 10;
        translation.M42 = 20;
        translation.M43 = 30;
        ```

    === "C#"

        ```csharp
        using Matrix4x4 = MarkupUI.Sdk.Core.Matrix4x4;

        var translation = new Matrix4x4(
             1,  0,  0, 0,
             0,  1,  0, 0,
             0,  0,  1, 0,
            10, 20, 30, 1);
        ```

    SDK 内置的 C# 矩阵为只读结构。修改矩阵属性时，应创建新值并发送对应的属性变更通知。

    ### 缩放

    缩放因子位于 **`M11`、`M22`、`M33`**，分别对应 X、Y、Z 轴；`M44` 保持为 `1`：

    ```text
    sx   0   0  0
     0  sy   0  0
     0   0  sz  0
     0   0   0  1
    ```

    三个因子相同表示等比缩放；负值表示对应轴反射，零值使该轴方向压缩为零，并使矩阵不可逆。

    ### 旋转

    下面以绕 Z 轴旋转为例。设旋转角度为 `θ`，`c = cos(θ)`、`s = sin(θ)`：

    ```text
     c  s  0  0
    -s  c  0  0
     0  0  1  0
     0  0  0  1
    ```

    该公式采用右手数学坐标约定及右手正角：绕 +Z 旋转 +90°，将 +X 方向转向 +Y。实际引擎或屏幕中的视觉方向由平台坐标约定决定。

    `sin`、`cos` 在应用代码中计算，角度以弧度传入；角度值可通过 `角度 * π / 180` 转为弧度。矩阵本身不保存角度单位或旋转顺序，也没有表达式内的三角函数调用。

    ### 组合顺序

    在行向量约定下，`A * B` 表示**先应用 A，再应用 B**。矩阵乘法通常不可交换，改变顺序会改变变换结果。

    应用分别提供缩放、旋转和平移矩阵属性后，可在表达式中组合：

    ```html
    <p>{{ Scaling * Rotation * Translation }}</p>
    ```

    这里先缩放，再旋转，最后平移。示例显示组合矩阵的文本结果；要用于实际界面变换，绑定目标或转换器还须支持相应矩阵值。

    例如，先缩放 `(2, 3, 1)`，再绕 Z 轴旋转 +90°，最后平移 `(10, 20, 0)`，组合矩阵为：

    ```text
     0   2  0  0
    -3   0  0  0
     0   0  1  0
    10  20  0  1
    ```

    点 `(1, 2, 0)` 依次变为 `(2, 6, 0)`、`(-6, 2, 0)`、`(4, 22, 0)`。

    绕中心点 `q` 旋转时，先将中心移到原点，再旋转，最后移回，即 `T(-q) * R * T(q)`。这里 `T` 表示平移矩阵，`R` 表示旋转矩阵，由应用准备，不是表达式函数。

### 支持的运算

| 运算 | 行为 |
| --- | --- |
| 矩阵 `+`、`-` 矩阵 | 对应分量相加、相减 |
| 矩阵 `*` 矩阵 | 标准矩阵乘法，不是逐分量乘法 |
| 矩阵 `*` 数字、数字 `*` 矩阵 | 所有分量乘该数字 |
| 矩阵 `/` 数字 | 所有分量除以非零数字 |
| 一元 `-` | 所有分量取负 |

矩阵除以矩阵、数字除以矩阵、矩阵与数字加减、矩阵取余及矩阵与向量相乘均不支持。

!!! warning "矩阵乘数字不等于空间缩放"
    `Matrix4x4` * `2` 会将全部十六个分量乘二，包括平移分量和 `M44`。空间缩放应由应用准备缩放矩阵，再按所需顺序进行矩阵乘法。

上述运算符描述的是模板表达式的行为，不表示 C++ 的 SDK 矩阵类型提供了相同的运算符重载。矩阵加法也不表示依次应用两个变换。

矩阵文本输出为 `Matrix4x4(...)`，分量按行排列，仅用于查看值。没有矩阵表达式构造语法、逆矩阵或矩阵分解函数，也没有 Quaternion 类型。

### C# 类型与平台适配

- `MarkupUI.Sdk.Core.Matrix4x4` 的分量使用 `double`。
- `System.Numerics.Matrix4x4` 的分量使用 `float`。

两种类型均可作为属性用于绑定，字段顺序和变换组合顺序一致。`System.Numerics.Matrix4x4` 进入 SDK 时，各分量提升为 `Double`，不转置；写回该类型时转换为 `float`。提升精度不会恢复原本已损失的精度，写回 `float` 也可能产生舍入。

需要保留 `double` 精度时使用 SDK 内置类型。使用 `System.Numerics.Matrix4x4` 时，可以在 C# 中直接调用其变换构造方法：

```csharp
var matrix = System.Numerics.Matrix4x4.CreateScale(2, 3, 1)
    * System.Numerics.Matrix4x4.CreateRotationZ((float)System.Math.PI / 2)
    * System.Numerics.Matrix4x4.CreateTranslation(10, 20, 0);
```

该组合也是先缩放、再旋转、最后平移，无需在绑定表达式中反转顺序。

!!! note "平台矩阵需要明确转换"
    SDK 的矩阵约定不等同于所有引擎的原生矩阵。平台插件需要处理分量精度、行列向量约定、坐标轴和单位。


## 对象、集合

| 类型 | 含义 | C++ | C# |
| --- | --- | --- | --- |
| `Object` | 对象 | `#!cpp MarkupUI::Binding::IObject` | `#!csharp System.ComponentModel.INotifyPropertyChanged` |
| `Array` | 有序列表 | `#!cpp MarkupUI::Binding::IArray<T>` | `#!csharp System.Collections.Generic.IList<T>` |
| `Map` | 字典 | `#!cpp MarkupUI::Binding::IMap<TKey, TValue>` | `#!csharp System.Collections.Generic.IDictionary<TKey, TValue>` |
| `Set` | 集合 | `#!cpp MarkupUI::Binding::ISet<T>` | `#!csharp System.Collections.Generic.ISet<T>` |
| `KeyValue` | 键值对 | `#!cpp MarkupUI::Binding::KeyValue<TKey, TValue>` | `#!csharp System.Collections.Generic.KeyValuePair<TKey, TValue>` |

表中的对象与集合类型列出最常用的接口；`KeyValue` 一行列出键值对结构类型。

### 集合变更通知接口

| 通知 | C++ | C# |
| --- | --- | --- |
| 属性变化 | `#!cpp MarkupUI::Binding::INotifyPropertyChanged` | `#!csharp System.ComponentModel.INotifyPropertyChanged` |
| Array、Set 数据项变化 | `#!cpp MarkupUI::Binding::INotifyCollectionChanged<T>` | `#!csharp System.Collections.Specialized.INotifyCollectionChanged` |
| Map 键值对变化 | `#!cpp MarkupUI::Binding::INotifyCollectionChanged<MarkupUI::Binding::KeyValue<TKey, TValue>>` | `#!csharp System.Collections.Specialized.INotifyCollectionChanged` |

C++ 的 `IArray`、`IMap` 和 `ISet` 已继承对应的集合通知接口。C# 的标准集合接口不包含变更通知契约，需要由具体集合额外实现通知接口。

### 常用可观察实现

| 类型 | C++ | C# |
| --- | --- | --- |
| 对象基类 | `#!cpp MarkupUI::Binding::Modeling::ObservableObject` | `#!csharp System.ComponentModel.INotifyPropertyChanged` |
| Array | `#!cpp MarkupUI::Binding::Modeling::ObservableArray<T>` | `#!csharp System.Collections.ObjectModel.ObservableCollection<T>` |
| Map | `#!cpp MarkupUI::Binding::Modeling::ObservableMap<TKey, TValue>` | `#!csharp MarkupUI.Sdk.Binding.ObservableDictionary<TKey, TValue>` |
| Set | `#!cpp MarkupUI::Binding::Modeling::ObservableSet<T>` | `#!csharp MarkupUI.Sdk.Binding.ObservableHashSet<T>` |

`ObservableCollection<T>` 属于 .NET 标准库；上表中的 C# 可观察字典和可观察 Set 由 SDK 提供。它们是具体集合类，不是 `IObservableCollection` 或 `IObservableDictionary` 接口。

对象和集合不进行逐项算术运算，也不因相等比较而递归比较所有字段或内容。

对象及属性访问见[基础绑定](basic-binding.md)，集合操作见[集合绑定](collection-binding.md)。命令使用独立的交互协议，不属于上述属性值类型。

## 空值与无效结果

`Null` 表示没有值，不等于 `0`、`false` 或空字符串。路径无法取得值，或表达式遇到类型不匹配、除零、越界算术等情况时，可能得到空或不可用结果。

```html
<p>{{ Weapon.Name ?? 'No weapon' }}</p>
<p>{{ (Amount / Divisor) ?? 0 }}</p>
```

`??` 仅为空或不可用结果提供缺省值，不替换 `0`、`false` 或空字符串。`Unknown` 表示未指定或不支持的类型，不是可供业务计算的值。

## 比较与逻辑判断

- **数字**可跨整数宽度、有无符号及浮点类型按数值比较；布尔值不属于数字。
- **颜色、向量、矩阵**支持同类型、逐分量的精确相等比较，不使用浮点容差，不支持大小比较。
- **不同的非数字类型**不自动转换为同一类型，例如字符串 `'1'` 不等于数值 `1`。
- **逻辑判断**中，空值为假，布尔值使用自身值，有限数字非零为真，字符串非空为真；有效对象和集合为真，包括空集合。
- **颜色、向量和矩阵**用于逻辑判断时均为假，不根据分量是否非零决定真假。应显式提供布尔属性或比较表达式。

表达式的运算符、优先级和短路规则见[绑定语法](binding-syntax.md)。
