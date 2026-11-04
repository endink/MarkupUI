---
icon: bootstrap/filetype-xml
---

# XHTML 支持

XHTML 使用 XML 语法编写 HTML 文档。Markup UI 的模板属性支持等价的 `@` 和 `mk:` 前缀；需要让模板符合 XML 的书写规则时，将属性名中的 `@` 改为 `mk:`。XML 的基本规则可参考 [XML 规范](https://www.w3.org/TR/REC-xml/){ target="_blank" rel="noopener noreferrer" }与 [XML 命名空间](https://www.w3.org/TR/xml-names/){ target="_blank" rel="noopener noreferrer" }。

!!! info "书写格式与解析能力"
    当前 SDK 支持 `mk:` 模板属性写法，但不会因此切换为 XML 解析模式，也不执行 XHTML DTD 验证。本章说明如何编写符合 XML 规范的 HTML 模板，不表示带有自定义属性的模板符合某个严格 XHTML DTD。

## 替换模板属性前缀

仅替换属性名开头的 `@`，属性值及表达式的含义保持不变：

| 原写法 | XML 兼容写法 |
| --- | --- |
| `@context="player"` | `mk:context="player"` |
| `@as="player"` | `mk:as="player"` |
| `@text="{Name}"` | `mk:text="{Name}"` |
| `@value="{Name}"` | `mk:value="{Name}"` |
| `@value.update="blur"` | `mk:value.update="blur"` |
| `@checked="{IsReady}"` | `mk:checked="{IsReady}"` |
| `@style.opacity="{Opacity}"` | `mk:style.opacity="{Opacity}"` |
| `@if="{IsLoading}"` | `mk:if="{IsLoading}"` |
| `@else-if="{HasError}"` | `mk:else-if="{HasError}"` |
| `@else` | `mk:else=""` |
| `@for="{Items}"` | `mk:for="{Items}"` |
| `@item-as="item"` | `mk:item-as="item"` |
| `@onclick="{Save}"` | `mk:onclick="{Save}"` |
| `@onclick.parameter="{@this}"` | `mk:onclick.parameter="{@this}"` |

同一目标不能同时使用两种前缀重复声明，例如同一元素不能同时填写 `@value` 和 `mk:value`。

!!! note "表达式中的 @ 不替换"
    `mk:` 只用于模板属性名。表达式中的 `@this`、`@item`、`@index`、`@key`、`@items` 和 `@player` 等作用域引用保留原样；文本插值仍使用 `{{ ... }}`。普通文本中的邮箱等 `@` 字符也无需替换。

## 声明命名空间

XML 文档需要为带前缀的属性声明命名空间。可在根元素上同时声明 XHTML 默认命名空间和 `mk` 前缀：

```html
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:mk="urn:markupui:template">
  <head>
    <title>Player</title>
  </head>
  <body>
    <p mk:text="{Name}">Player name</p>
  </body>
</html>
```

命名空间 URI 用于标识，不需要通过网络加载。`urn:markupui:template` 是本例使用的标识，不是下载地址。

SDK 识别固定的 `mk:` 属性前缀，不会根据命名空间 URI 自动识别任意其他前缀。将 `mk` 改成 `ui`，即使 URI 相同，也不会自动得到等价的模板指令。

!!! info "能否省略 xmlns:mk"
    能否省略 `xmlns:mk` 取决于用途：

    - **由当前 SDK 按 HTML 加载**：可以省略 `xmlns:mk`，`mk:context` 等指令仍有效。
    - **要求模板符合 XML 命名空间规范**：使用 `mk:` 属性时必须声明 `xmlns:mk`，不能省略；URI 仅用于标识，不会通过网络加载。

    因此，普通 HTML 示例无需声明，本文末尾的完整 XHTML 模板示例保留该声明。

## XML 书写规则

1. **只有一个根元素。** 完整页面使用 `html`，片段也需要一个根元素包裹全部内容。
2. **元素必须正确闭合和嵌套。** 使用 `<p>...</p>`，空元素写为 `<input ... />`、`<br />`、`<img ... />`。
3. **属性值必须加引号。** 使用 `class="panel"`，不写 `class=panel`。
4. **属性必须有值。** 使用 `checked="checked"`、`multiple="multiple"`；无条件值的分支写为 `mk:else=""`，不写裸属性 `mk:else`。
5. **名称区分大小写。** 开始标签和结束标签的拼写必须一致。HTML 元素及普通属性采用小写，业务属性名称保持应用中的实际拼写。
6. **保留字符必须转义。** 文本或属性值中的 `&` 写为 `&amp;`，`<` 写为 `&lt;`；与属性外层引号相同的引号也应使用相应实体。
7. **不要使用未声明的 HTML 命名实体。** XML 预定义实体只有 `amp`、`lt`、`gt`、`quot`、`apos`。例如不间断空格可写为 `&#160;`，不直接使用 `&nbsp;`。

### 表达式中的字符转义

可以使用运算符别名避开 `<`、`&` 等保留字符：

```html
<p mk:if="{Health :lt: MaxHealth :and: !IsDead}">Needs healing</p>
```

使用符号运算符时，按 XML 规则转义：

```html
<p mk:if="{Health &lt; MaxHealth &amp;&amp; !IsDead}">Needs healing</p>
```

两种写法含义相同。`mk:` 不用于运算符，`mk:lt`、`mk:and` 不是合法替代写法。更多运算规则见[绑定语法](binding-syntax.md)。

## 完整模板示例

下面的模板包含命名上下文、上下文别名、文本与属性绑定、样式绑定、输入写回、条件分支、集合循环、选择框和命令参数。它符合 XML 良构规则；实际数据和命令仍需由应用提供。

- 将可观察玩家对象登记为命名上下文 `player`。
- 提供 `Name`、`AvatarPath`、`Opacity`、`IsReady`、`IsLoading`、`HasError`、`IsEmpty`、`CanSave` 等属性。
- `Items` 的每项包含 `Name`、`Quantity`；`Difficulties` 的每项包含 `Id`、`Name`，`Difficulty` 保存当前选项值。
- `Save` 接收玩家对象和名称，`RemoveItem` 接收物品对象和遍历序号。命令参数应与应用的声明匹配。

```html
<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:mk="urn:markupui:template"
      lang="en" xml:lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Player panel</title>
    <link rel="stylesheet" href="styles/player.css" />
  </head>
  <body>
    <main mk:context="player" mk:as="player">
      <header mk:style.opacity="{Opacity}">
        <img mk:src="{AvatarPath}" alt="Player avatar" />
        <h1 mk:text="{Name}">Player name</h1>
      </header>

      <section>
        <label>
          Name
          <input type="text"
                 mk:value="{Name}"
                 mk:value.update="blur" />
        </label>
        <label>
          <input type="checkbox" mk:checked="{IsReady}" />
          Ready
        </label>
        <label>
          Difficulty
          <select mk:value="{Difficulty}" mk:for="{Difficulties}">
            <option mk:value="{Id}">{{ Name }}</option>
          </select>
        </label>
      </section>

      <p mk:if="{IsLoading}">Loading</p>
      <p mk:else-if="{HasError}">Load failed</p>
      <p mk:else-if="{IsEmpty}">No items</p>
      <section mk:else="">
        <h2>Inventory</h2>
        <p>Total: {{ Items.Count }}</p>
        <ul mk:for="{Items}" mk:item-as="item" mk:items-as="inventory">
          <li>
            <span>{{ @item.Name }} × {{ Quantity }}</span>
            <span mk:if="{Quantity :le: 0}">Out of stock</span>
            <button type="button"
                    mk:onclick="{@player.RemoveItem}"
                    mk:onclick.parameter="{@item, @index}">
              Remove
            </button>
          </li>
        </ul>
      </section>

      <button type="button"
              mk:disabled="{!CanSave}"
              mk:onclick="{Save, parameter={@this, Name}}">
        Save
      </button>
    </main>
  </body>
</html>
```
