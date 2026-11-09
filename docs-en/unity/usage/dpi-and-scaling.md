---
icon: bootstrap/aspect-ratio
---

# DPI and Scaling

`MarkupHtmlElement` updates the physical rendering resolution of the page based on the UI Toolkit content area, panel pixel density, and element transform.

## Calculate Viewport Size

The layout width and height of `MarkupHtmlElement` use UI Toolkit logical points. The plugin reads the content dimensions from `contentRect` and calculates the rendering density from the panel's `scaledPixelsPerPoint` and the accumulated element transform.

```text
effective scale = panel pixel density × max(horizontal scale, vertical scale)
physical size = round(logical content size × effective scale)
```

Scaling an element or an ancestor affects rendering density through the accumulated transform. For non-uniform scaling, the plugin uses the larger axis scale for both dimensions to maintain sufficient sampling density in both display directions.

The plugin updates size and density when the element is attached, when layout changes, and during ongoing viewport checks. A monitor DPI change can therefore trigger a check even when the element's width and height stay the same.

## Create an Offscreen Viewport Manually

When using `MarkupUIViewPort` directly, specify the width and height in physical pixels and supply the matching `deviceScale`. For example, a logical area of `800 × 600` at a scale of `2` requires a physical viewport of `1600 × 1200`. The host performs this conversion automatically for `MarkupHtmlElement`.

## Page Rendering and Pixel Alignment

The plugin places the page texture using the current panel density and element transform. It applies the frame's generation scale only once. For positive, axis-aligned transforms without rotation or skew, the plugin adjusts the page origin to the nearest physical pixel. It preserves explicit rotation and skew.

After a viewport change, the plugin places and clips the previous frame using the current coordinates until a new frame is ready. The previous frame retains its rendered size.

## Check the Display

1. Check the host control's actual logical size and effective scale.
2. Compare a `100 × 100px` color block and fixed-size text at several scales.
3. Resize the window and check text wrapping, scrolling, and clipping.
4. Check the final page position and source image resolution after ruling out additional CSS or ancestor scaling.

See also [DPI and Scaling](../../authoring/sizing-and-scaling.md) and [Layout and Sizing](../../authoring/layout-and-styles.md).
