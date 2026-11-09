---
icon: bootstrap/layout-split
---

# Layout and Sizing

Layout Reference: [MDN CSS Layout Guide](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/CSS_layout){ target="_blank" rel="noopener noreferrer" }

The layout determines how elements are arranged, how space is allocated, and how content beyond the visible area is handled. HTML defines parent-child relationships, and CSS controls the layout rules for each element. The host controls in the engine provide the display dimensions available on the page.

## Page Size and Element Size

The available space on the page comes from the host controls. The `width` and `height` settings in CSS determine the size of elements, but do not change the size of the host controls. When creating interfaces, it is necessary to check the size constraints of both the page layout and the engine controls.

| Properties | Purpose |
| --- | --- |
| `width`, `height` | Set the width and height. |
| `min-width`, `min-height` | Limit the minimum size. |
| `max-width`, `max-height` | Limit the maximum size. |
| `padding` | Set the padding between the content and the border. |
| `border` | Set the border. |
| `margin` | Set the margin of the element. |

`px` represents CSS pixels. It should not be directly equivalent to the physical pixels on the final texture. The actual display is calculated based on DPI and scaling. For more details, see [UE DPI and Scaling](../ue/usage/dpi-and-scaling.md) and [Unity DPI and Scaling](../unity/usage/dpi-and-scaling.md).

## Layout Method

### Normal Document Flow

When no special layout rules are used, elements participate in the layout in the order they appear in the document. Common block-level containers are arranged in sequence, and inline text is arranged within the line and according to the available width.

```html
<div class="panel">
  <h1>Player</h1>
  <p>Level 1</p>
  <p>Ready</p>
</div>
```

This type of structure is suitable for simple titles and description panels. It is not recommended to adjust the position by adding spaces or blank lines.

### Flex Layout

The Flex Layout arranges direct child elements along the main axis, making it suitable for toolbars, horizontal information areas, and vertical panels. After setting `display: flex`, the `flex-direction` property is used to determine the direction of the main axis.

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

Titles occupy the remaining space, with the number of items on the right side displayed. `min-width: 0` allows the Flex item containing the title to shrink, but it does not automatically generate ellipsis marks.

| Properties | Purpose |
| --- | --- |
| `flex-direction` | `row` Arrange by rows,`column` Arrange by columns |
| `justify-content` | Allocate remaining space on the main axis |
| `align-items` | Set the alignment method on the cross-axis |
| `gap` | Set the spacing between sub-items |
| `flex-wrap` | Control whether sub-items are allowed to wrap |
| `flex` | Setting the growth, contraction, and base size of sub-items |

!!! note "The main axis and cross axes"
    When using `row`, the main axis is usually horizontal. After changing to `column`, the main axis becomes vertical. Therefore, `justify-content` does not always indicate horizontal alignment.

### Positioning layout

When it is necessary to place elements such as corner labels in the specified positions of the container, a container with relative positioning and a child element with absolute positioning can be used:

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

Place elements with the `item-count` class name inside `.item` to position them at the bottom right of the container. Absolute-positioned elements do not participate in the normal document flow and do not reserve space for adjacent content. For main layout, the normal flow or Flex is preferred, and positioning is used only when necessary.

## Dimensions, margins, and spacing

### Box model

The space occupied by an element includes content, inner margins, and borders. Outer margins are used to separate adjacent elements. It is recommended to set the box model explicitly on the page:

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

Under `border-box`, `320px` includes content, inner margins on the left and right sides, but does not include outer margins. If `content-box` is used, the inner margins and borders will additionally increase the external size of the element. [^box-model]

### Fixed and adaptive sizes

Fixed sizes are suitable for icons or individual controls with well-defined sizes. Content panels usually require a combination of available width and maximum width:

```css
.panel {
  width: 100%;
  max-width: 640px;
  padding: 24px;
}
```

Percentage widths are calculated based on the available size of the containing block. `height: 100%` also requires a definite height reference. It cannot be simply understood as "filling the screen automatically". When creating a vertical-filled interface, the height of the parent container and the scaling rules of child elements should be clearly defined.

### Uniform spacing

Use `padding` to set the whitespace inside the container, use `gap` to set the spacing between Flex sub-items, and use `margin` to separate areas in the regular flow. Do not add multiple sets of spacing to adjacent items simultaneously, ignoring the final combined result.

For example, `padding: 16px 24px` means that the inner margins on the top and bottom are `16px`, and on the left and right are `24px`. `margin: 0` can be used to remove the default outer margins of titles or paragraphs.

## Content overflow and scrolling

When the content exceeds the container, the display mode is controlled by `overflow`:

| Values | Meanings |
| --- | --- |
| `visible` | Allows the overflow content to be rendered outside the container |
| `hidden` | Cuts off the overflow content |
| `auto` | Enables scrolling when there is content overflow |

The scrolling area must have size constraints. If the container always grows with the content, adding `overflow: auto` will not automatically create a list with a fixed height.

```css
.item-list {
  max-height: 320px;
  overflow-y: auto;
  overflow-x: hidden;
}
```

In vertical Flex containers, when the list needs to occupy the remaining height, it is usually necessary to set `min-height: 0` as well, allowing the list to shrink below the content height.

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

The above two examples demonstrate "limiting the maximum height" and "occupying the remaining height" respectively. Choose according to the actual layout, and should not be superimposed directly without adjustment.

!!! info "Scrolling and input"
    CSS defines the scrolling area, but the actual mouse wheel and focus behavior also depend on the input interface of the host control. If the content can be displayed but not scrolled, it is necessary to check the platform input settings, rather than just modifying CSS.

## Example: Information and column surfaces

The following independent example places the title and description at the top, allowing the list to occupy the remaining height. After adding more list items, the scrolling behavior can be checked.

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

Place the segments in the `body` of the HTML and the corresponding style sheets. Synchronize the assets and preview according to the process described in [Write Your First Page](first-page.md). Check the width and height of the display areas, and add enough list items to ensure the overflow effect is achieved. If the height of the host area is less than the height of the panel, it is necessary to adjust the panel or host size.

## Layout limitations and common issues

| Phenomena | Check items |
| --- | --- |
| The total width of elements is greater than expected | Check `box-sizing`, padding, borders, and margins |
| Flex sub-items do not shrink | Check fixed sizes, `flex`, and `min-width` / `min-height` |
| Percentage-based heights are ineffective | Check whether the parent container provides a definite height |
| The content does not form a scrolling area | Check height constraints, content length, and `overflow` settings |
| Caption elements block the main text | Check the absolute positioning range and reserve necessary space for the main content |
| The page does not match the preview area. | Check the size of the host control, page constraints, and DPI scaling. |

For references to CSS semantics: [Box model sizes](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/box-sizing), [Flex item sizes](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/flex), [Overflow handling](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/overflow). These resources explain standard CSS behaviors and do not represent the full range of browser capabilities supported by plugins. It is essential to verify the display and interaction results in the target engine.

Relevant sections: [CSS Styles](css-styles.md), [DPI and Scaling](sizing-and-scaling.md), [Support and Limitations](../reference/support-and-limitations.md).

[^box-model]: The `box-sizing` property controls the calculation of sizes. It does not change whether margins take up space, nor does it change the size allocated to the page by the host control.
