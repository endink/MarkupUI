---
icon: bootstrap/images
---

# Images and Fonts

In Unreal Engine, pages load images and fonts from the `Asset Directory`. First, place the files in the `Design-Time Directory` and synchronize them. Alternatively, import the files from the `Asset Directory`, and then reference the logical paths of these files in HTML and CSS.

## Prepare Images and Fonts

For example, place the following files in the `Design-Time Directory`:

```text
pages/
  index.html
styles/
  main.css
images/
  avatar.png
fonts/
  interface.ttf
```

After synchronizing using **Markup UI → Import Design Folder**, the directory structure remains intact. When using the default asset naming rules of the plugin, each file generates the following assets:

| Design Files | Imported Assets | Asset type |
| --- | --- | --- |
| `pages/index.html` | `pages/HTML_index` | `UHtmlDocument` |
| `styles/main.css` | `styles/CSS_main` | `UHtmlStyleSheet` |
| `images/avatar.png` | `images/T_avatar` | `UTexture2D` |
| `fonts/interface.ttf` | `fonts/interface` | `UFontFace` |

Supported synchronization formats can be found in [Working Directories](working-directories.md).

## Image reference and display dimensions

HTML uses `img` to reference images:

```html
<img src="/images/avatar.png" alt="Player avatar">
```

CSS can also be used to reference images. The relative paths below are calculated from the location of `styles/main.css`:

```css
/* styles/main.css */
.avatar {
  width: 96px;
  height: 96px;
  background-image: url("../images/avatar.png");
}
```

`/images/avatar.png` is searched from the globally configured `Asset Directory`; `../images/avatar.png` is parsed from the directory where the CSS file is located.

!!! warning "Asset prefix"
    In the page, the resource paths use the original name and extension of the design file. No Unreal asset prefix is added. For example, under the default configuration, the texture asset is named `T_avatar`, but in the page, it is still written as `avatar.png`. The plugin will find the corresponding asset based on the current asset naming rules.

The display size of images is determined by HTML attributes and CSS layouts. When scaling images, keep the required proportions. Enlarging low-resolution images may reduce clarity. When the interface is large or has multiple display sizes, it is necessary to check the texture size and actual display effect on the target platform.

!!! info "SVG assets"
    The synchronization feature allows SVG files to be imported as `USVGData` assets. However, the current Unreal asset domain does not support loading this asset type directly. When displaying on the page, use supported bitmap textures and verify the effect on the target platform.

## Font loading and selection

!!! warning "Select the Font Face asset"
    When dragging font files directly into the **Content Browser**, Unreal Engine may create two types of assets by default:

    - **Font**: Unreal Engine.
    - **Font Face** (`UFontFace`):  The assets used when Markup UI loads fonts.

    Make sure that the **Font Face** asset is located in the `Asset Directory`, and corresponds to the font file path referenced on the page.

After synchronizing the `.ttf` or `.otf` fonts as Font Face assets, use the `@font-face` declaration in CSS:

```css
/* styles/main.css */
@font-face {
  font-family: "Interface";
  src: url("../fonts/interface.ttf");
}

body {
  font-family: "Interface", sans-serif;
}
```

The font path is relative to the CSS file that declares it. You can also use `/fonts/interface.ttf` to search from the `Asset Directory`. `Interface` is the name of the font family specified in CSS, which can be different from the name of the Unreal asset.

## Missing Chinese Characters

When displaying text in Chinese or other languages, select a font that contains the required characters. Ensure that the corresponding font assets have been imported. If the text appears blank or as a box, first check whether the font file contains these characters, and then check the font path, asset name, and the settings on the page. `font-family` Set.

Do not rely solely on the fonts developed on the computer to determine the final outcome. It is necessary to check the actual text on both the editor preview and the target device.

## Update and troubleshoot

After modifying the image or font source files, synchronize the assets again and reopen the page or resume the playback. After changing the `Asset Directory` or asset naming rules, it is also necessary to reload the opened pages.

| Phenomena | Items to check |
| --- | --- |
| Images not displayed | Whether the file has been imported, whether the path and file name are correct, and whether the asset is located in the `Asset Directory` |
| The image appears blurry. | Is the resolution of the source image, texture settings, and the display size on the page matching? |
| The font is not being applied correctly. | Are the path of `@font-face`, the name of the font family, and the Font Face asset correct? |
| Chinese characters are displayed as boxes. | Does the font contain the required characters, and can the font asset be loaded? |
| The old content still appears after the modifications are made. | Should the assets be re-synced and the page reloaded? |

For details on path and asset naming rules, refer to [Working Directories](working-directories.md) and [Plugin Settings](../getting-started/settings.md).
