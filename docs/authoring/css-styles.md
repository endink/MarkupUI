---
icon: bootstrap/palette
---

# CSS 样式

CSS 语法与属性参考：[MDN CSS 文档](https://developer.mozilla.org/en-US/docs/Web/CSS){ target="_blank" rel="noopener noreferrer" }。

CSS 用于设置 HTML 元素的布局与外观。一条样式规则由选择器和声明块组成；选择器确定作用对象，声明指定颜色、字体、尺寸等属性。

## 引入样式表

### 外部样式表

在 HTML 的 `head` 中使用 `link` 引入 CSS：

```html
<link rel="stylesheet" href="../styles/main.css">
```

`href` 相对于 HTML 文件的位置解析。例如，`pages/index.html` 使用上述路径引用同一`资产目录`下的 `styles/main.css`。CSS 文件需要与 HTML 一起同步到工程资产中。

较大的界面可将共用规则和页面规则拆分为多个样式表：

```html
<link rel="stylesheet" href="../styles/common.css">
<link rel="stylesheet" href="../styles/inventory.css">
```

先加载共用规则，再加载页面规则，便于在优先级相同的情况下覆盖具体属性；加载顺序不是决定最终样式的唯一条件。

### 文档内样式与行内样式

验证少量规则时，可将 CSS 放在 `head` 的 `style` 元素中：

```html
<style>
  .panel {
    color: #edf4fa;
    background-color: #1b2a38;
  }
</style>
```

也可用元素的 `style` 属性设置局部样式：

```html
<p style="color: #55b7ff;">Ready</p>
```

重复使用的规则优先放在外部 CSS 中，通过类名应用。大量行内样式不便于统一修改，也容易增加覆盖关系的复杂度。

## 选择器与样式规则

```css
.panel {
  padding: 24px;
  color: #edf4fa;
  background-color: #1b2a38;
}
```

`.panel` 是选择器，花括号内每条声明使用 `属性: 值;` 的格式。属性名和值之间用冒号分隔，声明之间用分号分隔。

| 选择器 | 示例 | 匹配对象 |
| --- | --- | --- |
| 元素选择器 | `p` | 所有 `p` 元素 |
| 类选择器 | `.panel` | `class` 中包含 `panel` 的元素 |
| ID 选择器 | `#inventory` | `id="inventory"` 的元素 |
| 后代选择器 | `.panel p` | `.panel` 内任意层级的 `p` 元素 |
| 子元素选择器 | `.panel > p` | `.panel` 的直接子元素 `p` |
| 选择器列表 | `h1, h2` | 匹配任一选择器的元素 |

多个类名可组合表达基础样式和局部变化：

```html
<div class="panel compact">Inventory</div>
```

```css
.panel { padding: 24px; }
.panel.compact { padding: 12px; }
```

`.panel.compact` 匹配同时具有这两个类名的同一个元素；`.panel .compact` 则匹配 `.panel` 内部具有 `compact` 类名的后代元素，两者含义不同。

## 层叠、优先级与继承

### 多条规则如何共同生效

多个规则可同时匹配一个元素，最终样式按属性分别确定。修改 `color` 不会自动覆盖另一条规则中的 `padding`。

```css
.status {
  color: #edf4fa;
  padding: 8px;
}

.status {
  color: #55b7ff;
}
```

在上述相同条件下，后面的 `color` 生效，`padding` 仍为 `8px`。

当规则声明相互冲突时，CSS 会综合声明来源、重要性和选择器优先级等因素。对同一来源、同一层中的普通规则，通常 ID 选择器优先于类选择器，类选择器优先于元素选择器；优先级相同时，再比较声明顺序。行内普通样式通常优先于样式表中的普通规则。

!!! tip "先检查匹配规则"
    样式未生效时，先检查资源是否加载、选择器是否匹配及后续是否存在覆盖规则。不要直接用大量 `!important` 解决所有样式冲突。

完整规则见 [MDN 选择器优先级](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity){ target="_blank" rel="noopener noreferrer" }。

### 子元素继承哪些样式

`color`、`font-family` 等属性通常从父元素继承；`margin`、`padding`、`border` 和背景色通常不会继承。

```css
body {
  color: #edf4fa;
  font-family: sans-serif;
}

.secondary {
  color: #b7c5d3;
}
```

没有单独指定文字颜色的内容使用继承的颜色，`.secondary` 中的文字使用自己的颜色。子元素本身已有匹配声明时，不能仅通过提高父元素选择器的优先级来覆盖它。

## 颜色、背景与边框

### 文字与背景

```css
.panel {
  color: #edf4fa;
  background-color: #1b2a38;
}

.status {
  color: #55b7ff;
}
```

`color` 设置文字颜色，`background-color` 设置元素背景。颜色可使用十六进制形式，也可使用 `rgb()` 或 `rgba()`：

```css
.overlay {
  background-color: rgba(0, 0, 0, 0.5);
}
```

这里的透明度只属于背景颜色；`opacity` 则作用于整个元素及其子内容。设置 `opacity: 0.5` 会同时降低文字、图片和背景的可见程度。

!!! note "透明背景不等于透明输出"
    CSS 背景透明表示该元素不绘制不透明背景，并不保证页面绘制目标或引擎中的最终合成结果透明。透明显示还取决于平台的绘制与呈现方式。

### 边框与圆角

```css
.panel {
  border: 1px solid #55b7ff;
  border-radius: 12px;
}
```

`border` 同时设置边框宽度、样式和颜色。边框参与盒模型尺寸计算，相关说明见[布局与尺寸](layout-and-styles.md)。

### 文字样式

```css
.title {
  font-size: 28px;
  font-weight: bold;
  line-height: 1.3;
}

.description {
  font-size: 16px;
  line-height: 1.5;
}
```

无单位的 `line-height` 表示字号的倍数，不是固定像素值。DPI 换算见 [DPI 与缩放](sizing-and-scaling.md)。

## 图片与字体

各平台处理图片与字体的方式不同，请参考各平台文档。

## 样式中的资源路径

CSS 中通过 `url()` 引用的资源，以 CSS 文件自身的位置为相对路径起点：

```css
.banner {
  background-image: url("../images/banner.png");
}
```

若规则位于 `styles/main.css`，该路径指向同一`资产目录`下的 `images/banner.png`。不要因为 HTML 位于 `pages/` 而改用相对于 HTML 的路径。

完整路径规则见[资源路径](resource-paths.md)。

## 支持的 CSS 属性

MDN 描述标准 Web 平台的 CSS 能力，不是 Markup UI 的支持清单。实际效果还取决于页面解析、布局、绘制及平台输入接入；不能仅因语法有效就认定所有视觉效果或交互均已实现。

本节示例使用常见的文本、颜色、背景和边框属性。完整支持状态应以[支持范围与限制](../reference/support-and-limitations.md)及目标平台验证结果为准。

## 检查样式结果

1. 检查 HTML 中的样式表路径，确认 CSS 及其依赖资源已同步。
2. 确认元素的 `class`、`id` 与选择器一致。
3. 检查声明中的冒号、分号、花括号和属性值。
4. 检查其他规则与行内样式是否覆盖当前属性。
5. 修改后重新同步资产并加载页面，在引擎预览中确认结果。

常见的排版问题见[布局与尺寸](layout-and-styles.md)；一个可直接使用的外部样式表示例见[编写第一个页面](first-page.md)。
