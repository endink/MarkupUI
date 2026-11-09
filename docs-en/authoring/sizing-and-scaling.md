---
icon: bootstrap/aspect-ratio
---

# DPI and Scaling

Markup UI lays out pages in logical units. The platform host calculates the physical rendering resolution from the actual layout size and effective scale.

!!! note "Host Controls"
    A host control displays an HTML page inside the engine UI. The space allocated to the control determines the display area available to the page.

    - **Unreal Engine** uses `MarkupUIWidget` in UMG.
    - **Unity** uses `MarkupHtmlElement` in UI Toolkit.

## Logical Size and Physical Resolution

CSS `px` is a logical unit. With uniform scaling, multiply the logical size by the effective scale and round to obtain the physical size in pixels.

For example, a logical display area of `800 × 600` at an effective scale of `2` corresponds to a physical resolution of `1600 × 1200`. A page font size of `16px` scales automatically.

## Platform Details

The host on each platform determines the DPI, effective scale, and presentation behavior.

- [Unreal Engine DPI and Scaling](../ue/usage/dpi-and-scaling.md) covers accumulated layout scale, the project DPI curve, and Render Transform.
- [Unity DPI and Scaling](../unity/usage/dpi-and-scaling.md) covers panel pixel density, element scaling, and offscreen viewports.

## Layout and Display Quality

Changing the logical display area can cause text to wrap and trigger a new layout. Increasing pixel density changes the rendering resolution. Enlarging the final image can introduce resampling, and the detail available in a source image remains limited by its original resolution.

Font size specifies the typographic scale. Visible glyph height depends on the typeface. Choose images with enough resolution for the target pixel density and set the viewport to an appropriate resolution.

See [Layout and Sizing](layout-and-styles.md) for page dimensions, percentages, and layout constraints.
