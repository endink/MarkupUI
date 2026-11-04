# Markup UI 文档站点

文档源文件位于 `docs/`，中文页面骨架已按公共内容、Unreal Engine、Unity、示例教程和版本信息分组；正文待逐步完善，英文后续补充。

## 本地预览

安装 Python 3.11 或更高版本后，双击 `preview-docs.bat`。脚本创建 `.venv-zensical`、安装依赖并启动预览。在浏览器打开终端显示的地址；修改文档后自动刷新。按 Ctrl+C 停止。

也可手动运行：

```powershell
py -3 -m venv .venv-zensical
.\.venv-zensical\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv-zensical\Scripts\python.exe -m zensical serve
```

## 构建检查

```powershell
.\.venv-zensical\Scripts\python.exe -m zensical build --clean --strict
```

生成文件位于 `site/`，无需提交。依赖版本在 `requirements-docs.txt` 中统一维护。

## GitHub Pages

1. 在 GitHub 创建目标仓库，将本地仓库关联并推送到 `main`。
2. 在仓库 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**。
3. 在 Actions 中手动运行 Documentation，或再次推送到 `main`。

Pull Request 仅执行构建检查；`main` 更新和在 `main` 上手动触发会构建并发布。发布任务使用 `github-pages` 环境，需要符合仓库的部署保护规则。

本地默认地址为 `http://127.0.0.1:15861/`。线上构建从 Pages 自动取得地址，通过 `DOCS_SITE_URL` 注入，支持仓库子路径，无需将账号名称写入配置。若以后启用自定义域名，在 Pages 设置中配置并核对生成地址。

参考：[Zensical](https://zensical.org/docs/)、[GitHub Pages 自定义工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

## 站点配置

### 代码高亮

`html` 代码块使用项目内的 Markup UI 高亮器，保留 HTML、内嵌 CSS 和 JavaScript 的高亮，并识别 `@` / `mk:` 指令、文本插值和绑定表达式。也可显式使用 `markupui` 语言标记。CSS 等其他语言的代码块继续使用原有高亮。

高亮器位于 `tools/markupui-highlighter/`，通过 `requirements-docs.txt` 安装，本地预览和 GitHub Actions 共用。修改高亮器后重新安装依赖，执行一次清洁构建以更新高亮缓存，再重启预览；全新环境也必须先安装依赖。颜色在 `docs/stylesheets/extra.css` 中分别适配深浅主题。高亮仅用于展示，不验证语法是否合法或平台是否支持。

C++ 使用 `cpp`，C# 使用 `csharp`。这两类代码块在 Pygments 原有规则上增加 SDK 类型、`MARKUPUI_*` 宏、调用和属性的识别，使用单独的深浅主题配色。类型名称和调用识别属于词法提示，不进行编译器级别的符号解析；注释和字符串中的名称不会套用这些规则。

高亮器通过 `markupui_highlighter` Markdown 扩展在每个渲染实例中主动注册，普通正文修改的增量更新无需手动清理缓存。`preview-docs.bat` 在启动时自动刷新构建缓存；升级高亮器后重启该脚本即可。`scripts/check-highlight-preview.py` 会在隔离站点启动预览并连续更新页面，检查 C++、C# 和 HTML 的高亮是否保留，此检查也在 CI 中运行。

唯一配置文件为 `zensical.toml`，使用 Zensical modern 深色主题。站内搜索随中文主题启用。Pages 构建通过 `scripts/build-docs.py` 读取 `DOCS_SITE_URL`，生成根目录下的临时 TOML，构建结束后自动删除；本地直接预览无需配置环境变量。
