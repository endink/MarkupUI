---
icon: bootstrap/folder2-open
---

# Configure Directories

Open **Window → Markup UI → Settings** to configure the `Design-Time Directory` and `Asset Directory`. Click **Apply** to save your changes. File synchronization is a separate action.

!!! info "Before Changing Directories"
    Exit Play Mode and close the page preview so the runtime has stopped before you change directories. Directory settings are read-only during Play Mode and while entering it.

## Design Folder

The `Design-Time Directory` contains source HTML, CSS, images, and fonts for asset synchronization.

- Use an absolute path or a path relative to the Unity project root.
- You can leave this setting blank until you need to synchronize files. Synchronization requires an existing directory.
- HTML asset previews and Player builds load the imported assets described below.

## Assets Folder

The `Asset Directory` contains imported project assets for editor previews and runtime loading. For example, use `Assets/FirstPageUI`.

- Use `Assets` or a project-relative path under `Assets/` or `Packages/`.
- Separate path segments with `/`. Use named segments in place of `.`, `..`, and empty segments.
- To synchronize into `Packages/`, choose a writable local or embedded package.

Unity imports HTML and CSS as custom assets. Page references continue to use the original relative paths, without the Unity `.asset` suffix.

## Example Directory Configuration

```text
Unity project/
  Design/
    FirstPage/
      pages/index.html
      styles/main.css
  Assets/
    FirstPageUI/
```

Set **Design Folder** to `Design/FirstPage` and **Assets Folder** to `Assets/FirstPageUI`. Save the settings, then click **Sync Design Folder to Assets Folder** on the same page to select and import assets.

!!! warning "Use Separate Source and Destination Directories"
    The `Design-Time Directory` and the destination must be distinct, with neither directory inside the other. Select the actual source and destination paths directly. Synchronization requires paths that resolve without symbolic links or directory junctions.

## How Pages Load Assets

HTML asset previews load pages and their dependencies from the current project assets in the `Asset Directory`. The Player uses an asset package prepared during the build. After editing source files, synchronize or reimport the affected assets, then reload the page.

Next steps include [Write Your First Page](../../authoring/first-page.md), [Synchronize Design Files](sync-design-files.md), and [Build the Player](../publishing/player-build.md).
