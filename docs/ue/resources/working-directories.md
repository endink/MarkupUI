---
icon: bootstrap/folder2-open
---

# 工作目录

Markup UI 使用`设计时目录`维护界面源文件，通过同步将文件导入`资产目录`，供 Unreal Engine 预览和运行时加载。两类目录在[插件配置](../getting-started/settings.md)中设置。

## 设计时目录与资产目录

- **设计时目录**：存放可编辑的 HTML、CSS、图片和字体，通常由界面设计人员维护。
- **资产目录**：存放导入 Unreal 工程后的资产，供开发人员引用、文档资产预览和游戏运行时加载。

例如，`设计时目录`中的 `pages/index.html` 和 `styles/main.css` 同步后，在`资产目录`中保持对应的 `pages/` 与 `styles/` 结构。资产名称根据插件配置的命名规则生成；页面中仍使用源文件路径。

```text
设计时目录/                  资产目录/
  pages/index.html    →       pages/HTML_index
  styles/main.css     →       styles/CSS_main
```

示例使用默认资产前缀。通过 Viewport 顶部的 **Markup UI → Import Design Folder** 同步设计文件；也可以将支持的文件单独拖入 **Content Browser** 导入。

## 支持同步的文件类型

同步功能识别以下文件，并将其导入为对应的 Unreal 资产：

| 设计文件 | 导入后的资产类型 |
| --- | --- |
| `.html`、`.htm` | HTML 文档（`UHtmlDocument`） |
| `.css` | CSS 样式表（`UHtmlStyleSheet`） |
| `.svg` | SVG 资产（`USVGData`） |
| `.ttf`、`.otf` | 字体资产（`UFontFace`） |
| `.png`、`.jpg`、`.jpeg` 等位图文件 | 纹理资产（`UTexture2D`） |

不支持的文件类型会被跳过，不会导入为资产。受支持的文件仍需由 Unreal Engine 成功导入，才能用于页面。

## 资源域

**资源域**决定页面及其引用的样式、图片和字体从哪里查找：

| 资源域 | 查找对象 | 对应目录 |
| --- | --- | --- |
| 磁盘文件域 | 磁盘上的设计文件 | `设计时目录` |
| Unreal 资产域 | 导入到 Unreal 工程的资产 | `资产目录` |

文档及其引用的资源使用相同的资源域。**文档资产预览和游戏运行时使用 Unreal 资产域**，从`资产目录`查找，不直接读取`设计时目录`。

!!! note "资源域不会自动切换"
    如果`资产目录`中缺少页面所需的样式、图片或字体，即使`设计时目录`存在同名文件，也不会自动回退读取。请先同步或导入对应资产，再重新加载页面。

## 页面中的路径

页面使用源文件的逻辑路径，不需要写入 `HTML_`、`CSS_` 等资产前缀：

```html
<link rel="stylesheet" href="../styles/main.css">
<img src="/images/icon.png" alt="Icon">
```

在资产预览和游戏运行时：

- `../styles/main.css` 相对于引用它的 HTML 文档位置解析。
- `/images/icon.png` 从全局配置的`资产目录`开始查找，不表示磁盘根目录或工程根目录。

### CSS 中的路径

假设样式文件位于 `styles/main.css`，图片位于 `images/background.png`。   

CSS 中的**相对路径**从样式文件所在位置解析：

```css
/* styles/main.css */
.panel {
  background-image: url("../images/background.png");
}
```

也可以使用以 `/` 开头的**根路径**，从`资产目录`开始查找同一张图片：

```css
.panel {
  background-image: url("/images/background.png");
}
```

修改`设计时目录`中的文件后，需要重新同步资产；修改`资产目录`或命名规则后，已打开的页面需要重新加载。详细路径规则见[资源路径](../../authoring/resource-paths.md)，配置项见[插件配置](../getting-started/settings.md)。
