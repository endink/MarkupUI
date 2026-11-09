---
icon: bootstrap/file-earmark-plus
---

# Write Your First Page

Create a static information panel. Define the content using HTML, set the layout and colors using external CSS, and finally preview it in the engine editor. After completion, you should be able to see a title, explanatory text, and a display area. `Ready` The status area.

!!! info "Before starting"
    Install and enable the corresponding platform plugins in the project. Prepare a `Design-Time Directory` to store HTML and CSS files. Ensure that the editor can load page resources. Install the entry points: [Unreal Engine](../ue/getting-started/install.md), [Unity](../unity/getting-started/install.md)).

## 1. Create the file directory

Establish the following structure in the `Design-Time Directory`:

```text
first-page/
  pages/
    index.html
  styles/
    main.css
```

`first-page/` serves as the `Design-Time Directory` for this example. You can adjust the folder name, but the reference path in HTML must match the actual file location.

## 2. Write HTML code

Save the following file as `pages/index.html`, encoded in UTF-8:

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

The `main` section contains the panel content. The `class="panel"` attribute is used to match the style rules. The `link` tag is used to import the style sheet: it returns to the parent level from `pages/`, and then enters `styles/`. Therefore, the path is `../styles/main.css`.

This example uses static English text. No data context is required. [^sample-text]

## 3. Add CSS code

Save the following file as `styles/main.css`:

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

The `body` element uses a transparent background and Flex layout. The panel is centered on the page. Elements with class `.panel` are used to set the width, padding, and border of the panel. Elements with class `.status` are used to set the color of the status area. The `max-width` property limits the maximum content width of the panel. When the preview area is small, it is necessary to check whether the content can still be displayed completely.

You can directly download the [HTML example](assets/first-page/pages/index.html) and [CSS example](assets/first-page/styles/main.css). Keep the above directory structure when saving the files.

## 4. Import the resources and preview the results

=== "Unreal Engine"

    1. Open the **Markup UI** resource settings in the project settings. Configure the following directories:

        - **Design Root Directory**: Set to `first-page/` in this example. Save design source files such as HTML and CSS.
        - **Asset Root Directory**: Set to `/Game/FirstPageUI` in this example. This corresponds to `Content/FirstPageUI/`. Save the imported documents and style assets here.

    2. In the **Markup UI** toolbar menu at the top of the viewport, select **Import Design Folder** to synchronize the resources from the `first-page/` directory to `/Game/FirstPageUI`. After synchronization, HTML and CSS will be located in the `pages` and `styles` subdirectories under the asset directory. Keep the relative path relationship.
    3. Double-click on the imported HTML document asset in the content browser. Open the asset editor and view the page preview.
    4. Adjust the size of the preview area. Check whether the title, panel borders, and status area are displayed completely.

    For detailed operations, refer to [Plugin Settings](../ue/getting-started/settings.md), [Asset Synchronization](../ue/resources/asset-synchronization.md), and [Editor Preview](../ue/resources/editor-preview.md).

=== "Unity"

    1. Open **Window → Markup UI → Settings**, configure the following directories, and click **Apply**:

        - **Design Folder (Design directory)**: Set it to `first-page/` in this example. Save design source files such as HTML and CSS. Relative paths start from the root directory of the Unity project. You can also enter a complete absolute path.
        - **Assets Folder (Asset directory)**: In this example, it can be set to `Assets/FirstPageUI`. Save resources that will be used for page preview and runtime loading after synchronization. Use relative project paths and the `/` delimiter.

    2. On the same settings page, click **Sync Design Folder to Assets Folder**. Select the HTML and CSS in this example, and click **Start**.
    3. Verify the source directory, target directory, and overwrite options. After confirmation, click **Confirm and Import**.
    4. After the import is completed, double-click the HTML asset in the **Project** window to view **Preview**. If the **Load HTML** button is displayed, click it to load the page.

    !!! warning "Confirm the coverage."
        The synchronization operation will be written directly to the target directory, and it cannot be undone using Unity’s **Undo** function. For the first attempt, you can use a separate target directory to ensure that the list only contains the files that need to be imported.

    For detailed instructions, see [Synchronize Design Files](../unity/resources/sync-design-files.md) and [Preview Page Assets](../unity/resources/editor-preview.md).

!!! note "Browser preview and engine preview"
    You can open this example HTML file in a browser to check the content of the auxiliary files. However, the final display results should be confirmed through the plugin preview. The HTML, CSS, and interactive capabilities supported by browsers do not mean that the plugin also supports them.

## 5. Verify the modifications

1. Change the HTML title text to `Hello, Markup UI` and save it. `My First UI` Change the border color in the CSS to
2. Change the border color in CSS to `.panel` Change the border color to `#83d7ff` Change the border color in the CSS to
3. Re-synchronize assets.
4. Reload the preview to check the title and border color.

Expected result: A dark-colored panel with a blue border is displayed in the center of the transparent page. Inside the panel, there are a title, description, and a light blue `Ready` status area. The status text is fixed text in HTML, and does not represent the loading status at runtime.

## Common problems

| Phenomena | Check items |
| --- | --- |
| Text is displayed, but there is no background or border | Has the CSS been imported? Is `../styles/main.css` consistent with the imported directory? |
| Resource loading failed | Is the document and CSS located within the configured `Asset Directory`. Are the file names and case formats consistent? |
| The old content still appears after modifications | Has the project assets been updated, and should the preview be reloaded? |
| The panel display is incomplete. | Is the preview area too small? Are the page margins, internal margins, and element sizes exceeding the available space? |

## Subsequent operations

- Display the page in the game: [UE first game interface](../ue/getting-started/quick-start.md), [Unity first game interface](../unity/getting-started/quick-start.md).
- Continue writing the page: [HTML Document Structure](html-structure.md), [Layout and Sizing](layout-and-styles.md), [CSS Styles](css-styles.md).
- Use game data: [Data Binding Overview](../binding/getting-started.md).

[^sample-text]: When using Chinese content, it is necessary to ensure that the project includes the required fonts. For font configuration, refer to the documentation on fonts and images for each platform.
