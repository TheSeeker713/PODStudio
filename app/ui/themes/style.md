# Theme System Design

**Version**: 0.1.0  
**Status**: STEP 2 - Tokens defined, not yet applied

---

## Overview

PODStudio uses a **token-based theming system** inspired by video editing applications like Adobe Premiere Pro and DaVinci Resolve.

### Design Principles

1. **Minimalist**: Clean, distraction-free interface
2. **Functional**: UI elements clearly communicate state and affordance
3. **Accessible**: High contrast, clear typography, keyboard-first
4. **Professional**: Video editor aesthetic with docked panels

---

## Theme Variants (Future)

### Light Theme (Default)
- High contrast for outdoor/bright environments
- White background, dark text
- Primary accent: Blue (#0078d4)

### Dark Theme (Future - Step 5+)
- Low eye strain for long editing sessions
- Dark background (#1e1e1e), light text
- Primary accent: Blue (#0078d4)

---

## Color Roles

### Semantic Colors
- **Primary**: Interactive elements (buttons, links, focus states)
- **Success**: Approved assets, completed jobs
- **Warning**: YELLOW hardware tier, caution states
- **Danger**: Rejected assets, RED hardware tier, errors
- **Info**: Informational messages, tooltips

### Hardware Tier Colors
- **Green (#28a745)**: All operations safe
- **Yellow (#ffc107)**: Warn on heavy operations
- **Red (#dc3545)**: Block unsafe operations

### Surface Colors
- **Background**: Main app background
- **Surface**: Panel backgrounds (docks, cards)
- **Surface Alt**: Hover states, dividers

---

## Typography

### Font Stack
```
Segoe UI, system-ui, -apple-system, sans-serif
```

### Sizes
- **XL (20px)**: Section headers
- **LG (16px)**: Panel titles
- **Base (14px)**: Body text, buttons
- **SM (12px)**: Metadata, labels

### Weights
- **Normal (400)**: Body text
- **Bold (600)**: Headings, active states

---

## Spacing Scale

Consistent spacing using 8px base unit:
- **XS (4px)**: Tight padding within elements
- **SM (8px)**: Default element padding
- **MD (16px)**: Panel padding, section gaps
- **LG (24px)**: Major section separation
- **XL (32px)**: Page margins

---

## Border Radii

- **SM (4px)**: Buttons, inputs
- **MD (8px)**: Cards, panels
- **LG (12px)**: Dialogs, modals
- **Pill (999px)**: Hardware pills, tags

---

## Shadows

Elevation system for depth:
- **SM**: Subtle lift (buttons, inputs on hover)
- **MD**: Cards, floating panels
- **LG**: Dialogs, context menus

---

## Application (Step 3+)

### Qt Stylesheet (QSS)
Tokens will be applied via Qt stylesheets:

```css
QPushButton {
    background-color: #0078d4;  /* primary */
    color: white;
    padding: 8px 16px;          /* sm md */
    border-radius: 4px;          /* sm */
    font-size: 14px;             /* base */
}

QPushButton:hover {
    background-color: #005a9e;  /* primary_hover */
}
```

### Dynamic Theme Switching
Future feature (v1.1):
- User preference stored in QSettings
- Hot-reload stylesheets on theme change
- Persist across sessions

---

## References

- [Qt Stylesheet Syntax](https://doc.qt.io/qt-6/stylesheet-syntax.html)
- [Material Design Color System](https://material.io/design/color/)
- [Adobe Spectrum Design Tokens](https://spectrum.adobe.com/page/design-tokens/)

---

**Status**: Tokens defined in `tokens.json`  
**Next**: Apply via Qt stylesheets in Step 3+
