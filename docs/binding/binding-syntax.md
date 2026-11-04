---
icon: bootstrap/braces
---

# 绑定语法

属性路径从当前数据上下文读取值；表达式可以进一步组合属性值、字面量和运算符，用于显示计算结果或判断条件。表达式随其依赖的数据变化通知重新求值。

## 声明表达式

- **文本插值**使用双括号 `{{ ... }}`，可以与固定文字混合。
- **绑定属性**使用单括号 `{...}`，例如 `@text`、`@value` 和 `@style.opacity`。

```html
<p>Health: {{ Health }} / {{ MaxHealth }}</p>
<span @text="{Health + Shield}"></span>
```

假设 `Health` 为 `80`、`MaxHealth` 为 `100`、`Shield` 为 `20`。

输出：

```html
<p>Health: 80 / 100</p>
<span>100</span>
```

表达式中的属性名、作用域名称和字符串内容**区分**大小写。HTML 中的静态文本和普通属性值不会自动作为绑定表达式求值。

## 属性路径

### 当前上下文与多级属性

不带前缀的名称从当前数据上下文读取。点号用于继续访问前一级对象的属性：

```html
<p>{{ Name }}</p>
<p>{{ Weapon.Name }}</p>
<p>{{ Weapon.Owner.Name }}</p>
```

假设玩家名称为 `Alice`、武器名称为 `Sword`，武器所有者名称为 `Alice`。

输出：

```html
<p>Alice</p>
<p>Sword</p>
<p>Alice</p>
```

`Weapon.Owner.Name` 依次读取当前对象的 `Weapon`、武器的 `Owner` 和所有者的 `Name`。`@this` 明确表示当前数据上下文，因此 `Name` 与 `@this.Name` 含义相同。

切换上下文后，路径从新上下文开始：

```html
<section @context="{Weapon}">
  <p>{{ Name }}</p>
  <p>{{ Owner.Name }}</p>
</section>
```

输出：

```html
<section>
  <p>Sword</p>
  <p>Alice</p>
</section>
```

这里的 `Name` 是武器名称。路径中的对象替换及属性通知见[基础绑定](basic-binding.md)。

### 固定索引与键

Array 使用从 `0` 开始的整数下标；Map 使用与实际键类型一致的键：

```html
<p>{{ Items[0].Name }}</p>
<p>{{ Stats['Health'] }}</p>
<p>{{ PlayersById[1001].Name }}</p>
```

假设第一项名称为 `Sword`，`Stats` 的 `Health` 键对应 `80`，编号 `1001` 的玩家名称为 `Alice`。

输出：

```html
<p>Sword</p>
<p>80</p>
<p>Alice</p>
```

Map 的整数键表示键值，不代表遍历位置。字符串键应使用单引号；`Stats['Health']` 中的 `Health` 是固定键，不是数据上下文的属性。

!!! warning "Set 不支持下标访问"
    `Tags[0]` 等路径无效。Set 应通过循环读取数据项，不能根据遍历序号反向使用下标查找。各集合的访问规则见[集合绑定](collection-binding.md)。

### 动态索引与键

方括号中也可以使用属性或表达式，按当前值选择数据项：

```html
<p>{{ Items[SelectedIndex].Name }}</p>
<p>{{ Items[SelectedIndex + 1].Name }}</p>
<p>{{ Stats[SelectedStat] }}</p>
```

假设 `SelectedIndex` 为 `0`，前两项名称依次为 `Sword`、`Potion`；`SelectedStat` 为 `Health`，对应的值为 `80`。

输出：

```html
<p>Sword</p>
<p>Potion</p>
<p>80</p>
```

`SelectedIndex` 提供整数下标，`SelectedStat` 提供 Map 的键。它们发生变化并通知绑定后，路径会重新读取选中的数据项。集合变化及选中项属性变化也需要相应通知。

动态索引不会改变容器的访问规则：Array 不接受字符串下标，Map 的键仍须与实际类型匹配，Set 仍不支持索引。

## 字面量

| 类别 | 写法 | 说明 |
| --- | --- | --- |
| 整数 | `0`、`100`、`-10` | 十进制整数 |
| 浮点数 | `0.5`、`1.25`、`1e3`、`2.5e-2` | 小数或科学计数法 |
| 字符串 | `'Alice'`、`''` | 使用单引号，`''` 是空字符串 |
| 布尔值 | `true`、`false` | 使用小写形式 |
| 空值 | `null` | 表示没有值 |

## 字符转义

普通文本、表达式字符串和 HTML 属性使用不同的转义规则。以下代码均表示 HTML 文件中的实际内容；如果再将其写入 C++ 或 C# 字符串，还需遵守对应语言的字符串规则。

### 表达式字符串中的转义

转义字符：

| 转义 | 含义 |
| --- | --- |
| `\'` | 单引号 |
| `\\` | 反斜杠 |
| `\n` | 换行 |
| `\r` | 回车 |
| `\t` | 制表符 |

```html
<p>{{ 'Player: ' + Name }}</p>
<span @text="{'Player\'s weapon: ' + Weapon.Name}"></span>
```

假设 `Name` 为 `Alice`，`Weapon.Name` 为 `Sword`。

输出：

```html
<p>Player: Alice</p>
<span>Player's weapon: Sword</span>
```

表达式中的字符串必须用单引号包裹，**不能用双引号或反引号包裹**。字符串内容可以包含双引号；写在双引号包裹的 HTML 属性中时，应将内容中的双引号写为 `&quot;`。Unicode 字符可以直接输入，**不支持** `\uXXXX` 转义。

```html
<span @text="{'Path: C:\\temp'}"></span>
```

输出：

```html
<span>Path: C:\temp</span>
```

这里字符串内的反斜杠需要写成 `\\`，与普通文本直接写 `C:\temp` 的规则不同。

### 双引号处理

表达式字符串使用单引号包裹，内容中的双引号可以直接写入，无需反斜杠转义：

```html
<!-- Name = "Alice" -->
<p>{{ '"Player: ' + Name + '"' }}</p>
```

输出：

```html
<p>"Player: Alice"</p>
```

如果表达式写在双引号包裹的 HTML 属性中，内容中的双引号应写成 `&quot;`，避免提前结束属性值：

```html
<!-- Name = "Alice" -->
<span @text="{'&quot;Player: ' + Name + '&quot;'}"></span>
```

输出：

```html
<span>"Player: Alice"</span>
```

HTML 先将 `&quot;` 解码为双引号，再解析表达式。不要使用 `\"` 代替 HTML 实体：反斜杠不能转义 HTML 属性的结束引号，表达式字符串也不支持 `\"` 转义。

### 普通文本中的大括号

单个 `{`、`}` 是普通文字，无需转义。只有 `{{` 会开始文本插值；需要原样显示它时，在前面添加反斜杠，写为 `\{{`：

```html
<p>Object: { Name, Health }</p>
<p>Syntax: \{{ Name }}</p>
```

输出：

```html
<p>Object: { Name, Health }</p>
<p>Syntax: {{ Name }}</p>
```

未参与插值结束的 `}}` 可以直接显示，不必额外转义。`\{{` 只转义紧随其后的起始标记，不会使后续整段文字停止识别插值。

### 转义文本与插值混合

假设 `Name` 为 `Alice`，同一段文字中可以同时显示插值语法和实际绑定值：

```html
<p>Literal: \{{ Name }}; value: {{ Name }}</p>
```

输出：

```html
<p>Literal: {{ Name }}; value: Alice</p>
```

需要在绑定结果外侧显示单个大括号时，可将字面大括号与插值分开：

```html
<p>{ {{ Name }} }</p>
```

输出：

```html
<p>{ Alice }</p>
```

也可以在表达式内部使用字符串拼接：

```html
<p>{{ '{' + Name + '}' }}</p>
<span @text="{'{' + Name + '}'}"></span>
```

输出：

```html
<p>{Alice}</p>
<span>{Alice}</span>
```

字符串中的大括号是文字，不是新的绑定边界，不需要写成 `\{` 或 `\}`。

### 插值前的反斜杠

只有紧邻 `{{` 的连续反斜杠按插值转义规则处理：每两个反斜杠输出一个字面反斜杠，剩下一个时转义 `{{`。仍假设 `Name` 为 `Alice`：

| HTML 文本内容 | 最终显示 |
| --- | --- |
| `\{{ Name }}` | `{{ Name }}` |
| `\\{{ Name }}` | `\Alice` |
| `\\\{{ Name }}` | `\{{ Name }}` |

其他普通文本中的反斜杠保持原样。例如，`C:\temp` 不会将 `\t` 解释成制表符。普通文本中的 `@`、`@@` 也保持原样，不使用 `@@` 表示单个 `@`。

### HTML 实体与模板转义

属性表达式中的 `<`、`&` 等字符推荐使用运算符别名，避免与 HTML／XML 标记冲突：

```html
<p @if="{Health :lt: MaxHealth :and: !IsDead}">Needs healing</p>
```

假设 `Health` 为 `80`、`MaxHealth` 为 `100`、`IsDead` 为 `false`。

输出：

```html
<p>Needs healing</p>
```

!!! info "可以使用标准 HTML 转义字符，但不推荐"
    HTML 实体先解码，之后才解析表达式，因此也可以使用 `&lt;`、`&amp;` 等标准 HTML 转义字符。下面的写法与运算符别名等价，但可读性较差，推荐使用 `:lt:`、`:and:` 等别名。

    ```html
    <p @if="{Health &lt; MaxHealth &amp;&amp; !IsDead}">Needs healing</p>
    ```

    等效的内置运算符别名写法：

    ```html
    <p @if="{Health :lt: MaxHealth :and: !IsDead}">Needs healing</p>
    ```

    使用上面的示例数据，输出：

    ```html
    <p>Needs healing</p>
    ```

XML 兼容模板的完整规则见[XHTML 支持](xhtml-support.md)。

!!! warning "字符实体不能阻止插值"
    `&#123;&#123; Name }}` 解码后仍是 `{{ Name }}`，会读取 `Name`，不会原样显示插值语法。需要显示字面插值标记时，应使用 `\{{ Name }}`。

### 绑定结果不再次解析

普通文本和属性绑定的结果是数据，不会再次扫描其中的模板语法。例如，`Name` 的实际内容为 `{{ OtherName }}` 时：

```html
<!-- Name = "{{ OtherName }}" -->
<p>{{ Name }}</p>
```

输出：

```html
<p>{{ OtherName }}</p>
```

其中 `{{ OtherName }}` 是字面文本，不会继续读取 `OtherName`。此时无需在业务数据中额外添加模板转义。显式的动态 HTML 绑定按其自身规则处理，不属于普通文本绑定。

## 运算符

数字、字符串、颜色、向量和矩阵各自支持的运算不同。以下介绍通用语法；完整类型范围及向量、矩阵算术见[数据类型](data-types.md)。

### 算术运算符

| 运算符 | 含义 | 示例 |
| --- | --- | --- |
| `+` | 加法；任一操作数为字符串时进行字符串拼接 | `Health + Shield`、`'HP: ' + Health` |
| `-` | 减法或一元负号 | `MaxHealth - Health`、`-Offset` |
| `*` | 乘法 | `Price * Quantity` |
| `/` | 除法 | `Health / MaxHealth` |
| `%` | 取余 | `SelectedIndex % 2` |

```html
<p>Total: {{ Price * Quantity }}</p>
<p>{{ 'HP: ' + Health + '/' + MaxHealth }}</p>
```

假设 `Price` 为 `10`、`Quantity` 为 `3`、`Health` 为 `80`、`MaxHealth` 为 `100`。

输出：

```html
<p>Total: 30</p>
<p>HP: 80/100</p>
```

除法可产生小数，例如 `5 / 2` 为 `2.5`。不要依赖运算符将数字字符串自动转换成数值；`'10' + 2` 的结果是字符串 `102`，不是数值 `12`。

除零、对零取余、超出支持范围的整数运算和非有限浮点结果会得到空结果，不会自动变为 `0`。

### 比较运算符

| 运算符 | 含义 |
| --- | --- |
| `==`、`!=` | 相等、不相等 |
| `<`、`<=` | 小于、小于等于 |
| `>`、`>=` | 大于、大于等于 |

数值之间按数值比较，字符串之间可比较文本顺序；不要依赖不同类别的值进行隐式转换。例如，`null == 0` 为 `false`，`null == ''` 也为 `false`。对象相等不表示逐个比较其所有业务属性。

### 逻辑运算符

| 运算符 | 含义 |
| --- | --- |
| `!` | 逻辑非 |
| `&&` | 逻辑与 |
| `||` | 逻辑或 |

逻辑运算返回布尔值：

```html
<p>{{ IsReady :and: HasWeapon }}</p>
<p>{{ !IsDead }}</p>
```

假设 `IsReady`、`HasWeapon` 均为 `true`，`IsDead` 为 `false`。

输出：

```html
<p>true</p>
<p>true</p>
```

逻辑判断中，`null`、不可用值、`false`、数值 `0` 和空字符串为假，非零有限数值及非空字符串为真。有效对象和集合为真，空集合也不会仅因项数为 `0` 而变为假。判断集合是否有内容时应使用 `Items.Count :gt: 0`。

#### 短路求值

逻辑与 `&&`（`:and:`）和逻辑或 `||`（`:or:`）支持短路求值：

- **逻辑与**：左侧为假时，结果已经确定为 `false`，不计算右侧。
- **逻辑或**：左侧为真时，结果已经确定为 `true`，不计算右侧。

```html
<!-- 左侧为假，不计算右侧的除法 -->
<p>{{ false :and: (1 / 0) }}</p>

<!-- 左侧为真，不计算右侧的除法 -->
<p>{{ true :or: (1 / 0) }}</p>
```

输出：

```html
<p>false</p>
<p>true</p>
```

也可以先检查计算条件，再决定是否继续求值：

```html
<!-- Divisor = 0：左侧为假，不执行除法 -->
<p>{{ Divisor != 0 :and: Amount / Divisor :gt: 1 }}</p>
```

输出：

```html
<p>false</p>
```

### ?? 运算符

空值合并运算符 `??` 用于在没有值时提供替代值。它先读取左侧：

- 左侧有值时，返回左侧的值，不计算右侧。
- 左侧为 `null` 或不可用值时，计算并返回右侧的值。

`??` 返回选中的值，不将结果转换为布尔值。

#### 提供缺省值

```html
<p>{{ Nickname ?? 'Guest' }}</p>
<p>{{ Weapon.Owner.Name ?? 'Unknown' }}</p>
<p>{{ Items[SelectedIndex].Name ?? 'No item' }}</p>
```

假设 `Nickname`、`Weapon` 均为空，`Items` 为空集合，`SelectedIndex` 为 `0`。

输出：

```html
<p>Guest</p>
<p>Unknown</p>
<p>No item</p>
```

路径中的中间对象为空、属性缺失、Array 下标越界或 Map 键不存在时，可以通过 `??` 提供缺省值。

| 表达式 | 结果 |
| --- | --- |
| `null ?? 'Guest'` | `Guest` |
| `'' ?? 'Guest'` | 空字符串 |
| `0 ?? 100` | `0` |
| `false ?? true` | `false` |

`??` 不将空字符串、`0` 或 `false` 当作缺失值，也不能修复表达式的语法错误。

#### 只在需要时计算替代值

左侧有值时，不会计算右侧的替代表达式：

```html
<!-- Name = "Alice"：保留左侧名称，不计算右侧的除法 -->
<p>{{ Name ?? (1 / 0) }}</p>
```

输出：

```html
<p>Alice</p>
```

替代值也可以从另一个属性读取：

```html
<!-- Nickname = null，Name = "Alice" -->
<p>{{ Nickname ?? Name ?? 'Guest' }}</p>
```

输出：

```html
<p>Alice</p>
```

!!! note "与逻辑或不同"
    `Name || 'Guest'` 返回布尔值，不返回名称或 `Guest`。需要在没有值时显示缺省文字，应使用 `Name ?? 'Guest'`。

!!! info "不支持空值合并赋值"
    Markup UI 支持 `??`，但不支持 C# 的 `??=` 赋值运算符、`throw` 表达式或 `?.` 可选链。`??` 只计算结果，不修改原属性；不能将 C# 示例直接作为模板表达式使用。

### 运算符别名

在 HTML 中编写 `<`、`>`、`&` 等字符可能涉及标记与实体转义，可以使用以下等价别名：

| 运算符 | 别名 |
| --- | --- |
| `<` | `:lt:` |
| `<=` | `:le:` |
| `>` | `:gt:` |
| `>=` | `:ge:` |
| `&&` | `:and:` |
| `||` | `:or:` |

```html
<p>{{ Health :lt: MaxHealth :and: !IsDead }}</p>
<span @text="{Health :ge: 100}"></span>
```

假设 `Health` 为 `80`、`MaxHealth` 为 `100`、`IsDead` 为 `false`。

输出：

```html
<p>true</p>
<span>false</span>
```

别名两端的冒号都必须保留。字符串中的 `':and:'` 只是文本，不作为运算符处理。

## 优先级与括号

下表按优先级从高到低排列：

| 优先级 | 语法 |
| --- | --- |
| 1 | 属性访问 `.`、索引 `[]` |
| 2 | 一元 `!`、一元 `-` |
| 3 | `*`、`/`、`%` |
| 4 | `+`、`-` |
| 5 | `<`、`<=`、`>`、`>=` |
| 6 | `==`、`!=` |
| 7 | `&&` |
| 8 | `||` |
| 9 | `??` |

运算符别名与对应符号具有相同优先级。同级二元运算从左向右结合；括号可以明确计算顺序：

```html
<p>{{ 1 + 2 * 3 }}</p>
<p>{{ (1 + 2) * 3 }}</p>
```

输出：

```html
<p>7</p>
<p>9</p>
```

括号中的结果也可以继续访问属性或集合项：

```html
<p>{{ (Weapon ?? DefaultWeapon).Name }}</p>
<p>{{ (Items ?? DefaultItems)[SelectedIndex].Name }}</p>
```

假设 `Weapon`、`Items` 均为空，`DefaultWeapon.Name` 为 `Sword`，`DefaultItems` 第一项名称为 `Potion`，`SelectedIndex` 为 `0`。

输出：

```html
<p>Sword</p>
<p>Potion</p>
```

## 作用域与别名

### 外层数据上下文

通过 `@as` 为上下文声明别名，表达式中使用 `@别名` 访问。在切换上下文后，可以继续引用外层对象：

```html
<section @context="{@this}" @as="player">
  <div @context="{Weapon}">
    <p>Weapon: {{ Name }}</p>
    <p>Owner: {{ @player.Name }}</p>
  </div>
</section>
```

假设当前玩家名称为 `Alice`、武器名称为 `Sword`。

输出：

```html
<section>
  <div>
    <p>Weapon: Sword</p>
    <p>Owner: Alice</p>
  </div>
</section>
```

`@player` 是已声明的别名，不是自动识别的命名上下文。使用名为 `player` 的命名上下文仍需通过 `@context="player"` 选择。

### 循环作用域

循环中可使用 `@item`、`@items`、`@index` 和 Map 的 `@key`。`@item-as` 为当前项声明别名，`@items-as` 为当前集合声明别名：

```html
<ul @for="{Items}" @item-as="entry" @items-as="inventory">
  <li>{{ @index }}: {{ @entry.Name }} / {{ @inventory.Count }}</li>
</ul>
```

假设 `Items` 包含名称依次为 `Sword`、`Potion` 的两个对象。

输出：

```html
<ul>
  <li>0: Sword / 2</li>
  <li>1: Potion / 2</li>
</ul>
```

嵌套循环中的内置名称指向内层循环；需要保留外层项或集合时，使用不同名称的别名。别名只在声明的作用域及其子作用域中有效，不会传递给相邻区域；内层同名别名会遮蔽外层别名。

## 表达式与绑定选项

属性路径或计算公式决定读取什么，绑定选项决定如何传递结果。例如：

```html
<input @value="{Name, mode=twoWay, update=blur}">
```

假设 `Name` 为 `Alice`，初始输出：

```html
<input value="Alice">
```

这里 `Name` 是表达式，逗号后的 `mode` 和 `update` 是绑定选项。展开形式与之对应：

```html
<input @value="{Name}" @value.mode="twoWay" @value.update="blur">
```

输出：

```html
<input value="Alice">
```

转换器通过 `converter` 指定，可通过 `converter.parameter` 提供参数。转换器需要由应用提供，不是表达式可以直接调用的函数：

```html
<!-- Currency 是应用已提供的转换器名称 -->
<span @text="{Price}" @text.converter="Currency" @text.converter.parameter="'USD'"></span>
```

假设 `Price` 为 `10`，应用提供的 `Currency` 转换器将该值格式化为 `USD 10.00`。

输出：

```html
<span>USD 10.00</span>
```

`mode`、`update`、转换器和事件参数属于各绑定声明的选项，不是通用运算符，也不能把这些逗号选项直接写进 `{{ ... }}`。模式与更新时机见[数据绑定概述](getting-started.md)。

## 可写路径与计算结果

`Name`、`Weapon.Name`、`Items[SelectedIndex].Name` 等路径可以定位具体属性；能否写回还取决于属性是否可写、容器是否支持相应写入及绑定目标是否支持输入。

```html
<input @value="{Items[SelectedIndex].Name}">
```

假设 `SelectedIndex` 为 `0`，对应物品名称为 `Sword`，初始输出：

```html
<input value="Sword">
```

`Price * Quantity`、`Name ?? 'Guest'` 等表达式只产生计算结果，不对应一个可直接写入的业务属性：

```html
<span @text="{Price * Quantity}"></span>
```

假设 `Price` 为 `10`、`Quantity` 为 `3`。

输出：

```html
<span>30</span>
```

不能通过设置 `twoWay` 让计算结果自动反推到原属性。若要编辑计算结果，应由应用提供明确的可写属性及业务处理。

## 不支持的语法

表达式不是 JavaScript 或 C# 脚本，不支持以下写法：

| 写法 | 原因 |
| --- | --- |
| `GetName()`、`Math.Round(Price)` | 不支持函数或方法调用 |
| `Health = 100`、`Health += 1`、`Health++` | 不支持赋值、复合赋值或自增 |
| `IsReady ? 'Ready' : 'Waiting'` | 不支持三元条件运算符 |
| `Weapon?.Name` | 不支持可选链；可用普通路径与 `??` 处理缺失结果 |
| `Value === 0`、`Value !== 0` | 不支持严格相等运算符，使用 `==` 或 `!=` |
| `[1, 2]`、`{Name: 'Alice'}` | 不支持数组或对象字面量 |
| `A & B`、`A << 1`、`2 ** 3` | 不支持位运算、移位或幂运算 |

需要格式化、复杂计算或业务操作时，由应用提供属性、转换器或命令；不要将脚本写入绑定表达式。
