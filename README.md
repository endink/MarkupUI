<p align="right"><b>English</b> · <a href="README_CN.md">简体中文</a></p>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/images/readme/markup-ui-overview-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="docs/images/readme/markup-ui-overview.svg">
  <img alt="Markup UI — HTML/CSS interfaces for Unreal Engine and Unity" src="docs/images/readme/markup-ui-overview.svg" width="100%">
</picture>

<p align="center">
  <b>A data-driven HTML/CSS UI framework for games and real-time applications.</b><br>
  Unreal Engine · Unity · C++ · C#
</p>

<p align="center">
  <a href="#documentation">Documentation</a> ·
  <a href="https://markupui.labijie.com/en/ue/getting-started/quick-start/">Unreal Engine</a> ·
  <a href="https://markupui.labijie.com/en/unity/getting-started/quick-start/">Unity</a> ·
  <a href="https://github.com/endink/MarkupUI/issues">Issues</a>
</p>

## Markup UI

Markup UI uses HTML for interface structure and CSS for layout and styling. Hardware-accelerated rendering, data binding, and commands connect those interfaces to application logic. Build menus, inventories, settings panels, and other game interfaces while keeping page design separate from C++ or C# code.

- **HTML and CSS** — define page structure, reusable styles, layouts, and assets.
- **Data binding** — connect text, attributes, styles, conditions, and collections to application data.
- **UI interaction** — write input values back to models and invoke commands from UI events; use triggers to connect application events to page behaviors.
- **Engine integration** — work with Unreal Engine through UMG and with Unity through UI Toolkit, including engine-specific asset and preview workflows.
- **C++ and C#** — expose observable data and typed commands through the SDK and engine integrations.

# Documentation

- [简体中文](https://markupui.labijie.com/)
- [English](https://markupui.labijie.com/en/)

## Engine integrations

### Unreal Engine

**Blueprint support connects interfaces to gameplay logic**: bind Blueprint object properties, invoke Blueprint functions from page events, and send property change notifications through Blueprint nodes. Display HTML interfaces in UMG and preview pages in the editor, with C++ properties, `UFUNCTION` commands, and extension properties available for integration with existing game systems.

[Install](https://markupui.labijie.com/en/ue/getting-started/install/) · [Create your first interface](https://markupui.labijie.com/en/ue/getting-started/quick-start/) · [Display in UMG](https://markupui.labijie.com/en/ue/usage/umg/)

<a href="https://youtu.be/i6j4lgOKl3E?si=bZueuEBIKbOvEHXN">
  <img src="https://i.ytimg.com/vi/i6j4lgOKl3E/mqdefault.jpg" alt="Watch the Unreal Engine quick start on YouTube" width="320">
</a>

[Watch the Unreal Engine quick start on YouTube](https://youtu.be/i6j4lgOKl3E?si=bZueuEBIKbOvEHXN)

### Unity

Display HTML interfaces through UI Toolkit, synchronize page assets into the project, and preview them in the editor. Use C# data models and commands to connect interfaces to application logic.

[Install](https://markupui.labijie.com/en/unity/getting-started/install/) · [Create your first interface](https://markupui.labijie.com/en/unity/getting-started/quick-start/) · [Integrate with UI Toolkit](https://markupui.labijie.com/en/unity/usage/ui-toolkit/)

## From data to interaction

Templates describe what the interface displays. Data binding keeps page content connected to observable application data, while two-way binding writes user input back to the model. Commands let UI events invoke business operations; triggers let application events execute behaviors on page elements.

This supports interfaces such as inventories, player status panels, settings screens, and in-game menus, with presentation defined in HTML/CSS and application behavior implemented in C++ or C#.

[Write your first page](https://markupui.labijie.com/en/authoring/first-page/) · [Data binding](https://markupui.labijie.com/en/binding/getting-started/) · [Events and commands](https://markupui.labijie.com/en/binding/events-and-commands/) · [Triggers](https://markupui.labijie.com/en/binding/triggers/)

Report bugs, ask questions, or suggest features in [Issues](https://github.com/endink/MarkupUI/issues).
