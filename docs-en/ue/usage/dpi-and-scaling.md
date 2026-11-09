---
icon: bootstrap/aspect-ratio
---

# DPI and Scaling

`MarkupUIWidget` Use the local sizing and cumulative layout scaling provided by Slate to determine the logical space of the HTML page relative to its physical rendering resolution.

## viewport size calculation

The Markup UI control obtains local dimensions and cumulative layout scaling from Slate geometry:

```text
effective scale = accumulated Slate layout scale
physical size = round(widget local size × effective scale)
```

!!! note "Cumulative layout scaling"
    Cumulative layout scaling is the overall scaling ratio used by Slate to convert the local layout coordinates of a control to absolute coordinates. It includes the scaling inherited from the parent layout and combined together. It is not just the scaling set individually by the current control.

    For example, if there are two levels of scaling in the parent layout, namely `1.5` and `0.8`, and there is no other layout scaling, the total scaling ratio is `1.5 × 0.8 = 1.2`. For a control with local dimensions of `800 × 600`, the corresponding physical resolution of the page is `960 × 720`.

    The plugin directly reads the calculated total proportions in the Slate geometry, eliminating the need for users to multiply values step by step. **Render Transform** does not belong to this layout scaling mechanism.

The plugin uses the physical dimensions along with the scaling values for the page viewport. UMG’s layout and DPI settings affect the page through the host geometry, eliminating the need to configure the same proportions repeatedly in HTML.

#### The DPI curve in the project settings

When displaying the UMG interface through a standard game viewport, the settings in **Project Settings → User Interface → DPI Scaling** also affect the parent layout, thereby influencing `MarkupUIWidget`:

- **DPI Scale Rule**: Select the rule used to calculate the proportions. For example, **Shortest Side** uses the smaller of the game viewport’s width and height, rather than the HTML page’s own width and height.
- **DPI Curve**: Maps the selected resolution value from the rule to the UI scaling ratio.
- **Application Scale**: Applies an additional overall UI scaling factor to the calculated result.

For example, if the viewport is `1920 × 1080`, and the rule is **Shortest Side**, then the value is taken at the `1080` position of the curve. If the curve value is `1.25` and **Application Scale** is `1.2`, the result of UI scaling in the project UI is `1.5`. This is not a parameter that is directly assigned to the plugin. The final scale still depends on the Slate geometry received by the control.

For interfaces that cover the same physical area, when the UI scaling increases, the logical size will decrease accordingly. For example, if the physical area is `1200 × 900` and the final effective scaling is `1.5`, the logical layout area would be approximately `800 × 600`. Therefore, adjusting the curve may also change the text size, line wrapping, and layout, rather than just improving clarity.

!!! note "The applicable range of the DPI curve"
    The Markup UI does not read the curve separately and then apply scaling. Instead, it uses the cumulative layout scaling calculated by the host. The UE game viewport will handle the issue of repeated application of platform DPI. It is not possible to simply multiply the system scaling, curve value, and all UI settings together manually. The Slate window, off-screen preview, or asset editor may not necessarily use the DPI curve of the game viewport. These should be judged based on their respective host geometries.

**Scale to Fit** Calculate based on the design resolution and viewport ratio.**Custom** Use custom rules. These two methods do not follow the standard sampling process mentioned above. For detailed instructions, see... [UE DPI Scaling](https://dev.epicgames.com/documentation/en-us/unreal-engine/dpi-scaling-in-unreal-engine){ target="_blank" rel="noopener noreferrer" }.

**Render Transform** This is a final rendering transformation that is still retained, but it is not equivalent to the cumulative layout scaling mentioned above. Scaling the rendered page using Render Transform may introduce texture resampling. It should not be considered as a setting that automatically improves the page's rendering resolution.

## Page rendering and pixel alignment

The page textures have been rendered at the physical resolution. During rendering, they are first scaled to the local size according to the current Slate layout, and then the explicit rendering transformations are preserved. Do not apply the DPI recorded in the frame again. The pixel alignment of the page follows the Slate pixel snapping settings. Disabling snapping or additional scaling may lead to resampling.

When the viewport changes but the new frame has not been published, the old images are placed and cropped according to the current coordinates, without being forced to stretch to the new control size.

## Check the display results

1. Confirm that the actual logical size of the host controls matches the effective scaling.
2. Use color blocks of `100 × 100px` and fixed-sized text to compare the display results under different zoom levels.
3. Adjust the window size to check for line breaking, scrolling, and cropping issues.
4. Exclude any CSS or parent-level scaling adjustments. Check the final position of the page and the resolution of the image source.

Relevant instructions: [Common DPI and Scaling](../../authoring/sizing-and-scaling.md), [Layout and Sizing](../../authoring/layout-and-styles.md).
