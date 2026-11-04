---
icon: bootstrap/signpost-split
---

# 条件绑定

条件绑定通过 `@if` 根据数据上下文中的值选择要生成的 HTML 内容。条件为真时生成对应元素及其子内容；条件为假时，可以通过 `@else-if` 继续判断，或通过 `@else` 提供缺省内容。

## 基本语法

将布尔属性作为条件：

```html
<p @if="{IsReady}">Ready</p>
```

`IsReady` 为 `true` 时，最终输出的 HTML 代码：

```html
<p>Ready</p>
```

`IsReady` 为 `false` 时，不生成该 `p` 元素。条件也可以是比较或逻辑表达式：

```html
<p @if="{Health :le: 0}">Defeated</p>
<p @if="{IsReady :and: !IsDead}">Can start</p>
```

`@if` 的值必须使用 `{...}`。`@if="IsReady"` 不符合条件绑定语法。

## 条件分支

### 使用 @else

在同级的下一个元素上声明 `@else`，提供条件为假时的内容：

```html
<p @if="{IsReady}">Ready</p>
<p @else>Waiting</p>
```

`IsReady` 为 `false` 时，最终输出的 HTML 代码：

```html
<p>Waiting</p>
```

`@else` 不填写条件或其他值。每组分支只会生成被选中的一侧。

!!! warning "分支必须相邻且处于同一级"
    分支链必须以 `@if` 开始，后面可以接多个 `@else-if`，最后可选一个 `@else`。所有分支必须是同级相邻元素；分支之间可以有空白、换行或 HTML 注释，不能插入其他元素或非空白文本。`@else-if` 和 `@else` 不能单独使用，`@else` 之后不能再接 `@else-if`。同一个元素只能声明 `@if`、`@else-if`、`@else` 中的一个。

以下写法无效，因为 `hr` 打断了分支关系，`@if` 与 `@else` 不相邻：

```html
<!-- 错误：@if 与 @else 之间插入了其他元素 -->
<p @if="{IsReady}">Ready</p>
<hr>
<p @else>Waiting</p>
```

以下写法同样无效，因为 `@if` 位于 `section` 内，而 `@else` 位于 `section` 外，两者不在同一级：

```html
<!-- 错误：@if 与 @else 不在同一级 -->
<section>
  <p @if="{IsReady}">Ready</p>
</section>
<p @else>Waiting</p>
```

应将两个分支放在同一个父元素内，并相邻声明：

```html
<section>
  <p @if="{IsReady}">Ready</p>
  <p @else>Waiting</p>
</section>
```

### 使用 @else-if

需要依次判断多个条件、仅选择一个分支时，使用 `@else-if`：

```html
<p @if="{IsLoading}">Loading</p>
<p @else-if="{HasError}">Load failed</p>
<p @else-if="{IsEmpty}">No data</p>
<p @else-if="{IsReadOnly}">Read only</p>
<p @else>Loaded</p>
```

依次判断 `IsLoading`、`HasError`、`IsEmpty` 和 `IsReadOnly`；所有条件都为假时选择 `@else`。只生成第一个条件为真的分支，后续条件不再求值。例如 `IsLoading` 和 `HasError` 都为真时，最终输出：

```html
<p>Loading</p>
```

`@else-if` 必须提供 `{...}` 表达式，`@else` 不填写值。也可使用等价前缀 `mk:else-if`。

可以连续声明多个 `@else-if`，也可以省略末尾的 `@else`。没有条件满足且没有 `@else` 时，不生成该分支链的内容。多个独立的 `@if` 则分别判断，可能同时生成内容。

以下写法无效，因为 `@else-if` 出现在 `@else` 之后：

```html
<!-- 错误：@else 已结束分支链 -->
<p @if="{IsLoading}">Loading</p>
<p @else>Loaded</p>
<p @else-if="{HasError}">Load failed</p>
```

以下写法同样无效，因为没有前置的 `@if`：

```html
<!-- 错误：@else-if 不能单独使用 -->
<p @else-if="{HasError}">Load failed</p>
```

`@else-if` 也支持 `template`，可以为一个分支生成多个同级元素；相邻与顺序规则保持不变。

## 一次控制多个元素

将条件写在 `template` 上，可以控制一组同级元素。`template` 自身不生成额外容器：

```html
<section>
  <template @if="{HasWeapon}">
    <h2>{{ Weapon.Name }}</h2>
    <p>Damage: {{ Weapon.Damage }}</p>
  </template>
  <p @else>No weapon equipped</p>
</section>
```

假设 `HasWeapon` 为真，武器名称为 `Sword`、伤害为 `25`，最终输出的 HTML 代码：

```html
<section>
  <h2>Sword</h2>
  <p>Damage: 25</p>
</section>
```

## 条件值的判断

`@if` 不限于布尔属性，也可以判断表达式结果：

| 值 | 判断结果 |
| --- | --- |
| `true` | 真 |
| `false`、`null`、不可用值 | 假 |
| 数值 `0` | 假 |
| 非零有限数值 | 真 |
| 空字符串 `''` | 假 |
| 非空字符串 | 真 |
| 有效对象、Array、Map、Set | 真 |

非空字符串 `'false'` 和 `'0'` 都为真；它们不是布尔值 `false` 或数值 `0`。

!!! note "空集合仍然为真"
    不要用 `@if="{Items}"` 判断集合是否包含数据。它判断的是集合值是否有效；有效的空集合也为真。应使用 `Items.Count :gt: 0` 判断是否有数据项。

对象是否存在可以显式比较 `null`：

```html
<p @if="{Weapon != null}">Weapon: {{ Weapon.Name }}</p>
<p @else>No weapon equipped</p>
```

条件表达式支持短路逻辑、比较和空值合并；完整运算规则见[绑定语法](binding-syntax.md)。HTML 中可使用 `:lt:`、`:le:`、`:gt:`、`:ge:`、`:and:`、`:or:` 代替相应符号。

## 在集合项中使用条件

将 `@if` 放在循环内容中时，条件从当前项的数据上下文读取：

```html
<ul @for="{Items}">
  <li @if="{Quantity :gt: 0}">{{ Name }} × {{ Quantity }}</li>
  <li @else>{{ Name }}: out of stock</li>
</ul>
```

假设集合包含 `Sword`（数量 `1`）和 `Potion`（数量 `0`），最终输出的 HTML 代码：

```html
<ul>
  <li>Sword × 1</li>
  <li>Potion: out of stock</li>
</ul>
```

如果不需要数量为零时的内容，直接省略 `@else`。这只控制当前项生成的 HTML，不会从业务集合中删除该项，也不会改变集合的 `Count`。

### 空集合提示

空集合不进入任何一项，因此循环内部的 `@else` 不能用作整个列表的空状态。空状态应在循环外判断：

```html
<ul @if="{Items.Count :gt: 0}" @for="{Items}">
  <li>{{ Name }}</li>
</ul>
<p @else>No items</p>
```

这里先在外层上下文判断 `Items.Count`，再遍历 `Items`。集合为空时，最终输出的 HTML 代码：

```html
<p>No items</p>
```

同一元素同时使用 `@if` 和 `@for` 时，条件在进入循环之前判断，不以每个集合项作为上下文。对每一项分别判断时，应像前例一样将 `@if` 写在循环内部。

## 条件变化与分支切换

条件依赖的属性变化后，应用需要发送对应变更通知。绑定重新判断条件，切换到相应分支，不需要重新加载 HTML。

- 条件从假变真时，生成 `@if` 分支。
- 条件从真变假时，移除 `@if` 分支；有 `@else` 时生成另一侧。
- 判断结果未改变时，保留当前分支，其中的文本等绑定仍按各自通知更新。

例如，修改 `IsReady` 需要通知 `IsReady` 变化；判断 `Items.Count` 时，集合数量变化需要相应的数量属性通知。平台接入方式请阅读各平台文档。

!!! note "分支切换会重新创建内容"
    条件绑定控制元素是否存在，不是仅修改 CSS 可见性。切换分支会移除旧内容，再次切回时创建新的内容。需要保留的输入值等业务状态应写入数据上下文，不应依赖已移除元素的临时状态。

如果只需要调整现有元素的外观或可见性，可使用相应的属性或样式绑定；条件绑定适用于根据状态选择页面结构。
