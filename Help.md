# Markup UI 文档站点

中文文档位于 `docs/`，英文文档位于 `docs-en/`。两种语言的 Markdown 页面使用相同的相对路径，并共用主题、样式和截图。中文是默认语言，英文发布到 `/en/`。

## 本地预览

安装 Python 3.11 或更高版本后，双击 `preview-docs.bat`。脚本创建 `.venv-zensical`、安装依赖并构建中英文站点。打开 [中文首页](http://127.0.0.1:15861/) 或 [英文首页](http://127.0.0.1:15861/en/)，也可以通过页眉的语言菜单切换。保存修改后，脚本自动重建中英文站点，浏览器会在构建成功后刷新当前页面。按 Ctrl+C 停止。

也可手动启动双语实时预览。

```powershell
py -3 -m venv .venv-zensical
.\.venv-zensical\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv-zensical\Scripts\python.exe scripts/preview-docs.py
```

## 构建检查

```powershell
.\.venv-zensical\Scripts\python.exe scripts/build-docs.py
```

构建会检查中英文页面是否一一对应，允许显式登记的待翻译页面仅出现在中文站点，并以严格模式分别生成 `site/` 和 `site/en/`。生成文件无需提交。依赖版本在 `requirements-docs.txt` 中统一维护。

## GitHub Pages

1. 在 GitHub 创建目标仓库，将本地仓库关联并推送到 `main`。
2. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
3. 在 Actions 中手动运行 Documentation，或再次推送到 `main`。

GitHub Actions 默认构建中英文站点。Pull Request 执行构建检查，`main` 更新和在 `main` 上手动触发会构建并发布两种语言。发布任务使用 `github-pages` 环境，需要符合仓库的部署保护规则。

本地默认地址为 `http://127.0.0.1:15861/`。线上构建从 Pages 自动取得地址，通过 `DOCS_SITE_URL` 注入，支持仓库子路径，无需将账号名称写入配置。若以后启用自定义域名，在 Pages 设置中配置并核对生成地址。

参考：[Zensical](https://zensical.org/docs/)、[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

## 站点配置

### 代码高亮

代码块和带语言标记的行内代码统一通过 Tree-sitter 解析，再由项目的 Markdown 扩展直接生成 HTML。支持 C++、C#、HTML/XML、CSS、JavaScript、JSON、YAML；纯文本或未支持的语言仅转义显示，不自动猜测语言。HTML 中的 `<style>`、`<script>` 分别交给 CSS、JavaScript 解析器；Markup UI 指令属性和文本插值中的表达式使用 JavaScript 语法树配合专用显示规则处理。

高亮扩展位于 `tools/markupui-highlighter/`，通过 `requirements-docs.txt` 安装，本地预览和 GitHub Actions 共用。解析器版本固定在扩展的 `pyproject.toml`，依赖清单要求下载预编译包，无需本机编译解析器。第三方包、原生解析器、虚拟环境和下载缓存不提交到 Git 仓库。

扩展通过 PyMdown 的高亮提供者接口接入 SuperFences 和 InlineHilite，代码块、缩进代码和行内代码不调用 Pygments 的词法分析或 HTML 格式化。Pygments 可能仍由 Zensical 等上游依赖安装；无需手动删除这些上游依赖。生成的 HTML 沿用现有 CSS 角色名称和 `docs/stylesheets/extra.css` 中的深浅色板，并保持复制按钮。名称是否属于类型、命名空间等类别由官方查询的捕获结果决定，不再通过本地命名规则或符号表猜测。

基础高亮直接执行各语法仓库发布的原始 `highlights.scm`，C++ 按上游配置先加载 C 基础查询，再加载 C++ 查询。HTML 的内嵌 CSS、JavaScript 由官方 `injections.scm` 决定。查询快照和许可证位于 `tools/markupui-highlighter/markupui_queries/`；`manifest.json` 记录版本、来源与 SHA-256，测试校验快照未被修改。只将官方捕获类别映射为站点配色，不在查询文件中追加本地语言规则。

C++ 使用 `cpp`，C# 使用 `csharp`；也支持原有别名。只有 UE 宏、元数据以及 Markup UI 的宏、SDK 专有类型和绑定语法保留额外显示适配。Tree-sitter 不执行编译器级别的符号解析，高亮不验证代码能否编译或绑定功能是否受支持。

`markupui_highlighter` 扩展会在每个 Markdown 实例中注册提供者，普通正文的增量更新无需清理缓存。修改高亮器后重新运行 `preview-docs.bat`，脚本会安装依赖、执行严格清洁构建后启动预览。`scripts/check-highlight-preview.py` 在隔离站点连续修改页面，检查代码块、行内代码及内嵌语言的高亮；此检查与禁止 Pygments 高亮调用的回归测试均在 CI 中运行。

`zensical.toml` 定义公共主题、中文导航和页面顺序，`zensical.en.toml` 提供英文名称与导航标签。构建脚本为两种语言分别生成搜索索引与语言菜单。新增页面时，在两个内容目录中添加同路径页面，并更新导航与英文标签。先审核中文稿时，可把页面路径加入 `zensical.en.toml` 的 `pending_pages`。补齐译文和英文导航标签后，从该列表移除页面路径。Pages 构建通过 `scripts/build-docs.py` 读取 `DOCS_SITE_URL`，生成临时配置和英文构建目录，构建结束后自动清理。本地预览可直接使用默认地址。
