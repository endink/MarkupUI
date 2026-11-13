---
icon: bootstrap/code-slash
---

# 标记与绑定语法

Markup UI 使用 HTML 元素组织界面，通过文本插值和模板属性声明绑定。表达式的详细规则见[绑定语法](../binding/binding-syntax.md)。

## 指令与前缀

模板属性支持等价的 `@` 和 `mk:` 前缀：

```html
<span @text="{Name}"></span>
<span mk:text="{Name}"></span>
```

`Name` 为 `Alice` 时，两者均输出：

```html
<span>Alice</span>
```

两种前缀可以混用，但不能重复声明同一目标或选项。表达式内的 `@this`、`@item` 和别名仍使用 `@`，不替换为 `mk:`。XML 规范写法见[XHTML 支持](../binding/xhtml-support.md)。

| 标记 | 示例 | 作用 |
| --- | --- | --- |
| `@context` | `@context="player"` | 使用应用登记的命名上下文 |
| `@context` | `@context="{Child}"` | 使用当前上下文的 `Child` 属性 |
| `@as` | `@as="page"` | 为继承或切换后的当前上下文创建 `@page` 别名，可独立使用 |
| `@if` | `@if="{IsReady}"` | 条件成立时生成当前分支 |
| `@else-if` | `@else-if="{IsLoading}"` | 前面分支未命中时判断条件 |
| `@else` | `@else` | 前面分支均未命中时生成内容 |
| `@for` | `@for="{Items}"` | 按集合项重复生成当前容器的子内容 |
| `@item-as` | `@item-as="item"` | 为当前集合元素创建 `@item` 别名 |
| `@items-as` | `@items-as="items"` | 为当前遍历的集合创建 `@items` 别名 |

`@else-if`、`@else` 必须与前面的分支同级相邻，中间只允许空白和注释；分支链从 `@if` 开始，`@else` 位于最后。`@item-as`、`@items-as` 需要同元素的 `@for`；循环容器上的 `@as` 表示容器上下文，不表示集合元素。


## 绑定目标

| 标记 | 示例 | 说明 |
| --- | --- | --- |
| `{{ ... }}` | `{{ Name }}` | 将结果插入文本，可与静态文字混合 |
| `@text` | `@text="{Name}"` | 替换元素内的文本，占位文字可用于设计时预览 |
| `@html` | `@html="{Content}"` | 使用结果生成动态 HTML 内容 |
| `@value` | `@value="{Name}"` | 用于 `input`、`textarea`、`select`、`option` |
| `@values` | `@values="{SelectedValues}"` | 用于多选 `select`，不能与 `@value` 同时声明 |
| `@checked` | `@checked="{IsEnabled}"` | 绑定 `input` 的勾选状态 |
| `@disabled` | `@disabled="{IsBusy}"` | 设置禁用状态 |
| `@hidden` | `@hidden="{IsHidden}"` | 设置隐藏状态 |
| `@属性名` | `@src="{AvatarPath}"` | 设置受支持的属性 |
| `@style.属性名` | `@style.opacity="{Opacity}"` | 设置受支持的 CSS 样式属性 |

受支持的普通 HTML 属性如下；支持绑定不等于平台支持该属性对应的全部浏览器行为：

```text
title id class name lang dir role tabindex accesskey contenteditable
draggable spellcheck src srcset sizes alt href target rel download type
placeholder autocomplete inputmode min max step pattern minlength maxlength
size rows cols form action method enctype accept width height colspan rowspan scope
```

另外支持具有非空后缀的 `data-*`、`aria-*` 属性。样式目标采用 `@style.属性名`，具体属性支持范围以 Markup UI 的 CSS 支持为准，不等同于浏览器的全部 CSS 属性。

!!! warning "内容目标与模板内容"
    `@text` 和 `@html` 会接管元素的内容，不应在同一元素上同时声明两者，或同时用 `@for` 管理同一份子内容。`template` 是透明容器，用于结构指令及配套别名，不接受普通属性、样式或事件绑定。


## 绑定选项

选项可以放在绑定内部，也可以展开为同一元素的属性，两种写法等价：

```html
<input @value="{Name, mode=twoWay, update=blur}">
<input @value="{Name}" @value.mode="twoWay" @value.update="blur">
```

| 选项 | 值 | 用途 |
| --- | --- | --- |
| `mode` | `oneWay`、`twoWay`、`oneTime`、`oneWayToSource` | 指定更新方向 |
| `update` | `input`、`change`、`blur`、`explicit` | 指定输入回写时机 |
| `converter` | 应用登记的转换器名称 | 转换绑定值 |
| `converter.parameter` | 单个表达式 | 向转换器提供参数 |

输入属性通常默认 `twoWay`；显示目标和 `option` 的 `value` 默认 `oneWay`。文本与数字输入框、`textarea` 默认 `blur`，复选框、单选框、选择框、滑块等默认 `change`。完整规则见[输入与双向绑定](../binding/input-and-two-way-binding.md)。

转换器参数放在 `converter` 内，或使用展开形式：

```html
<!-- Currency 是应用登记的转换器。 -->
<span @text="{Price, converter={Currency, parameter={'USD'}}}"></span>
<span @text="{Price}" @text.converter="Currency" @text.converter.parameter="'USD'"></span>
```

同一目标的同一选项只能声明一次。展开选项必须有对应的主绑定；没有独立的 `@mode`、`@update` 或 `@converter` 指令。文本插值 `{{ ... }}` 中不填写绑定选项。

## 事件与命令

事件绑定读取数据上下文中的命令，通过 `parameter` 提供参数：

```html
<button @onclick="{Save}">Save</button>
<button @onclick="{Move, parameter={@this, TargetIndex}}">Move</button>
```

| 事件 | 可用选项 |
| --- | --- |
| `@onclick`、`@onpointerdown`、`@onpointerup` | `parameter`、`button`、`modifiers` |
| `@onkeydown`、`@onkeyup` | `parameter`、`key`、`modifiers` |
| `@oninput`、`@onchange`、`@onsubmit`、`@onfocus`、`@onblur` | `parameter` |
| `@onanimationstart`、`@onanimationiteration`、`@onanimationend`、`@onanimationcancel` | `parameter` |
| `@ontransitionrun`、`@ontransitionstart`、`@ontransitionend`、`@ontransitioncancel` | `parameter` |

- **`parameter`**：命令参数，可使用 `{Name}` 或多个表达式 `{Name, Count}`；也可展开为 `@onclick.parameter`。
- **`key`**：静态逻辑按键名称，例如 `'Enter'`。
- **`button`**：`Left`、`Middle`、`Right`、`Back`、`Forward` 或 `none`。
- **`modifiers`**：`Control`、`Shift`、`Alt`、`Windows`、`Meta` 的组合，例如 `Control+Shift`；`none` 表示不过滤。

事件不使用 `mode`、`update` 或 `converter`。命令路径写为 `{Save}`，不写 `{Save()}`。同一次事件同时触发输入回写和命令时，先回写，再执行命令；属性声明顺序不影响结果。事件不会强制提交尚未到回写时机的输入。

完整事件规则见[事件与命令](../binding/events-and-commands.md)。

### 动画与过渡

通过样式绑定设置 CSS 动画或过渡，通过事件绑定在生命周期变化时执行命令：

| 绑定属性 | 说明 | 示例 |
| --- | --- | --- |
| `@style.animation` | 设置 CSS 动画简写值，动画名称对应样式中的 `@keyframes` | `@style.animation="{DamageAnimation}"` |
| `@style.transition` | 设置 CSS 过渡简写值 | `@style.transition="{Transition}"` |

例如，`DamageAnimation` 可以是 `damage-float 1050ms ease-out both`；`Transition` 可以是 `opacity 200ms ease-out`。静态动画直接写在 CSS 中，不需要绑定动画声明。

| 事件属性 | 触发时机 |
| --- | --- |
| `@onanimationstart` | 动画进入播放阶段，正延迟结束后触发 |
| `@onanimationiteration` | 动画进入下一次迭代；最后一次结束使用 `animationend` |
| `@onanimationend` | 动画自然播放结束 |
| `@onanimationcancel` | 动画在自然结束前被取消 |
| `@ontransitionrun` | 过渡创建，包括延迟阶段 |
| `@ontransitionstart` | 过渡进入播放阶段，正延迟结束后触发 |
| `@ontransitionend` | 过渡自然播放结束 |
| `@ontransitioncancel` | 过渡在自然结束前被取消 |

这些事件使用与其他命令事件相同的 `parameter` 选项，不使用 `mode`、`update`、`converter` 或按键、鼠标过滤选项。事件按原生 DOM 规则冒泡，绑定在父元素上的命令也可能收到子元素的动画事件；一个元素存在多个动画或过渡属性时，也可能触发多次。

下面以 `DamageItems` 为 Map、键为唯一编号、值为显示文字。每次 `PlayDamage` 向集合新增一项，生成的数字独立播放同一个 CSS 动画；结束后把键传给外层上下文的 `RemoveDamage`：

```html
<div @as="page">
    <button @onclick="{PlayDamage}" type="button">受到伤害</button>
    <div @for="{DamageItems}">
        <span class="damage"
              @onanimationend="{@page.RemoveDamage, parameter={@key}}">{{ @item }}</span>
    </div>
</div>
```

```css
.damage {
    position: absolute;
    color: #f04452;
    pointer-events: none;
    animation: damage-float 1050ms ease-out both;
}
@keyframes damage-float {
    from { opacity: 1; transform: translateY(0px); }
    to { opacity: 0; transform: translateY(-125px); }
}
```

`PlayDamage` 和 `RemoveDamage` 由应用提供，集合新增和移除需要发送对应通知。Map 循环中，`@key` 是键，`@item` 是值。

XHTML/XML 使用声明过的 `mk:` 前缀；内联参数和展开参数写法等价：

```xml
<div xmlns="http://www.w3.org/1999/xhtml" xmlns:mk="urn:markup-ui">
    <span mk:style.animation="{DamageAnimation}"
          mk:onanimationend="{RemoveDamage, parameter={Id}}">-128</span>
    <span mk:style.animation="{DamageAnimation}"
          mk:onanimationend="{RemoveDamage}"
          mk:onanimationend.parameter="{Id}">-128</span>
</div>
```

向同一元素再次设置完全相同的动画声明不会自动重播；列表中新建的元素拥有独立动画。自然结束和取消是不同事件，不应依赖 `animationend` 处理所有取消情况。

## 使用限制

- 表达式不执行 JavaScript，不支持函数调用、赋值、自增、三元运算、可选链、数组或对象字面量。
- 双向绑定需要可写路径；`Price * Quantity` 等计算结果不能直接回写。
- 属性、下标和键必须有效；只添加绑定语法不会自动创建数据对象、属性或集合项。
- 数据变化需要对应的属性或集合通知；直接修改数据而不通知，不能保证界面更新。
- 仅支持列出的模板目标和事件，不能给任意 HTML 属性加上 `@` 就假定可用。
- 模板属性前缀和 XML 格式是两回事；使用 `mk:` 不会自动使整个文档符合 XML 规范。

数据上下文与别名见[数据上下文](../concepts/data-context.md)，结构指令见[集合绑定](../binding/collection-binding.md)和[条件绑定](../binding/conditions-and-lists.md)。

## 表达式速查

| 标记 | 含义 | 示例 |
| --- | --- | --- |
| `@context` | 选择命名数据上下文，或通过表达式切换上下文 | `#!html <div @context="{Child}"></div>` |
| `@as` | 为当前数据上下文创建别名 | `#!html <div @as="page"></div>` |
| `@if` | 条件分支 | `#!html <div @if="{IsReady}"></div>` |
| `@else-if` | 后续条件分支 | `#!html <div><p @if="{IsReady}">Ready</p><p @else-if="{IsLoading}">Loading</p></div>` |
| `@else` | 后备分支 | `#!html <div><p @if="{IsReady}">Ready</p><p @else>Waiting</p></div>` |
| `@for` | 按集合项重复容器的子内容 | `#!html <ul @for="{Items}"><li>{{ Name }}</li></ul>` |
| `@item-as` | 为集合元素创建别名 | `#!html <ul @for="{Items}" @item-as="item"><li>{{ @item.Name }}</li></ul>` |
| `@items-as` | 为循环集合创建别名 | `#!html <ul @for="{Items}" @items-as="list"><li>{{ @list.Count }}</li></ul>` |
| `@text` | 设置元素文本 | `#!html <span @text="{Name}"></span>` |
| `@html` | 设置动态 HTML 内容 | `#!html <div @html="{Content}"></div>` |
| `@value` | 绑定单值输入 | `#!html <input @value="{Name}">` |
| `@values` | 绑定 select 多选值 | `#!html <select multiple @values="{SelectedValues}"><option value="a">A</option></select>` |
| `@checked` | 绑定勾选状态 | `#!html <input type="checkbox" @checked="{IsReady}">` |
| `@disabled` | 绑定禁用状态 | `#!html <button @disabled="{IsBusy}"></button>` |
| `@hidden` | 绑定隐藏状态 | `#!html <div @hidden="{IsHidden}"></div>` |
| `mode` | 绑定方向选项 | `#!html <input @value="{Name, mode=twoWay}">` |
| `update` | 回写时机选项 | `#!html <input @value="{Name, update=blur}">` |
| `converter` | 转换器选项 | `#!html <span @text="{Price, converter=Currency}"></span>` |
| `converter.parameter` | 转换器参数 | `#!html <span @text="{Price}" @text.converter="Currency" @text.converter.parameter="'USD'"></span>` |
| `parameter` | 事件命令参数 | `#!html <button @onclick="{Save, parameter={Name}}"></button>` |
| `key` | 键盘事件的按键过滤 | `#!html <input @onkeyup="{Save, key='Enter'}">` |
| `button` | 鼠标事件的按键过滤 | `#!html <button @onclick="{Save, button=Left}"></button>` |
| `modifiers` | 事件的修饰键过滤 | `#!html <input @onkeydown="{Save, modifiers=Control}">` |
| `@onclick` | 点击或激活时执行命令 | `#!html <button @onclick="{Save}"></button>` |
| `@oninput` | 输入值变化时执行命令 | `#!html <input @oninput="{Save}">` |
| `@onchange` | 提交一次实际变化时执行命令 | `#!html <input @onchange="{Save}">` |
| `@onsubmit` | 表单提交时执行命令 | `#!html <form @onsubmit="{Save}"></form>` |
| `@onfocus` | 获得焦点时执行命令 | `#!html <input @onfocus="{Save}">` |
| `@onblur` | 失去焦点时执行命令 | `#!html <input @onblur="{Save}">` |
| `@onkeydown` | 按键按下时执行命令 | `#!html <input @onkeydown="{Save}">` |
| `@onkeyup` | 按键释放时执行命令 | `#!html <input @onkeyup="{Save}">` |
| `@onpointerdown` | 指针按下时执行命令 | `#!html <button @onpointerdown="{Save}"></button>` |
| `@onpointerup` | 指针抬起时执行命令 | `#!html <button @onpointerup="{Save}"></button>` |
| `{{` | 文本插值开始 | `#!html <p>{{ Name }}</p>` |
| `}}` | 文本插值结束 | `#!html <p>{{ Name }}</p>` |
| `{` | 绑定表达式或参数表达式开始 | `#!html <span @text="{Name}"></span>` |
| `}` | 绑定表达式或参数表达式结束 | `#!html <span @text="{Name}"></span>` |
| `@this` | 当前数据上下文 | `#!html <p>{{ @this.Name }}</p>` |
| `@item` | 当前集合元素；Map 中为当前值 | `#!html <ul @for="{Items}"><li>{{ @item.Name }}</li></ul>` |
| `@index` | 当前循环的遍历序号，从 `0` 开始 | `#!html <ul @for="{Items}"><li>{{ @index }}</li></ul>` |
| `@key` | Map 当前项的键 | `#!html <ul @for="{Stats}"><li>{{ @key }}</li></ul>` |
| `@items` | 当前循环遍历的集合 | `#!html <ul @for="{Items}"><li>{{ @items.Count }}</li></ul>` |
| `true` | 布尔真值 | `#!html <span @if="{true}"></span>` |
| `false` | 布尔假值 | `#!html <span @disabled="{false}"></span>` |
| `null` | 空值 | `#!html <span @if="{Weapon != null}"></span>` |
| `+` | 加法、字符串拼接；一元形式表示正号 | `#!html <p>{{ Price + Tax }}</p>` |
| `-` | 减法；一元形式表示取负 | `#!html <p>{{ Health - Damage }}</p>` |
| `*` | 乘法 | `#!html <p>{{ Price * Quantity }}</p>` |
| `/` | 除法 | `#!html <p>{{ Total / Count }}</p>` |
| `%` | 取余 | `#!html <p>{{ Index % 2 }}</p>` |
| `==` | 等于 | `#!html <span @if="{Health == 100}"></span>` |
| `!=` | 不等于 | `#!html <span @if="{Health != 0}"></span>` |
| `#!html <` | 小于 | `#!html <span @if="{Health < 100}"></span>` |
| `#!html <=` | 小于或等于 | `#!html <span @if="{Health <= 100}"></span>` |
| `>` | 大于 | `#!html <span @if="{Health > 0}"></span>` |
| `>=` | 大于或等于 | `#!html <span @if="{Health >= 0}"></span>` |
| `!` | 逻辑非 | `#!html <span @if="{!IsDead}"></span>` |
| `&&` | 逻辑与，支持短路求值 | `#!html <span @if="{IsReady && IsVisible}"></span>` |
| `||` | 逻辑或，支持短路求值 | `#!html <span @if="{IsReady || IsLoading}"></span>` |
| `??` | 空值合并，左侧非空时返回左侧，否则求值右侧 | `#!html <p>{{ Name ?? 'Guest' }}</p>` |
| `(` | 运算分组开始 | `#!html <p>{{ (Price + Tax) * Quantity }}</p>` |
| `)` | 运算分组结束 | `#!html <p>{{ (Price + Tax) * Quantity }}</p>` |
| `.` | 属性访问 | `#!html <p>{{ Weapon.Name }}</p>` |
| `[` | 下标或键访问开始 | `#!html <p>{{ Items[0].Name }}</p>` |
| `]` | 下标或键访问结束 | `#!html <p>{{ Items[0].Name }}</p>` |
| `:lt:` | `#!html <` | `#!html <span @if="{Health :lt: 100}"></span>` |
| `:le:` | `#!html <=` | `#!html <span @if="{Health :le: 100}"></span>` |
| `:gt:` | `>` | `#!html <span @if="{Health :gt: 0}"></span>` |
| `:ge:` | `>=` | `#!html <span @if="{Health :ge: 0}"></span>` |
| `:and:` | `&&` | `#!html <span @if="{IsReady :and: IsVisible}"></span>` |
| `:or:` | `||` | `#!html <span @if="{IsReady :or: IsLoading}"></span>` |
| `\'` | 表达式字符串中的单引号 | `#!html <p>{{ 'Player\'s name' }}</p>` |
| `\\` | 表达式字符串中的反斜杠 | `#!html <p>{{ 'C:\\UI' }}</p>` |
| `\n` | 表达式字符串中的换行 | `#!html <p>{{ 'Line 1\nLine 2' }}</p>` |
| `\r` | 表达式字符串中的回车 | `#!html <p>{{ 'Line 1\rLine 2' }}</p>` |
| `\t` | 表达式字符串中的制表符 | `#!html <p>{{ 'Name\tHealth' }}</p>` |
| `\{{` | 普通文本中输出字面量 `{{`，不开始插值 | `#!html <p>\{{ Name }}</p>` |
