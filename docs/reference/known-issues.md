---
icon: bootstrap/exclamation-triangle
---

# 已知问题

以下问题可能导致页面效果与浏览器不同。实际表现可能因平台、显示缩放和页面布局而异；发布前请在目标平台检查界面。

> Markup UI 使用 [Blitz](https://github.com/DioxusLabs/blitz){ target="_blank" rel="noopener noreferrer" } 解析 HTML。涉及 Blitz 的渲染问题需要等待上游修复，修复后还需更新并验证 Markup UI。

## 细边框可能缺失

在 Windows 显示缩放为 125% 或 150% 的部分布局中，圆角面板或输入框的 `1px` 边框可能缺少某一边。

```css
.panel {
  border: 1px solid #55b7ff;
  border-radius: 12px;
}
```

检查不同显示缩放下的效果；需要时可尝试较粗的边框。相关上游问题：[#837](https://github.com/DioxusLabs/blitz/issues/837){ target="_blank" rel="noopener noreferrer" }。

## 三维变换可能不生效

`rotateX()`、`rotateY()` 和透视效果可能无法按预期显示。将二维变换与三维旋转写在同一个 `transform` 中时，整个变换也可能失效。

```css
.card {
  transform: translate(30px, -10px) rotateY(42deg);
}
```

需要稳定显示时，可优先使用二维变换并在目标平台验证。该问题在 Windows 的页面中观察到，其他平台的表现尚未确认。

## 圆角与图片裁剪可能不一致

图片尺寸大于容器、并通过负外边距调整位置时，`overflow: hidden` 配合 `border-radius` 可能无法按预期裁剪图片，图片位置和右侧圆角也可能与浏览器不同。

```css
.frame {
  overflow: hidden;
  border-radius: 16px;
}

.frame img {
  width: 240px;
  margin-left: -20px;
}
```

请检查实际页面中的图片位置和四个圆角。该现象在特定预览环境中观察到，平台间表现可能不同。

## 圆角背景模糊可能超出边界

同时使用 `border-radius` 和 `backdrop-filter` 时，背景模糊可能显示在圆角外侧的矩形区域。

```css
.glass {
  border-radius: 24px;
  backdrop-filter: blur(12px);
}
```

该现象在特定预览环境中观察到；使用背景模糊时请在目标平台检查边缘效果。

## 渐变颜色空间可能不生效

使用 `in oklab` 或 `in srgb-linear` 指定渐变插值颜色空间时，结果可能与浏览器不同，两种写法也可能显示为相近效果。

```css
.panel {
  background: linear-gradient(90deg in oklab, red, blue);
}
```

如果颜色过渡对界面设计有重要影响，请在目标平台核对效果。该现象在特定预览环境中观察到。

## SVG 显示限制

### SVG 背景重复

SVG 用作 CSS 背景时，`background-repeat: repeat` 可能只显示一张图片，而不是平铺：

```css
.pattern {
  background-image: url("pattern.svg");
  background-size: 40px 40px;
  background-repeat: repeat;
}
```

可以考虑使用位图背景并在目标平台验证。此问题在特定预览环境中观察到；Unreal Engine 中外部 SVG 资产的使用范围另见[图片与字体](../ue/resources/images-and-fonts.md)。

### 内联 SVG 描边

通过外部 CSS 为内联 SVG 的父元素指定 `stroke` 等样式时，子路径可能不显示。

```css
.icon {
  fill: none;
  stroke: white;
  stroke-width: 2;
}
```

```html
<svg class="icon" viewBox="0 0 24 24">
  <path d="M2 12H22"></path>
</svg>
```

如果描边内容不可见，请在目标平台检查 SVG 的显示效果。该现象在特定预览环境中观察到。

### 圆形粗描边

SVG 圆形的描边宽度超过直径时，中心可能出现小孔：

```html
<svg viewBox="0 0 120 120">
  <circle cx="60" cy="60" r="12" fill="none"
          stroke="#ef8354" stroke-width="32"></circle>
</svg>
```

若需要实心圆，优先使用填充而非粗描边，并检查目标平台显示效果。
