---
icon: bootstrap/layout-split
---

# 布局与尺寸

布局参考：[MDN CSS 布局指南](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout){ target="_blank" rel="noopener noreferrer" }。

布局决定元素如何排列、分配空间以及处理超出显示区域的内容。HTML 定义父子关系，CSS 控制每个元素的布局规则；引擎中的宿主控件则提供页面可用的显示尺寸。

## 页面尺寸与元素尺寸

页面可用空间来自宿主控件。CSS 中的 `width` 和 `height` 设置元素尺寸，不会修改宿主控件的大小。制作界面时，应同时检查页面布局和引擎控件的尺寸约束。

| 属性 | 用途 |
| --- | --- |
| `width`、`height` | 设置宽度和高度 |
| `min-width`、`min-height` | 限制最小尺寸 |
| `max-width`、`max-height` | 限制最大尺寸 |
| `padding` | 设置内容与边框之间的内边距 |
| `border` | 设置边框 |
| `margin` | 设置元素外边距 |

`px` 表示 CSS 像素，不应直接等同于最终纹理上的物理像素；实际显示由宿主按 DPI 与缩放换算，详见 [UE DPI 与缩放](../ue/usage/dpi-and-scaling.md)及 [Unity DPI 与缩放](../unity/usage/dpi-and-scaling.md)。

## 布局方式

### 普通文档流

未使用特殊布局规则时，元素按文档顺序参与布局。常见的块级容器依次排列，行内文字在行内排列并按可用宽度换行。

```html
<div class="panel">
  <h1>Player</h1>
  <p>Level 1</p>
  <p>Ready</p>
</div>
```

这类结构适合简单的标题与说明面板。不应依靠添加空格或空行调整位置。

### Flex 布局

Flex 布局按主轴排列直接子元素，适合工具栏、横向信息区域和纵向面板。设置 `display: flex` 后，通过 `flex-direction` 选择主轴方向。

```html
<div class="toolbar">
  <span class="toolbar-title">Inventory</span>
  <span>12 items</span>
</div>
```

```css
.toolbar {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
}

.toolbar-title {
  flex: 1 1 0;
  min-width: 0;
}
```

标题占用剩余空间，右侧显示物品数量。`min-width: 0` 允许标题所在 Flex 项缩小，但不自动产生省略号。

| 属性 | 用途 |
| --- | --- |
| `flex-direction` | `row` 按行排列，`column` 按列排列 |
| `justify-content` | 分配主轴上的剩余空间 |
| `align-items` | 设置交叉轴上的对齐方式 |
| `gap` | 设置子项之间的间距 |
| `flex-wrap` | 控制子项是否允许换行 |
| `flex` | 设置子项的增长、收缩和基础尺寸 |

!!! note "主轴与交叉轴"
    使用 `row` 时，主轴通常为水平方向；改为 `column` 后，主轴变为垂直方向。因此，`justify-content` 并不始终表示水平对齐。

### 定位布局

需要将角标等元素放在容器的指定位置时，可使用相对定位的容器与绝对定位的子元素：

```css
.item {
  position: relative;
  width: 96px;
  height: 96px;
}

.item-count {
  position: absolute;
  right: 8px;
  bottom: 8px;
}
```

将带有 `item-count` 类名的元素放在 `.item` 内部，即可将其定位在容器右下方。绝对定位元素不参与普通文档流，不会为相邻内容预留空间；主体布局优先使用普通流或 Flex，局部叠放再使用定位。

## 尺寸、边距与间距

### 盒模型

元素占用的空间包括内容、内边距和边框，外边距用于分隔相邻元素。建议在页面中明确设置盒模型：

```css
* {
  box-sizing: border-box;
}

.panel {
  width: 320px;
  padding: 24px;
  border: 1px solid #55b7ff;
}
```

在 `border-box` 下，`320px` 包含内容、左右内边距和边框，不包含外边距。若采用 `content-box`，内边距和边框会额外增加元素的外部尺寸。[^box-model]

### 固定与自适应尺寸

固定尺寸适用于尺寸明确的图标或局部控件；内容面板通常需要结合可用宽度和最大宽度：

```css
.panel {
  width: 100%;
  max-width: 640px;
  padding: 24px;
}
```

百分比宽度依据包含块的可用尺寸计算。`height: 100%` 也需要可确定的高度参照，不能简单理解为“自动填满屏幕”。制作纵向填充界面时，应明确父容器的高度和子元素的伸缩规则。

### 统一间距

使用 `padding` 设置容器内部留白，使用 `gap` 设置 Flex 子项间距，使用 `margin` 分隔普通流中的区域。不要同时在相邻两项添加多组间距，却忽略最终叠加结果。

例如，`padding: 16px 24px` 表示上下内边距为 `16px`，左右为 `24px`；`margin: 0` 可用于清除标题或段落的默认外边距。

## 内容溢出与滚动

当内容大于容器时，通过 `overflow` 控制显示方式：

| 值 | 含义 |
| --- | --- |
| `visible` | 允许溢出内容绘制到容器之外 |
| `hidden` | 裁剪溢出内容 |
| `auto` | 在内容溢出时允许滚动 |

滚动区域必须存在尺寸约束。如果容器始终随内容增高，就不会因为添加 `overflow: auto` 而自动形成固定高度列表。

```css
.item-list {
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
}
```

在纵向 Flex 容器中，列表需要占用剩余高度时，通常还需为其设置 `min-height: 0`，允许列表缩小到内容高度以下：

```css
.panel {
  display: flex;
  flex-direction: column;
  height: 480px;
}

.item-list {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
}
```

以上两个片段分别展示“限制最大高度”和“占用剩余高度”，按实际布局选择，不应未经调整直接叠加。

!!! info "滚动与输入"
    CSS 定义滚动区域，实际鼠标滚轮和焦点行为还取决于宿主控件的输入接入。若内容可以显示但不能滚动，应同时检查平台输入设置，而不只修改 CSS。

## 示例：信息与列表面板

下面的独立示例将标题与说明放在顶部，让列表占用剩余高度。增加列表项后，可检查滚动行为。

```html
<main class="inventory">
  <h1>Inventory</h1>
  <p>Available items</p>
  <div class="items">
    <div class="item-row">Potion</div>
    <div class="item-row">Shield</div>
    <div class="item-row">Key</div>
  </div>
</main>
```

```css
* { box-sizing: border-box; }
body { margin: 0; padding: 16px; }

.inventory {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  max-width: 640px;
  height: 360px;
  padding: 20px;
  background-color: #1b2a38;
  color: #edf4fa;
}

.inventory h1, .inventory p { margin: 0; }

.items {
  flex: 1 1 0;
  min-height: 0;
  overflow-y: auto;
}

.item-row {
  padding: 12px;
  border-bottom: 1px solid #55b7ff;
}
```

将片段分别放入 HTML 的 `body` 与对应样式表，按[编写第一个页面](first-page.md)的流程同步资产并预览。检查宽窄两种显示区域，并增加足够多的列表项确认溢出效果；若宿主区域高度小于面板高度，还需要调整面板或宿主尺寸。

## 布局限制与常见问题

| 现象 | 检查项 |
| --- | --- |
| 元素总宽度大于预期 | 检查 `box-sizing`、内边距、边框和外边距 |
| Flex 子项不收缩 | 检查固定尺寸、`flex` 和 `min-width` / `min-height` |
| 百分比高度无效 | 检查父容器是否提供可确定的高度 |
| 内容未形成滚动区域 | 检查高度约束、内容长度及 `overflow` |
| 角标遮挡正文 | 检查绝对定位范围，并为主体内容保留必要空间 |
| 页面与预览区域不匹配 | 检查宿主控件尺寸、页面约束和 DPI 缩放 |

CSS 语义参考：[盒模型尺寸](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/box-sizing)、[Flex 项尺寸](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/flex)、[溢出处理](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow)。这些资料解释标准 CSS 行为，不代表完整浏览器能力在插件中的支持承诺；最终应在目标引擎中检查显示和交互结果。

相关章节：[CSS 样式](css-styles.md)、[DPI 与缩放](sizing-and-scaling.md)、[支持范围与限制](../reference/support-and-limitations.md)。

[^box-model]: `box-sizing` 控制尺寸的计算范围，不改变外边距是否占用空间，也不改变宿主控件分配给页面的尺寸。
