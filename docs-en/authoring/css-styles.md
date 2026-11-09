---
icon: bootstrap/palette
---

# CSS Styles

CSS syntax and property reference: [MDN CSS documentation](https://developer.mozilla.org/en-US/docs/Web/CSS){ target="_blank" rel="noopener noreferrer" }.

CSS is used to set the layout and appearance of HTML elements. A style rule consists of a selector and a declaration block. The selector specifies the target object, and the declaration specifies properties such as color, font, and size.

## Importing style sheets

### External style sheets

Introducing CSS using the `link` tag in the `head` of HTML:

```html
<link rel="stylesheet" href="../styles/main.css">
```

`href` resolves relative to the location of the HTML file. For example, `pages/index.html` uses the above path to reference `styles/main.css` from the same `Asset Directory`. The CSS file needs to be synchronized with HTML in the project assets.

For larger interfaces, common rules and page rules can be split into multiple style sheets:

```html
<link rel="stylesheet" href="../styles/common.css">
<link rel="stylesheet" href="../styles/inventory.css">
```

First, load the common rules, and then load the page-specific rules. This makes it easier to override specific properties when the priorities are the same. The loading order is not the only factor that determines the final style.

### Styles within the document and styles within lines

When verifying a small number of rules, CSS can be placed in the `style` element of the `head`:

```html
<style>
  .panel {
    color: #edf4fa;
    background-color: #1b2a38;
  }
</style>
```

Local styles can also be set using the `style` property of elements:

```html
<p style="color: #55b7ff;">Ready</p>
```

Rules that are reused should be placed in the external CSS, and applied through class names. A large number of inline styles is difficult to modify uniformly, and it also increases the complexity of overlapping relationships.

## Selectors and style rules

```css
.panel {
  padding: 24px;
  color: #edf4fa;
  background-color: #1b2a38;
}
```

`.panel` It is a selector, used for each declaration within the parentheses. `property: value;` The format is as follows: the attribute name and value are separated by a colon, and declarations are separated by semicolons.

| Selector | Example | Matching objects |
| --- | --- | --- |
| Element selector | `p` | All `p` elements |
| Class selector | `.panel` | `class` It contains `panel` The elements |
| ID selector | `#inventory` | The element with `id="inventory"` |
| Descendant selector | `.panel p` | `p` elements at any level within `.panel` |
| Child element selector | `.panel > p` | `p` elements that are direct children of `.panel` |
| Selector list | `h1, h2` | Elements matching any selector |

Multiple class names can be combined to express the base style and local variations:

```html
<div class="panel compact">Inventory</div>
```

```css
.panel { padding: 24px; }
.panel.compact { padding: 12px; }
```

`.panel.compact` It matches the same element that has both class names;`.panel .compact` Then it matches `.panel` It has within itself `compact` The descendant elements of the class name have different meanings.

## Stacking, priority, and inheritance

### How multiple rules can take effect together

Multiple rules can match a single element at the same time, and the final style is determined by the properties respectively. Changing `color` will not automatically override `padding` in another rule.

```css
.status {
  color: #edf4fa;
  padding: 8px;
}

.status {
  color: #55b7ff;
}
```

Under the same conditions as above, the `color` property takes effect, while the `padding` property remains at `8px`.

When rule declarations conflict with each other, CSS takes into account factors such as the source of the declaration, its importance, and the selector's priority. For ordinary rules from the same source within the same layer, typically, ID selectors have priority over class selectors, and class selectors have priority over element selectors. When the priorities are the same, the declaration order is considered. Inline styles usually have priority over ordinary rules in the style sheet.

!!! tip "First, check the matching rules"
    When the styles are not effective, first check whether the resources have been loaded, whether the selectors match, and whether there are any override rules in the future. Do not use a large number of `!important` to resolve all style conflicts.

For the complete rules, refer to [MDN Selector Priorities](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Cascade/Specificity){ target="_blank" rel="noopener noreferrer" }.

### What styles do child elements inherit from?

Properties such as `color` and `font-family` usually inherit from the parent element. Properties like `margin`, `padding`, `border`, and background color usually do not inherit.

```css
body {
  color: #edf4fa;
  font-family: sans-serif;
}

.secondary {
  color: #b7c5d3;
}
```

For content that does not specify a text color individually, the inherited color is used. The text within `.secondary` uses its own color. When a child element already has a matching declaration, it cannot be overridden simply by increasing the priority of the parent element's selector.

## Colors, backgrounds, and borders

### Text and backgrounds

```css
.panel {
  color: #edf4fa;
  background-color: #1b2a38;
}

.status {
  color: #55b7ff;
}
```

The `color` property sets the text color, while `background-color` sets the background of the element. Colors can be specified in hexadecimal format, or using `rgb()` or `rgba()`:

```css
.overlay {
  background-color: rgba(0, 0, 0, 0.5);
}
```

The transparency here only applies to the background color; `opacity` affects the entire element and its child content. Setting `opacity: 0.5` reduces the visibility of both text, images, and backgrounds.

!!! note "A transparent background does not equal a transparent output"
    In CSS, a transparent background means that the element does not draw a transparent background. This does not guarantee that the final composite result in the page's rendering target or engine will be transparent. Transparent display also depends on the platform's rendering and presentation methods.

### Border and corners

```css
.panel {
  border: 1px solid #55b7ff;
  border-radius: 12px;
}
```

`border` allows you to set the width, style, and color of the border. The border is involved in calculating the box model size. For more details, see [Layout and Sizing](layout-and-styles.md).

### Text style

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

`line-height`, which has no unit, represents a multiple of the font size, not a fixed pixel value. For DPI conversion, see [DPI and Scaling](sizing-and-scaling.md).

## Images and fonts

Different platforms handle images and fonts differently. Please refer to the documentation for each platform.

## Resource paths in styles

In CSS, resources referenced through `url()` use the location of the CSS file itself as the relative path starting point.

```css
.banner {
  background-image: url("../images/banner.png");
}
```

If a rule is located in `styles/main.css`, this path points to `images/banner.png` within the same `Asset Directory`. Do not use a path relative to the HTML, even if the HTML is located in `pages/`.

For the complete path rules, see [Resource Paths](resource-paths.md).

## Supported CSS properties

The MDN describes the CSS capabilities of the standard Web platform. It is not a list of Markup UI supports. The actual effects also depend on page parsing, layout, rendering, and platform input access. It cannot be assumed that all visual effects or interactions are implemented just because the syntax is valid.

This section uses common text, color, background, and border properties. The full support status should be based on the results of [Support and Limitations](../reference/support-and-limitations.md) and verification on target platforms.

## Check the style results

1. Check the path of the style sheets in the HTML code to ensure that the CSS and its dependent resources have been synchronized.
2. Verify that the `class` and `id` of the elements match the selectors.
3. Inspect the colon, semicolon, curly braces, and property values in the declarations.
4. Check whether other rules and inline styles override the current properties.
5. After making the modifications, synchronize the assets again and load the page. Verify the results in the engine preview.

For common typography issues, refer to [Layout and Sizing](layout-and-styles.md). For an example of an externally used style sheet, see [Write Your First Page](first-page.md).
