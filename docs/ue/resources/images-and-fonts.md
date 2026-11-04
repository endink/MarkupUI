---
icon: bootstrap/images
---

# 图片与字体

Unreal Engine 中的页面从`资产目录`加载图片和字体。先将文件放入`设计时目录`并同步，或将文件导入`资产目录`，再在 HTML 和 CSS 中使用源文件的逻辑路径引用。

## 准备图片与字体

例如，将以下文件放入`设计时目录`：

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

通过 **Markup UI → Import Design Folder** 同步后，目录结构保持对应。使用插件默认资产命名规则时，各文件生成以下资产：

| 设计文件 | 导入后的资产 | 资产类型 |
| --- | --- | --- |
| `pages/index.html` | `pages/HTML_index` | `UHtmlDocument` |
| `styles/main.css` | `styles/CSS_main` | `UHtmlStyleSheet` |
| `images/avatar.png` | `images/T_avatar` | `UTexture2D` |
| `fonts/interface.ttf` | `fonts/interface` | `UFontFace` |

支持的同步格式见[工作目录](working-directories.md)。

## 图片引用与显示尺寸

HTML 使用 `img` 引用图片：

```html
<img src="/images/avatar.png" alt="Player avatar">
```

CSS 也可以引用图片；下面的相对路径从 `styles/main.css` 所在位置计算：

```css
/* styles/main.css */
.avatar {
  width: 96px;
  height: 96px;
  background-image: url("../images/avatar.png");
}
```

`/images/avatar.png` 从全局配置的`资产目录`开始查找；`../images/avatar.png` 从 CSS 文件所在目录解析。

!!! warning "资产前缀"
    页面中的资源路径使用设计文件的原始名称和扩展名，不添加 Unreal 资产前缀。例如，默认配置下纹理资产名为 `T_avatar`，页面中仍写 `avatar.png`。插件会根据当前资产命名规则查找对应资产。

图片的显示尺寸由 HTML 属性和 CSS 布局决定。缩放图片时注意保留所需比例；放大低分辨率图片可能降低清晰度。界面较大或有多种显示尺寸时，应结合目标平台检查纹理尺寸与实际显示效果。

!!! info "SVG 资产"
    同步功能可以将 SVG 文件导入为 `USVGData` 资产，但当前 Unreal 资产域的页面图片加载不支持直接读取该资产类型。需要在页面中显示时，请使用受支持的位图纹理，并在目标平台验证效果。

## 字体加载与选择

!!! warning "选择 Font Face 资产"
    将字体文件直接拖入 **Content Browser** 时，Unreal Engine 默认可能创建两类资产：

    - **Font**：Unreal Engine 的字体资产。
    - **Font Face**（`UFontFace`）：Markup UI 加载字体时使用的资产。

    请确保 **Font Face** 资产位于`资产目录`中，并与页面引用的字体文件路径对应。

将 `.ttf` 或 `.otf` 字体同步为 Font Face 资产后，在 CSS 中通过 `@font-face` 声明并使用：

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

字体路径相对于声明它的 CSS 文件；也可以使用 `/fonts/interface.ttf` 从`资产目录`开始查找。`Interface` 是 CSS 中指定的字体族名称，与 Unreal 资产名称可以不同。

## 中文与缺失字形

显示中文或其他语言时，选择包含所需字符的字体，并确认对应字体资产已导入。若文字显示为空白或方框，先检查字体文件是否包含这些字形，再检查字体路径、资产名称和页面的 `font-family` 设置。

不要仅依赖开发计算机上的字体判断最终效果；应在编辑器预览和目标设备上检查实际文字。

## 更新与排查

修改图片或字体源文件后，重新同步资产，并重新打开页面或重新开始播放。更改`资产目录`或资产命名规则后，也需要重新加载已打开的页面。

| 现象 | 检查项 |
| --- | --- |
| 图片不显示 | 文件是否已导入，路径和文件名是否正确，资产是否位于`资产目录`下 |
| 图片显示模糊 | 源图分辨率、纹理设置及页面显示尺寸是否匹配 |
| 字体没有生效 | `@font-face` 的路径、字体族名称和 Font Face 资产是否正确 |
| 中文显示为方框 | 字体是否包含所需字形，字体资产是否可加载 |
| 修改后仍显示旧内容 | 是否重新同步资产并重新加载页面 |

路径与资产命名规则见[工作目录](working-directories.md)和[插件配置](../getting-started/settings.md)。
