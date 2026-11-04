---
icon: bootstrap/input-cursor-text
---

# 输入与双向绑定

双向绑定既将数据上下文中的属性显示到输入控件，也将用户输入写回对应属性。应用修改属性并发出通知时，控件随之更新；用户编辑控件时，按配置的提交时机更新数据上下文。

本章示例使用可观察对象的可写属性。对象定义和通知写法见[数据上下文](../concepts/data-context.md)，类型范围见[数据类型](data-types.md)。

## 输入值与绑定目标

| HTML 元素 | 绑定目标 | 数据上下文中的值 | 默认模式 |
| --- | --- | --- | --- |
| `input`、`textarea` | `@value` | 字符串或可转换的数值 | `twoWay` |
| `input type="checkbox"` | `@checked` | 布尔值 | `twoWay` |
| 单选 `select` | `@value` | 与选项值对应的标量 | `twoWay` |
| 多选 `select` | `@values`，或 `multiple` 配合 `@value` | 标量 Array | `twoWay` |
| `option` | `@value` | 当前选项的值 | `oneWay` |

`@value` 读取和设置控件当前的输入值，`@checked` 对应实际勾选状态。它们不仅是设置 HTML 源文件中的初始属性。

!!! note "双向绑定需要可写属性"
    路径必须能定位可写的业务属性或可写集合项，控件也必须提供相应输入行为。`Price * Quantity`、`Name ?? 'Guest'` 等计算结果不能直接写回；设置 `twoWay` 不会自动反推业务属性。

## 文本输入

### 单行与多行文本

将字符串属性 `Name` 绑定到单行输入框，将 `Description` 绑定到文本域：

```html
<label>
  Name
  <input type="text" @value="{Name}">
</label>

<label>
  Description
  <textarea @value="{Description}"></textarea>
</label>
```

输入控件的 `value` 默认使用 `twoWay`，不必重复声明模式。两个控件分别读写当前数据上下文中的 `Name` 和 `Description`。

同一个属性可以同时用于编辑和显示：

```html
<input @value="{Name}">
<p>Player: {{ Name }}</p>
```

用户编辑输入框后，设置器更新 `Name` 并发出属性通知，下面的文本随之更新。将数据写入属性和通知其他绑定是两个环节；属性设置器应保留正确的通知逻辑。

### 设计时占位值

可以为设计时预览提供静态文字，运行时使用绑定值：

```html
<input value="Player name" @value="{Name}">
<textarea @value="{Description}">Character description</textarea>
```

静态内容不作为业务数据初始化方案。需要初始名称或描述时，应在可观察对象中设置初值。

### 数值输入

输入框可绑定整数或浮点属性，例如整数属性 `Health`：

```html
<input type="number" @value="{Health}">
```

显示时，数值转换为文本；写回时，输入文本按 `Health` 的实际类型转换，并检查其范围。HTML 的 `type="number"` 不改变业务属性类型，也不能代替写回校验。

!!! warning "无效输入不会成为有效数值"
    空文本、不能完整解析的数字、越界值或不符合目标类型的内容会使写回失败，原属性值保留。例如，整数属性不能接收 `12.5`，无符号属性不能接收负数。绑定不会将失败输入自动替换为 `0`，也不自动生成校验提示。

需要单位、特殊数字格式或其他业务转换时，应由应用提供适用的转换器及反向转换。不要将带单位的显示文本直接写入数值属性。

## 勾选状态

复选框使用 `@checked` 绑定布尔属性：

```html
<label>
  <input type="checkbox" @checked="{IsReady}">
  Ready
</label>
```

`IsReady` 为 `true` 时勾选，为 `false` 时取消勾选。用户切换勾选状态后，布尔值写回 `IsReady`。

不要用 `@value` 表示是否勾选，也不要将字符串 `'true'`、`'false'` 当作布尔属性。

## 单项选择

单选 `select` 通过 `@value` 绑定选中的选项值：

```html
<select @value="{Difficulty}">
  <option value="easy">Easy</option>
  <option value="normal">Normal</option>
  <option value="hard">Hard</option>
</select>
```

`Difficulty` 为 `normal` 时选中 **Normal**。用户选择 **Hard** 后，写回字符串 `hard`，不是显示文字 `Hard`，也不是选项下标。

选项值也可以转换为业务属性的数值类型：

```html
<select @value="{QualityLevel}">
  <option value="1">Low</option>
  <option value="2">Medium</option>
  <option value="3">High</option>
</select>
```

若 `QualityLevel` 是整数属性，选择 **High** 时写回数值 `3`。

### 从集合生成选项

`select` 支持通过 `@for` 绑定选项集合，单选和多选均可使用。`@for` 决定可选项，`@value` 或 `@values` 决定当前选中的值，两者分别绑定。

假设 `Difficulties` 的对象项包含 `Id` 和 `Name`，可通过集合绑定生成选项：

```html
<select @value="{Difficulty}" @for="{Difficulties}">
  <option @value="{Id}">{{ Name }}</option>
</select>
```

`select` 的 `Difficulty` 从外层数据上下文读取；每个 `option` 的 `Id` 和 `Name` 从当前集合项读取。`option` 的 `@value` 提供选项值，不负责将选中结果写回集合项。

绑定的属性值优先于静态 `selected`。属性为空或没有对应选项时，不应假定静态选中项会自动恢复；应用应提供与选项匹配的有效初值。

## 多项选择

使用 `@values` 将多选结果绑定到标量 Array：

```html
<select @values="{SelectedTags}">
  <option value="fire">Fire</option>
  <option value="ice">Ice</option>
  <option value="wind">Wind</option>
</select>
```

`SelectedTags` 是字符串数组或列表属性。它包含 `fire` 和 `wind` 时，对应两项选中；用户改变选择后，写回当前全部选中值。

也可以显式声明 `multiple` 并使用 `@value`：

```html
<select multiple @value="{SelectedTags}">
  <option value="fire">Fire</option>
  <option value="ice">Ice</option>
  <option value="wind">Wind</option>
</select>
```

两种写法含义相同。`@values` 本身启用多选，无需再填写 `multiple`。

多选同样可以通过 `@for` 生成选项。假设 `Tags` 的对象项包含 `Id` 和 `Name`：

```html
<select @values="{SelectedTags}" @for="{Tags}">
  <option @value="{Id}">{{ Name }}</option>
</select>
```

`Tags` 提供可选项，`SelectedTags` 保存选中的 `Id`。循环内的 `Id` 和 `Name` 属于当前标签对象，`SelectedTags` 则从外层数据上下文读取。集合增删及选项属性变化需要对应通知，具体规则见[集合绑定](collection-binding.md)。

!!! note "多选写回完整数组"
    多选提交的是按选项显示顺序排列的新数组，不是用户点击的顺序，也不是逐项增删原集合。因此，接收选择结果的属性必须允许整体赋值。不能用单个字符串、Map、Set 或对象数组接收多选结果；不要在同一元素上同时声明 `@value` 和 `@values`。

数值数组按元素类型转换全部选中值。任一选项转换失败时，不会将已成功转换的部分结果写入原属性。

## 绑定模式

输入目标默认使用 `twoWay`，可以按需要改为其他模式：

| 模式 | 输入目标的行为 |
| --- | --- |
| `twoWay` | 读取数据上下文显示，并将输入写回 |
| `oneWay` | 从数据上下文更新控件，不将用户修改写回 |
| `oneTime` | 初始化时读取，不持续跟随属性变化，也不写回 |
| `oneWayToSource` | 将控件值写入数据上下文，不从属性更新控件 |

例如，只让数据上下文更新输入框：

```html
<input @value="{Name, mode=oneWay}">
```

`oneWay` 只限制绑定方向，不禁止控件接受键盘或鼠标输入。需要只读或禁用交互时，应使用控件实际支持的相应设置。

## 提交时机

`mode` 决定更新方向，`update` 决定用户输入何时写回。提交时机仅对 `twoWay` 和 `oneWayToSource` 的写回方向有意义，不延迟数据上下文对控件的正常更新。

可以通过 `update` 显式指定提交时机：

1. **`update=input`**：在编辑过程中值发生变化、控件产生 `input` 事件时提交。例如，文本从 `A` 变成 `AB` 会产生一次输入变化；删除、粘贴等操作也可以产生该事件。它表示值发生了编辑变化，不表示用户已经结束编辑。
2. **`update=change`**：用户提交了一次实际变化、控件产生 `change` 事件时提交。例如，切换选项、勾选复选框会提交新状态；文本框通常在编辑结束并失焦后，且值相较上次提交确实发生变化时产生该事件。它强调确认后的值变化，不等同于所有失焦操作。
3. **`update=blur`**：控件失去焦点时提交已有的待写回值。它以焦点变化为提交时机，不要求控件先产生 `change` 事件；仅失焦而没有待写回变化时，不会凭空产生新数据。
4. **`update=explicit`**：不因 `input`、`change` 或 `blur` 自动写回。编辑值保持待提交状态，直到应用通过实际提供的写回入口显式提交。

!!! note "input 是输入事件，update 是绑定选项"
    `input` 描述控件中的值如何变化；`update` 决定绑定何时把该值写回数据上下文。`update=input` 的含义是选择 `input` 事件作为提交时机，并不是额外触发一个名为 `update` 的事件。

    `input` 不等于“按了一次键”。文本从 `A` 变成 `AB`、删除或粘贴都可能产生 `input`；中文输入法组字期间也可能产生它，因此不能将每次 `input` 都理解为完成了一次文字输入。平台如何处理输入法组字及何时允许写回，以其输入接入规则为准。

    即使文本框产生了 `input`，默认的 `update=blur` 也不会因此立即写回，而是等待失焦；显式设置 `update=input` 才选择随输入变化提交。

省略 `update` 时，各输入元素的默认提交时机如下：

| HTML 元素 | 目标属性 | 默认提交时机 |
| --- | --- | --- |
| `<input type="text">`（含省略 `type`） | `@value` | `blur` |
| `<input type="search">` | `@value` | `blur` |
| `<input type="email">` | `@value` | `blur` |
| `<input type="url">` | `@value` | `blur` |
| `<input type="tel">` | `@value` | `blur` |
| `<input type="password">` | `@value` | `blur` |
| `<input type="number">` | `@value` | `blur` |
| `<textarea>` | `@value` | `blur` |
| `<input type="checkbox">` | `@checked` | `change` |
| `<input type="radio">` | `@checked` | `change` |
| `<input type="range">` | `@value` | `change` |
| `<input type="color">` | `@value` | `change` |
| `<input type="date">` | `@value` | `change` |
| `<input type="datetime-local">` | `@value` | `change` |
| `<input type="month">` | `@value` | `change` |
| `<input type="week">` | `@value` | `change` |
| `<input type="time">` | `@value` | `change` |
| `<input type="file">` | `@value` | `change` |
| `<select>` | `@value` | `change` |
| `<select multiple>` | `@value` | `change` |
| `<select>` | `@values` | `change` |

以上按元素类型列出 SDK 的默认提交规则；颜色、日期、文件选择等专用控件是否可用，以各平台插件的实际支持范围为准。`@value` 不表示提供浏览器的文件对象或上传接口。

单向显示绑定不写回数据上下文，`update` 不改变绑定方向。

### 默认提交

```html
<input @value="{Name}">
```

文本输入框默认在失去焦点时写回 `Name`。如果需要随输入更新，应显式设置 `input`：

```html
<input @value="{Name, update=input}">
```

### 失去焦点时提交

```html
<input @value="{Name, update=blur}">
```

编辑期间控件可显示尚未提交的内容，离开控件后再写回 `Name`。也可以使用展开写法：

```html
<input @value="{Name}" @value.update="blur">
```

多选目标使用自己的选项名称，例如 `@values.update="blur"`。

### 显式提交

```html
<input @value="{Name, update=explicit}">
```

此时输入不会自动写回。仅添加按钮、触发 HTML `submit` 或绑定 `@onclick` 命令，都不等于已经实现显式提交；应用需要提供实际的绑定写回入口。是否提供相应操作及其调用方式，以各平台插件的公开能力为准。

!!! warning "不要依赖命令隐式提交输入"
    输入写回与事件命令是不同操作。命令不保证在执行前自动提交所有控件，尤其不能替代 `update=explicit` 的写回调用。若业务操作必须读取最新值，应明确配置提交时机及处理顺序。

## 嵌套属性与集合项

双向绑定也可以定位嵌套对象和集合项的可写属性：

```html
<input @value="{Weapon.Name}">
<input @value="{Items[SelectedIndex].Name}">
```

路径中间的对象、数组位置或 Map 键必须有效。动态下标或上下文变化后，后续输入针对当前解析出的属性，不继续写入旧对象。

循环中可编辑对象项的属性：

```html
<ul @for="{Items}">
  <li><input @value="{Name}"></li>
</ul>
```

标量 Array 项可使用 `@this` 或 `@item-as` 别名定位当前项；集合本身须支持对应位置写入：

```html
<ul @for="{Numbers}">
  <li><input @value="{@this}"></li>
</ul>
```

`@index`、`@key` 和 `@items` 是循环信息，不能作为可编辑字段写回；Set 也不提供下标赋值能力。

## 平台输入支持范围

绑定语法由 SDK 提供，焦点、键盘、鼠标、输入法和控件输入事件由平台接入。本文中的声明不代表所有 HTML 输入类型或浏览器控件行为均已支持；具体输入类型、输入法及焦点限制请阅读各平台文档。

界面可以显示初值但编辑后没有更新时，依次检查：

1. 当前数据上下文与属性路径是否正确。
2. 属性是否可写，输入值能否转换为目标类型。
3. 模式是否允许写回，提交时机是否已经满足。
4. 属性设置器是否发出通知，使其他绑定更新。
5. 平台是否向页面传递了焦点和输入事件，以及日志中是否有转换或绑定错误。
