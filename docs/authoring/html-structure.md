---
icon: bootstrap/filetype-html
---

# HTML 文档结构

HTML 语法与元素参考：[MDN HTML 文档](https://developer.mozilla.org/en-US/docs/Web/HTML){ target="_blank" rel="noopener noreferrer" }；规范定义见 [WHATWG HTML Standard](https://html.spec.whatwg.org/multipage/){ target="_blank" rel="noopener noreferrer" }。

HTML 文档由元素、属性和文本组成。元素定义界面的内容与层级，属性用于标识元素、引用资源或配置行为；CSS 根据元素及其属性设置布局和样式。

## 文档骨架

建议使用完整的 HTML 文档结构：

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Player Panel</title>
  <link rel="stylesheet" href="../styles/main.css">
</head>
<body>
  <main class="player-panel">
    <h1>Player</h1>
    <p>Level 1</p>
  </main>
</body>
</html>
```

| 组成部分 | 用途 |
| --- | --- |
| `<!doctype html>` | 声明文档使用 HTML 格式 |
| `html` | 文档根元素，包含 `head` 与 `body` |
| `head` | 保存字符编码、文档标题及样式引用等信息 |
| `meta charset="utf-8"` | 声明字符编码，源文件也应保存为 UTF-8 |
| `title` | 定义文档标题，区别于页面中可见的标题文字 |
| `link` | 引用外部 CSS 样式表 |
| `body` | 包含需要显示的界面内容 |

`lang` 用于声明文档内容的语言，例如中文使用 `zh-CN`，英文使用 `en`。[^language]

!!! note "文档标题与界面标题"
    `title` 不会在页面内容区域显示。需要在界面中显示标题时，应在 `body` 中添加 `h1` 等元素；引擎窗口名称由宿主界面决定。

## 元素与标签

大多数元素由开始标签、内容和结束标签组成：

```html
<p>Player information</p>
```

这里的 `p` 是元素名称，`Player information` 是文本内容。元素可以包含其他元素：

```html
<div class="player-panel">
  <h1>Player</h1>
  <p>Level 1</p>
</div>
```

`div` 是容器，`h1` 和 `p` 是其子元素。缩进用于表达源文件的层级，不代替实际的标签嵌套。

### 常见元素

| 元素 | 常见用途 |
| --- | --- |
| `div` | 分组界面内容，作为布局容器 |
| `main` | 组织页面主要内容 |
| `h1`～`h6` | 表示不同层级的标题 |
| `p` | 表示一个段落 |
| `span` | 标记一段行内内容，便于单独设置样式 |
| `img` | 引用图片 |
| `button` | 定义按钮元素，业务操作另行绑定 |

元素名称不决定最终布局。容器尺寸、排列方向、间距和颜色应通过 CSS 设置，参见[布局与尺寸](layout-and-styles.md)与 [CSS 样式](css-styles.md)。

### 空元素

`meta`、`link`、`img` 和 `input` 等为空元素，不包含子内容，也不写结束标签。例如：

```html
<link rel="stylesheet" href="../styles/main.css">
<img src="../images/avatar.png" alt="Player avatar">
```

图片示例中的文件需已同步到`资产目录`。路径相对于引用它的 HTML 文件解析，见[资源路径](resource-paths.md)。

## 属性

属性写在开始标签内，通常采用 `名称="值"` 的形式。属性值统一使用引号，多个属性之间以空格分隔。

```html
<div id="player-panel" class="panel compact">
  <span class="player-name">Player</span>
</div>
```

- `id` 标识当前文档中的特定元素，同一文档内应保持唯一。
- `class` 为元素指定一个或多个类名，多个类名用空格分隔，可由多个元素共用。
- `href`、`src` 等属性引用外部文件或资源。

对应的 CSS 选择器示例：

```css
#player-panel {
  padding: 24px;
}

.player-name {
  color: #55b7ff;
}
```

`#player-panel` 匹配具有相应 `id` 的元素，`.player-name` 匹配具有相应类名的元素。HTML 中不需要在 `id` 或 `class` 的值前添加 `#` 或 `.`。

## 文本与特殊字符

文字直接写在元素内部。需要在文字中显示 `<` 或 `&` 等具有 HTML 语法含义的字符时，使用字符引用：

```html
<p>Health &lt; 100</p>
<p>Weapons &amp; Armor</p>
```

这两行分别显示 `Health < 100` 和 `Weapons & Armor`。常用写法包括 `&lt;`（`<`）、`&gt;`（`>`）、`&amp;`（`&`）和 `&quot;`（双引号）。

默认的 HTML 空白处理会合并连续空格和换行。不要依靠源文件中的空格数量或空行进行排版；段落、间距与换行方式应通过合适的元素和 CSS 设置。

注释使用 `<!-- ... -->`，不作为页面文字显示：

```html
<!-- Player summary -->
<p>Level 1</p>
```

## 元素嵌套与页面组织

先按内容关系分组，再为需要独立布局或样式的区域设置类名。例如：

```html
<main class="player-panel">
  <div class="player-summary">
    <h1 class="player-name">Player</h1>
    <p class="player-level">Level 1</p>
  </div>
  <div class="player-actions">
    <button>View inventory</button>
  </div>
</main>
```

`player-summary` 与 `player-actions` 是同级区域，分别包含信息和操作。保持开始、结束标签正确配对，避免交叉嵌套；例如，不应将 `div` 等块级内容放入 `p` 元素中。

!!! note "按钮显示与业务操作"
    添加 `button` 只定义页面中的按钮元素，不会自动执行游戏逻辑。事件和业务命令的关联方式见[事件与命令](../binding/events-and-commands.md)。

## 与数据绑定的关系

普通 HTML 可以用于静态界面。需要显示业务数据、按条件显示元素或重复生成列表时，再使用 Markup UI 的绑定语法。绑定声明依附于现有文档结构，不需要另建一套 HTML 文档。

相关说明：[数据绑定概述](../binding/getting-started.md)、[条件绑定](../binding/conditions-and-lists.md)。

!!! info "HTML 支持范围"
    本页说明常用文档组织方式，不代表完整浏览器功能兼容性。具体元素、样式和交互能力以[支持范围与限制](../reference/support-and-limitations.md)及对应平台说明为准。

[^language]: 语言声明不翻译页面文字，也不代替字体配置。显示中文等字符时，仍需确保所用字体包含相应字形。
