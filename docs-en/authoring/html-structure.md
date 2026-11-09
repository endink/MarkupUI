---
icon: bootstrap/filetype-html
---

# HTML Document Structure

HTML syntax and element references: [MDN HTML document](https://developer.mozilla.org/en-US/docs/Web/HTML){ target="_blank" rel="noopener noreferrer" }. For specification definitions, refer to [WHATWG HTML Standard](https://html.spec.whatwg.org/multipage/){ target="_blank" rel="noopener noreferrer" }.

An HTML document consists of elements, attributes, and text. Elements define the content and hierarchy of the interface, while attributes are used to identify elements, reference resources, or configure behaviors; CSS is used to set the layout and style based on elements and their attributes.

## Document skeleton

It is recommended to use the complete HTML document structure:

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

| Components | Purpose |
| --- | --- |
| `<!doctype html>` | Declare the document to use HTML format |
| `html` | The root element of the document, including `head` and `body` |
| `head` | Store information such as character encoding, document title, and style references |
| `meta charset="utf-8"` | Declare the character encoding. The source file should also be saved in UTF-8 |
| `title` | Define the document title, which is distinct from the title text that is visible on the page |
| `link` | Reference external CSS style sheets |
| `body` | Include the interface content that needs to be displayed |

`lang` Used to declare the language of the document content, such as Chinese. `zh-CN` For English, it is used as follows. `en`. [^language]

!!! note "Document title and interface title"
    The `title` tag is not displayed in the page content area. When it is necessary to display the title in the interface, elements such as `h1` should be added to the `body`. The name of the engine window is determined by the host interface.

## Elements and tags

Most elements consist of a start tag, content, and an end tag:

```html
<p>Player information</p>
```

Here, `p` is the element name, and `Player information` is the text content. Elements can contain other elements:

```html
<div class="player-panel">
  <h1>Player</h1>
  <p>Level 1</p>
</div>
```

`div` is a container, and `h1` and `p` are its child elements. Indentation is used to indicate the hierarchy of the source file, and it does not replace the actual nesting of tags.

### Common elements

| Elements | Common uses |
| --- | --- |
| `div` | Used to group interface content, serving as layout containers |
| `main` | Organize the main content of the page |
| `h1`～`h6` | Represent titles at different levels |
| `p` | Indicate a paragraph |
| `span` | Mark a piece of inline content for easy styling customization. |
| `img` | Reference images. |
| `button` | Define button elements, with business operations to be bound separately. |

The name of the element does not determine the final layout. Container size, arrangement direction, spacing, and color should be set using CSS. Refer to [Layout and Sizing](layout-and-styles.md) and [CSS Styles](css-styles.md).

### Empty elements

Elements such as `meta`, `link`, `img`, and `input` are empty elements. They do not contain any child content and do not have a closing tag. For example:

```html
<link rel="stylesheet" href="../styles/main.css">
<img src="../images/avatar.png" alt="Player avatar">
```

The files in the image example must have been synchronized to the `Asset Directory`. The path is resolved relative to the HTML file that references it. See [Resource Paths](resource-paths.md).

## Properties

The properties are written within the start tag, and are usually used in this way. `name="value"` . , .

```html
<div id="player-panel" class="panel compact">
  <span class="player-name">Player</span>
</div>
```

- `id` identifies a specific element within the current document. It should be unique within the same document.
- `class` specifies one or more class names for an element. Multiple class names should be separated by spaces, and can be shared by multiple elements.
- Properties like `href` and `src` are used to reference external files or resources.

Examples of corresponding CSS selectors:

```css
#player-panel {
  padding: 24px;
}

.player-name {
  color: #55b7ff;
}
```

`#player-panel` matches elements with the corresponding `id`. `.player-name` matches elements with the corresponding class names. In HTML, there is no need to add `#` or `.` before the values of `id` or `class`.

## Text and special characters

When text needs to be written directly inside elements, use character references for characters that have HTML syntax, such as `<` or `&`:

```html
<p>Health &lt; 100</p>
<p>Weapons &amp; Armor</p>
```

These two lines show respectively `Health < 100` and `Weapons & Armor` Common writing methods include `&lt;` (`<`), `&gt;` (`>`), `&amp;` (`&`) and `&quot;` (double quotes)

The default HTML whitespace handling combines consecutive spaces and line breaks. Do not rely on the number of spaces or blank lines in the source file for layout. Paragraphs, spacing, and line breaks should be set using appropriate elements and CSS.

Comments are written using `<!-- ... -->` and are not displayed as page text:

```html
<!-- Player summary -->
<p>Level 1</p>
```

## Element nesting and page organization

First, group elements based on content relationships, and then assign class names to areas that require independent layout or styling. For example:

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

`player-summary` and `player-actions` It is a, . , , . ,  `div` Place equal block-level content here. `p` Within the element.

!!! note "Button display and business operations"
    Adding a `button` only defines the button element on the page. It does not automatically execute game logic. For the association between events and business commands, see [Events and Commands](../binding/events-and-commands.md).

## Relationship with data binding

Ordinary HTML can be used for static interfaces. When it is necessary to display business data, display elements based on conditions, or generate lists repeatedly, the binding syntax of Markup UI should be used. The binding declaration is attached to the existing document structure, and there is no need to create a separate HTML document.

Related explanations: [Data Binding Overview](../binding/getting-started.md), [Conditional Binding](../binding/conditions-and-lists.md).

!!! info "HTML support scope"
    This page describes the common document organization methods. It does not represent the complete compatibility of browser functions. Specific elements, styles, and interactive capabilities shall be subject to the [Support and Limitations](../reference/support-and-limitations.md) and corresponding platform descriptions.

[^language]: The language declaration does not translate the page text, nor does it replace the font configuration. When displaying characters such as Chinese, it is still necessary to ensure that the used font contains the corresponding glyphs.
