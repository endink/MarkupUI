---
icon: bootstrap/folder2-open
---

# 配置目录

通过 **Window → Markup UI → Settings** 配置`设计时目录`与`资产目录`。修改后点击 **Apply** 保存；保存设置不会自动同步文件。

!!! info "修改目录前"
    停止 Play Mode 并关闭页面预览，使运行时停止后再修改目录。运行时运行或即将进入播放模式时，目录设置不可编辑。

## Design Folder：设计时目录

保存 HTML、CSS、图片和字体等设计源文件，用于资源同步。

- 支持完整的绝对路径或相对于 Unity 工程根目录的路径。
- 可以暂时留空；需要使用同步功能时必须指定已存在的目录。
- 不作为 HTML 资产预览或 Player 的直接资源来源。

## Assets Folder：资产目录

保存导入后由编辑器预览和运行时加载的工程资源。例如 `Assets/FirstPageUI`。

- 必须使用 `Assets`、`Assets/` 或 `Packages/` 下的工程相对路径。
- 使用 `/` 分隔符，不使用 `.`、`..` 或空路径段。
- 同步到 `Packages/` 下时，目标必须属于可写的本地包或嵌入包，不能是缓存包。

HTML 和 CSS 同步为自定义资产；页面引用仍使用原始相对资源路径，不需要在 HTML 中添加 Unity 资产文件的 `.asset` 后缀。

## 目录配置示例

```text
Unity 工程/
  Design/
    FirstPage/
      pages/index.html
      styles/main.css
  Assets/
    FirstPageUI/
```

将 **Design Folder** 设为 `Design/FirstPage`，将 **Assets Folder** 设为 `Assets/FirstPageUI`。保存后，在同一设置页点击 **Sync Design Folder to Assets Folder**（同步资产）开始选择和导入资源。

!!! warning "同步目录必须相互独立"
    `设计时目录`和目标目录不能相同，也不能互相包含。同步不支持通过符号链接或目录联接访问源、目标路径；需要选择实际目录。

## 资源读取方式

HTML 资产预览从 Assets Folder 中的当前工程资产加载页面及依赖；Player 使用构建阶段准备的资源包。修改设计源文件后，应先同步或重新导入对应资源，再重新加载页面。

后续操作：[编写第一个页面](../../authoring/first-page.md)、[同步设计文件](sync-design-files.md)、[构建 Player](../publishing/player-build.md)。
