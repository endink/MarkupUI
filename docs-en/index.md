---
icon: bootstrap/house
hide:
  - navigation
  - toc
---

# Home

<img src="images/markupui-logo.svg" alt="Markup UI Logo" width="128" height="128">

Markup UI is a user interface framework for games and real-time applications. It uses HTML for structure and CSS for layout and styling, with hardware-accelerated rendering, data binding, and event handling. Platform plugins integrate asset management, editor previews, and runtime display into each engine so that interfaces can share a page format while keeping UI design separate from application logic.

<!-- Add Unreal Engine and Unity screenshots here later. -->

## :bootstrap-play-circle: Getting Started

### Unreal Engine

Manage pages as document assets, preview them in the editor, and display them with a UMG widget.

[Installation and Project Setup](ue/getting-started/install.md) · [Your First In-Game UI](ue/getting-started/quick-start.md) · [Display Pages in UMG](ue/usage/umg.md)

#### Unreal Engine Quick Start Video

<iframe class="quick-start-video" src="https://www.youtube-nocookie.com/embed/i6j4lgOKl3E" title="Unreal Engine Quick Start Video" loading="lazy" allowfullscreen></iframe>

[Watch on YouTube](https://youtu.be/i6j4lgOKl3E?si=bZueuEBIKbOvEHXN)

### Unity

Synchronize HTML, CSS, and related assets into the project, preview pages in the HTML asset window, and display them through UI Toolkit.

[Installation and Project Setup](unity/getting-started/install.md) · [Your First In-Game UI](unity/getting-started/quick-start.md) · [Integrate with UI Toolkit](unity/usage/ui-toolkit.md)

## HTML and Layout

- [Basic Concepts](concepts/pages-and-resources.md)
- [Write Your First Page](authoring/first-page.md)
- [HTML Document Structure](authoring/html-structure.md)
- [Layout and Sizing](authoring/layout-and-styles.md)
- [DPI and Scaling](authoring/sizing-and-scaling.md)

## Styles and Resources

- [CSS Styles](authoring/css-styles.md)
- [Resource Paths](authoring/resource-paths.md)

## Data Binding

- [Data Binding Overview](binding/getting-started.md)
- [Data Context](concepts/data-context.md)
- [Binding Syntax](binding/binding-syntax.md)
- [Conditional Binding](binding/conditions-and-lists.md)

## Input and Events

- [Input and Two-Way Binding](binding/input-and-two-way-binding.md)
- [Events and Commands](binding/events-and-commands.md)

## Editor Tools and Packaging

| Task | Unreal Engine | Unity |
| --- | --- | --- |
| Update assets | [Asset Synchronization](ue/resources/asset-synchronization.md) | [Synchronize Design Files](unity/resources/sync-design-files.md) |
| Preview pages | [Editor Preview](ue/resources/editor-preview.md) | [Preview Page Assets](unity/resources/editor-preview.md) |
| Profile performance | [Profiling](ue/troubleshooting/profiling.md) | [Profiling](unity/troubleshooting/profiling.md) |
| Build the project | [Package the Project](ue/publishing/packaging.md) | [Build the Player](unity/publishing/player-build.md) |

## Reference and Releases

- [Markup and Binding Syntax](reference/binding-syntax.md)
- [Support and Limitations](reference/support-and-limitations.md)
- [Compatibility](releases/compatibility.md)
- [Changelog](releases/changelog.md)
- FAQs for [Unreal Engine](ue/troubleshooting/faq.md) · [Unity](unity/troubleshooting/faq.md)

!!! info "Content Status"
    Some sections are currently outlines. See each platform's documentation for the status of individual features.
