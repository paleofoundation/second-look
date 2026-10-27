# Mapping Rx — preview 4

Created October 12, 2026 following the owner's correction that the simplified logo had lost the mapping visual. The owner prioritizes that meaning even when details diminish at favicon size and requested tighter Rx spacing plus restoration of the map-style “x marks the spot” idea.

The revised mark brings the R and x closer, centers the x within concentric open target rings, and restores cardinal crosshairs, inner registration marks and radial connectors. It retains the flat directional arrow and heavy outlined letters. Blue is `#1736F5`; yellow is `#FFC709`. Small favicon exports retain every mapping feature, with stronger line weights and full-blue inner marks to avoid muddy color blending on yellow.

- `remaprx-target-preview.png` / `.svg`: comparison sheet with native 16/32-pixel samples on light and dark surroundings.
- `remaprx-target-logo.svg`: editable outlined symbol, transparent background.
- `remaprx-target-logo-white.svg` / `.png`: blue logo on white.
- `remaprx-target-favicon.svg`: blue-on-yellow favicon draft.
- `remaprx-target-favicon-{16,32,48,180,512}.png`: inspection sizes.
- `build-preview.mjs`: reproducible vector construction and raster exports.

Prior drafts remain in `../target-round-3/` and `../sketch-round-2/`. The current files are review assets only; no site identity, public favicon or deployment is changed. Final owner assessment and production integration remain pending.

Validation: comparison sheet visually inspected; native 16/32-pixel samples included on light/dark backgrounds. Small-size detail loss is visible and accepted as a design tradeoff by the owner's direction, not claimed to be eliminated. SVG parsing and PNG dimensions checked. Run from the application root: `node assets/brand-concepts/mapping-round-4/build-preview.mjs`.
