---
icon: bootstrap/exclamation-triangle
---

# Known Issues

The issues below can cause pages to render differently from a browser. The results can vary with the platform, display scale, and page layout. Check the UI on the target platform before release.

> Markup UI uses [Blitz](https://github.com/DioxusLabs/blitz){ target="_blank" rel="noopener noreferrer" } to parse HTML. Rendering issues in Blitz require an upstream fix, followed by an update and verification in Markup UI.

## Thin Borders Can Lose an Edge

In some layouts at 125% or 150% Windows display scaling, a `1px` border around a rounded panel or input field can lose an edge.

```css
.panel {
  border: 1px solid #55b7ff;
  border-radius: 12px;
}
```

Check the result at different display scales and try a thicker border if needed. [Upstream issue #837](https://github.com/DioxusLabs/blitz/issues/837){ target="_blank" rel="noopener noreferrer" }

## 3D Transforms May Fail

`rotateX()`, `rotateY()`, and perspective can render incorrectly. Combining a 2D transform and a 3D rotation in the same `transform` can also cause the entire transform to fail.

```css
.card {
  transform: translate(30px, -10px) rotateY(42deg);
}
```

Use 2D transforms when you need consistent rendering, and verify the result on the target platform. This issue has been observed on Windows. Behavior on other platforms is unverified.

## Rounded Corners and Image Clipping Can Differ

When an image exceeds its container and a negative margin shifts its position, the combination of `overflow: hidden` and `border-radius` can clip the image incorrectly. The image position and the rounded corners on the right can differ from the browser result.

```css
.frame {
  overflow: hidden;
  border-radius: 16px;
}

.frame img {
  width: 240px;
  margin-left: -20px;
}
```

Check the image position and all four corners in the actual page. This issue was observed in a specific preview environment and can vary across platforms.

## Backdrop Blur Can Extend Beyond Rounded Corners

When `border-radius` and `backdrop-filter` are used together, the backdrop blur can extend into the rectangular area outside the rounded corners.

```css
.glass {
  border-radius: 24px;
  backdrop-filter: blur(12px);
}
```

This issue was observed in a specific preview environment. Check the edges on the target platform when using backdrop blur.

## Gradient Color Space May Have No Effect

When a gradient specifies an interpolation color space with `in oklab` or `in srgb-linear`, the result can differ from the browser. Both settings can also produce similar results.

```css
.panel {
  background: linear-gradient(90deg in oklab, red, blue);
}
```

If the color transition is important to the design, verify it on the target platform. This issue was observed in a specific preview environment.

## SVG Rendering Limitations

### Tiled SVG Backgrounds

When CSS uses SVG as a background, `background-repeat: repeat` can display a single copy of the image instead of tiling it.

```css
.pattern {
  background-image: url("pattern.svg");
  background-size: 40px 40px;
  background-repeat: repeat;
}
```

Consider using a bitmap background and check it on the target platform. This issue was observed in a specific preview environment. See [Images and Fonts](../ue/resources/images-and-fonts.md) for external SVG asset support in Unreal Engine.

### Strokes in Inline SVG

When an external stylesheet sets properties such as `stroke` on a parent element of an inline SVG, child paths can fail to render.

```css
.icon {
  fill: none;
  stroke: white;
  stroke-width: 2;
}
```

```html
<svg class="icon" viewBox="0 0 24 24">
  <path d="M2 12H22"></path>
</svg>
```

If a stroke is missing, verify the SVG on the target platform. This issue was observed in a specific preview environment.

### Wide Strokes on Circles

An SVG circle can display a small hole at the center when its stroke width exceeds its diameter.

```html
<svg viewBox="0 0 120 120">
  <circle cx="60" cy="60" r="12" fill="none"
          stroke="#ef8354" stroke-width="32"></circle>
</svg>
```

Use a fill for a solid circle and check the result on the target platform.
