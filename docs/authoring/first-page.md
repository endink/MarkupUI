---
icon: bootstrap/file-earmark-plus
---

# 编写第一个页面

创建一个静态信息面板，使用 HTML 定义内容，通过外部 CSS 设置布局与颜色，最后在引擎编辑器中预览。完成后应能看到标题、说明文字和一个显示 `Ready` 的状态区域。

!!! info "开始前"
    已在工程中安装并启用对应平台插件。准备一个用于保存 HTML 和 CSS 的`设计时目录`，并确认编辑器可以加载页面资源。安装入口：[Unreal Engine](../ue/getting-started/install.md)、[Unity](../unity/getting-started/install.md)。

## 1. 创建文件目录

在`设计时目录`中建立以下结构：

```text
first-page/
  pages/
    index.html
  styles/
    main.css
```

`first-page/` 作为本例的`设计时目录`。文件夹名称可调整，但 HTML 中的引用路径必须与实际文件位置一致。

## 2. 编写 HTML

将以下内容保存为 UTF-8 编码的 `pages/index.html`：

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>First page</title>
  <link rel="stylesheet" href="../styles/main.css">
</head>
<body>
  <main class="panel">
    <h1>Hello, Markup UI</h1>
    <p>This page is loaded from an HTML document.</p>
    <div class="status">Ready</div>
  </main>
</body>
</html>
```

`main` 包含面板内容，`class="panel"` 用于匹配样式规则。`link` 引入样式表：从 `pages/` 返回上一级，再进入 `styles/`，因此路径为 `../styles/main.css`。

本例使用静态英文文字，无需提供数据上下文。[^sample-text]

## 3. 添加 CSS

将以下内容保存为 `styles/main.css`：

```css
body {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  box-sizing: border-box;
  margin: 0;
  padding: 24px;
  background-color: transparent;
  color: #edf4fa;
  font-family: sans-serif;
  font-size: 16px;
}

.panel {
  box-sizing: border-box;
  width: 100%;
  max-width: 480px;
  padding: 24px;
  background-color: rgba(27, 42, 56, 0.3);
  border: 2px solid #55b7ff;
  border-radius: 12px;
}

h1 {
  margin: 0 0 16px;
  font-size: 28px;
}

p {
  margin: 0 0 24px;
  line-height: 1.5;
}

.status {
  padding: 8px 12px;
  background-color: #55b7ff;
  color: #101820;
}
```

`body` 使用透明背景和 Flex 布局，将面板在页面中居中；`.panel` 设置面板宽度、内边距和边框，`.status` 设置状态区域颜色。`max-width` 限制面板的最大内容宽度；预览区域较小时，应检查内容是否仍能完整显示。

可直接下载 [HTML 示例](assets/first-page/pages/index.html)与 [CSS 示例](assets/first-page/styles/main.css)，保存时保留上述目录结构。

## 4. 导入资源并预览

=== "Unreal Engine"

    1. 打开项目设置中的 **Markup UI** 资源设置，配置以下目录：

        - **Design Root Directory（设计时目录）**：设为本例的 `first-page/`，保存 HTML、CSS 等设计源文件。
        - **Asset Root Directory（资产目录）**：本例设为 `/Game/FirstPageUI`，对应工程的 `Content/FirstPageUI/`，保存导入后的文档和样式资产。

    2. 在 Viewport 顶部的 **Markup UI** 工具栏菜单中选择 **Import Design Folder**（同步资产），将设计时目录 `first-page/` 中的资源同步到 `/Game/FirstPageUI`。同步后，HTML 和 CSS 分别位于资产目录下的 `pages` 与 `styles` 子目录，保留相对路径关系。
    3. 在内容浏览器中双击导入的 HTML 文档资产，打开资产编辑器并查看页面预览。
    4. 调整预览区域大小，检查标题、面板边框和状态区域是否显示完整。

    详细操作见[插件配置](../ue/getting-started/settings.md)、[资产同步](../ue/resources/asset-synchronization.md)和[编辑器预览](../ue/resources/editor-preview.md)。

=== "Unity"

    1. 打开 **Window → Markup UI → Settings**，配置以下目录并点击 **Apply**：

        - **Design Folder（设计时目录）**：设为本例的 `first-page/`，保存 HTML、CSS 等设计源文件。相对路径以 Unity 工程根目录为起点，也可填写完整的绝对路径。
        - **Assets Folder（资产目录）**：本例可设为 `Assets/FirstPageUI`，保存同步后供页面预览和运行时加载的资源；使用工程相对路径和 `/` 分隔符。

    2. 在同一设置页点击 **Sync Design Folder to Assets Folder**（同步资产），选中本例 HTML 和 CSS，点击 **Start**。
    3. 核对源目录、目标目录及覆盖选项，确认后点击 **Confirm and Import**。
    4. 导入完成后，在 **Project** 窗口中双击 HTML 资产，查看 **Preview**。若显示 **Load HTML** 按钮，点击后加载页面。

    !!! warning "确认覆盖范围"
        同步操作会直接写入目标目录，无法通过 Unity 的 **Undo** 撤销。首次尝试可使用独立的目标目录，确认列表仅包含需要导入的文件。

    详细操作见[同步设计文件](../unity/resources/sync-design-files.md)和[预览页面资产](../unity/resources/editor-preview.md)。

!!! note "浏览器预览与引擎预览"
    可以在浏览器中打开本例 HTML 辅助检查文件内容，但最终显示结果应在插件预览中确认。浏览器支持的 HTML、CSS 和交互能力不代表插件均已支持。

## 5. 验证修改

1. 将 HTML 标题文字 `Hello, Markup UI` 改为 `My First UI` 并保存。
2. 将 CSS 中 `.panel` 的边框颜色改为 `#83d7ff` 并保存。
3. 重新同步资产。
4. 重新加载预览，检查标题和边框颜色。

预期结果：透明页面中央显示一个深色、带蓝色边框的面板，内部有标题、说明和浅蓝色的 `Ready` 状态区域。状态文字是 HTML 中的固定文本，不代表运行时加载状态。

## 常见问题

| 现象 | 检查项 |
| --- | --- |
| 文字显示，但没有背景和边框 | CSS 是否已导入；`../styles/main.css` 是否与导入后的目录一致 |
| 资源加载失败 | 文档及 CSS 是否位于配置的`资产目录`内；文件名和大小写是否一致 |
| 修改后仍显示旧内容 | 是否更新了工程资产，并重新加载预览 |
| 面板显示不完整 | 预览区域是否过小；页面边距、内边距及元素尺寸是否超出可用空间 |

## 后续操作

- 将页面显示在游戏中：[UE 第一个游戏界面](../ue/getting-started/quick-start.md)、[Unity 第一个游戏界面](../unity/getting-started/quick-start.md)。
- 继续编写页面：[HTML 文档结构](html-structure.md)、[布局与尺寸](layout-and-styles.md)、[CSS 样式](css-styles.md)。
- 使用游戏数据：[数据绑定概述](../binding/getting-started.md)。

[^sample-text]: 使用中文内容时，还需确认工程可加载的字体包含所需字形；字体配置请参考各平台的图片与字体文档。
