---
icon: bootstrap/folder2-open
---

# Working Directories

Markup UI uses `Design-Time Directory` to maintain the interface source files. These files are synchronized and imported into `Asset Directory`, allowing for previewing in Unreal Engine and loading during runtime. Both types of directories are configured in [Plugin Settings](../getting-started/settings.md).

## Design-time Directory vs. Asset Directory

- **Design-time Directory**: Stores editable HTML, CSS, images, and fonts. This directory is usually maintained by interface designers.
- **Asset Directory**: Stores assets that have been imported into the Unreal Engine project. These assets can be referenced by developers, used for documentation, and loaded during game runtime.

For example, when `Design-Time Directory` contains `pages/index.html` and `styles/main.css`, these files are synchronized and kept in the `Asset Directory` with corresponding `pages/` and `styles/` structures. Asset names are generated according to the naming rules configured in the plugin. Source file paths are still used in the pages.

```text
Design-Time Directory/        Asset Directory/
  pages/index.html       →       pages/HTML_index
  styles/main.css        →       styles/CSS_main
```

The example uses a default asset prefix. Design files can be synchronized using **Markup UI → Import Design Folder** at the top of the viewport. Alternatively, supported files can be dragged directly into the **Content Browser** for import.

## Suitable file types for synchronization

The synchronization function recognizes the following files and imports them as corresponding Unreal assets:

| Design files | Types of assets after import |
| --- | --- |
| `.html`, `.htm` | HTML documents (`UHtmlDocument`) |
| `.css` | CSS style sheets (`UHtmlStyleSheet`) |
| `.svg` | SVG assets (`USVGData`) |
| `.ttf`, `.otf` | Font assets (`UFontFace`) |
| Image files in formats such as `.png`, `.jpg`, `.jpeg` | Texture assets (`UTexture2D`) |

Files that are not supported will be skipped and not imported as assets. Supported files must be successfully imported by Unreal Engine before they can be used on the page.

## Resource domains

**Resource domains** determine where the page and the styles, images, and fonts it references are found:

| Resource domains | Objects for searching | Corresponding directory |
| --- | --- | --- |
| Disk file domain | Design files on disk | `Design-Time Directory` |
| Unreal asset domain | Assets imported into the Unreal engine | `Asset Directory` |

Documents and the resources they reference use the same resource domain. **Document assets are previewed and used in the Unreal engine during game execution**, found in `Asset Directory`, not directly from `Design-Time Directory`.

!!! note "The resource domain does not switch automatically"
    If the styles, images, or fonts required by a page are missing from the `Asset Directory`, even if files with the same names exist in the `Design-Time Directory`, the system will not automatically revert to reading those files. Please synchronize or import the corresponding assets first, and then reload the page.

## The paths in the page

The logic path of the source file used by the page, no need to write it. `HTML_`, `CSS_` Asset prefix:

```html
<link rel="stylesheet" href="../styles/main.css">
<img src="/images/icon.png" alt="Icon">
```

During asset preview and when the game is running:

- `../styles/main.css` is resolved relative to the location of the HTML document that references it.
- `/images/icon.png` is searched from the globally configured `Asset Directory`. It does not refer to the root directory of the disk or the root directory of the project.

### Paths in CSS

Suppose the style file is located at `styles/main.css`, and the image is located at `images/background.png`.  

In CSS, **relative paths** are resolved from the location of the style file.

```css
/* styles/main.css */
.panel {
  background-image: url("../images/background.png");
}
```

You can also use **root paths** that start with `/` to find the same image from the `Asset Directory`.

```css
.panel {
  background-image: url("/images/background.png");
}
```

After modifying the files in the `Design-Time Directory`, it is necessary to re-sync the assets. If you modify the `Asset Directory` or naming rules, the opened pages need to be reloaded. For detailed path rules, see [Resource Paths](../../authoring/resource-paths.md). For configuration details, see [Plugin Settings](../getting-started/settings.md).
