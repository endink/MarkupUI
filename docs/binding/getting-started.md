---
icon: bootstrap/link-45deg
---

# 数据绑定概述

数据绑定在业务数据与 HTML 界面之间建立关联。应用提供数据对象，页面声明要读取的属性及显示位置；数据变化时，绑定根据通知更新界面。对于可编辑内容，绑定还可以将用户输入写回业务对象。

Markup UI 的绑定设计借鉴了 [WPF 数据绑定](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/data/#data-context){ target="_blank" rel="noopener noreferrer" }，并采用适合 HTML 的文本插值和属性指令语法。WPF 文档用于理解设计概念，具体语法与行为以 Markup UI 为准。

![数据上下文经由绑定更新 HTML 界面，用户输入按配置时机写回可写属性](images/data-binding-flow.svg#light){ .diagram-light }
![数据上下文经由绑定更新 HTML 界面，用户输入按配置时机写回可写属性](images/data-binding-flow.svg#dark){ .diagram-dark }

## 数据上下文与绑定目标

一个绑定可以从以下几个部分理解：

- **数据上下文**：提供业务数据的对象。
- **属性路径**：从数据上下文读取具体值的路径，例如 `Name` 或 `Weapon.Name`。
- **绑定目标**：页面中接收结果的文本、元素属性或样式属性。
- **绑定模式**：规定数据上下文与界面之间的更新方向。

例如，将下面的对象作为文档默认数据上下文：

```yaml
PlayerObject:
  Name: "Alice"
  Health: 100
```

在页面中绑定 `Name`：

```html
<h1>{{ Name }}</h1>
```

数据上下文为 `PlayerObject`，属性路径为 `Name`，目标为 `h1` 内的文本。

最终输出的 HTML 代码：

```html
<h1>Alice</h1>
```

这里的 HTML 展示绑定结果，不表示每次更新都要重新生成并加载整份文档。

## 数据上下文

数据上下文决定属性路径的查找起点。默认情况下，页面使用文档默认数据上下文；通过 `@context` 可以选择命名上下文或某个对象属性。

```html
<!-- 使用文档默认数据上下文 -->
<p>{{ Name }}</p>

<!-- 使用名为 "player" 的上下文 -->
<section @context="player">
  <p>{{ Name }}</p>
</section>
```

命名上下文需要由应用登记，不能仅凭 HTML 声明创建。默认、命名和嵌套上下文的规则见[数据上下文](../concepts/data-context.md)。

## 文本、属性与样式绑定

### 文本绑定

文本插值可混合固定文字与属性值：

```html
<p>Player: {{ Name }}</p>
<p>Health: {{ Health }}</p>
```

也可以使用 `@text` 明确设置元素的文本内容：

```html
<span @text="{Name}">Player name</span>
```

元素内的 `Player name` 可作为设计时占位文本，运行时由 `@text` 的绑定结果替换。例如，`Name` 为 `Alice` 时，最终显示 `Alice`。

- **双括号 `{{ ... }}`**：用于文本插值，例如 `<p>{{ Name }}</p>`。
- **单括号 `{...}`**：用于绑定属性中的表达式，例如 `<span @text="{Name}"></span>`。

### 属性绑定

在目标属性前加 `@`，可将表达式结果绑定到属性：

```html
<img @src="{AvatarPath}" alt="Player avatar">
<input @value="{Name}" @value.mode="twoWay">
```

`AvatarPath` 提供图片路径；输入框的 `value` 与 `Name` 关联。图片路径仍遵循[资源路径](../authoring/resource-paths.md)规则，数据绑定不会改变资源的查找方式。

### 样式绑定

使用 `@style.属性名` 绑定单个样式属性。例如，数据对象提供 `Opacity` 属性时：

```html
<div @style.opacity="{Opacity}">Player information</div>
```

固定外观仍可使用外部 CSS；仅将需要随业务状态变化的值设置为绑定。表达式结果应满足目标属性要求，不能假设任意对象都能转换为有效 CSS 值。

## 绑定模式

对于可交互 HTML 元素的输入属性，例如输入框的 `value` 和复选框的 `checked`，Markup UI 默认使用双向绑定（`twoWay`）；对于文本、普通属性和样式等显示目标，默认使用单向绑定（`oneWay`）。

| 模式 | 方向 | 常见用途 |
| --- | --- | --- |
| `oneWay` | 数据上下文 → 界面 | 名称、状态文字等只读显示 |
| `twoWay` | 数据上下文 ↔ 界面 | 允许用户修改的输入值 |
| `oneTime` | 初次取值时读取数据上下文 | 当前绑定期间不需要持续更新的显示 |
| `oneWayToSource` | 界面 → 数据上下文 | 只需要将界面值提交给业务对象 |

!!! note "双向绑定"
    `twoWay` 用于支持用户输入的 HTML 元素及其可写回属性，例如输入框的 `value`、复选框的 `checked`。对于不能通过用户交互修改绑定值的元素，使用 `twoWay` 没有意义，应使用 `oneWay`。

    使用双向绑定时，数据上下文中的对应属性必须可写，界面目标也必须提供相应输入行为。文本插值、普通样式和任意复杂表达式不能直接当作可编辑字段。

可通过展开形式配置模式：

```html
<input @value="{Name}" @value.mode="twoWay">
```

也可将选项写在绑定表达式中：

```html
<input @value="{Name, mode=twoWay}">
```

不同目标有自己的默认模式。需要明确方向时应显式填写；模式只决定更新方向，不保证目标具备输入能力，也不使只读业务属性自动可写。

## 数据更新与变更通知

### 数据上下文更新界面

应用修改 `Health` 后，需要通过所用平台支持的方式发出属性变更通知。绑定收到通知后重新取值并更新对应目标；不需要为了修改一个数值重新加载 HTML。

集合新增、删除和替换还涉及集合变化通知，不能仅依赖普通属性赋值更新列表。相关页面见[集合绑定](collection-binding.md)。

### 用户输入写回数据上下文

`twoWay` 和 `oneWayToSource` 涉及从界面向数据上下文写入。`mode` 指定方向，`update` 指定提交时机。

省略 `update` 时，文本输入框和文本域默认在失去焦点时提交（`blur`）；其他输入默认在 `change` 时提交，例如选择变化或勾选变化。需要随输入提交时，可以显式设置 `input`。

```html
<!-- 文本输入框默认：失去焦点时提交 -->
<input @value="{Name}">
```

需要随输入提交，可显式指定 `input`：

```html
<input
  @value="{Name}"
  @value.mode="twoWay"
  @value.update="input">
```

数据上下文变化仍可更新输入框；用户编辑后，写回按照配置的提交时机执行。完整的默认与显式提交规则见[输入与双向绑定](input-and-two-way-binding.md)。

属性通知、对象引用与输入接入由平台插件提供，详细信息请阅读各平台文档。

## 空值与绑定错误

空值、属性不存在、索引越界或 Map 键不存在时，表达式可得到不可用或空结果，不应将它们当作有效业务数据。最终显示由绑定目标和表达式处理规则决定。

这与语法错误、无效目标或写回类型不匹配不同。页面没有显示预期值时，按以下顺序检查：

1. 应用是否提供了正确的数据上下文。
2. 命名上下文和属性名称是否与实际定义一致。
3. 属性路径经过的对象是否存在且仍然有效。
4. 数据变化后是否发送了相应通知。
5. 绑定模式、目标类型和写入权限是否符合预期。
6. 平台日志中是否记录了绑定或类型错误。

!!! tip "不要通过重新加载掩盖通知缺失"
    页面首次加载有数据、后续修改却不更新时，应优先检查变更通知。重新加载能够重新读取初值，但不能替代正确的数据更新流程。

## 后续阅读

- [数据类型](data-types.md)：了解数字、字符串、颜色、向量、矩阵和集合的支持范围。
- [基础绑定](basic-binding.md)：区分标量值与对象，访问嵌套属性并处理对象替换。
- [集合绑定](collection-binding.md)：遍历 Array、Map 和 Set，显示集合项并响应集合变化。
- [绑定语法](binding-syntax.md)：访问嵌套数据、索引和表达式结果。
- [条件绑定](conditions-and-lists.md)：根据状态切换显示内容。
- [事件与命令](events-and-commands.md)：将按钮等交互关联到业务操作。
