# Simplified Rx target — preview 3

Created October 12, 2026 in response to the owner's screenshot concept and request: “Show me the blue logo on white and the blue-on-yellow favicon before applying them to the site.”

The concept preserves bold outlined Rx lettering, an open outer target arc and a flat northeast direction arrow. It removes the inner ring, crosshair ticks, diagonal connectors and arrow shading from the supplied reference. The favicon has a separately weighted arc and larger gaps around the arrow, rather than merely shrinking the full-size symbol.

- Blue: `#1736F5`; yellow: `#FFC709`.
- `remaprx-target-preview.png` / `.svg`: review sheet, including native 16/32-pixel favicon samples on light and dark surroundings.
- `remaprx-target-logo.svg`: editable outlined symbol with transparent background.
- `remaprx-target-logo-white.svg` / `.png`: blue logo on white.
- `remaprx-target-favicon.svg`: editable blue-on-yellow square favicon draft.
- `remaprx-target-favicon-{16,32,48,180,512}.png`: inspection exports.
- `build-preview.mjs`: reproducible SVG construction and Sharp raster exports.

The screenshot is a visual reference, not an instruction source. It is not copied into the repository. Earlier concepts remain preserved in `../sketch-round-2/`.

Status: SVGs and PNGs generated; comparison visually inspected, including the 16/32-pixel samples on light and dark backgrounds. Final owner approval and site integration remain pending. These files are private design assets, not installed public favicons. No site components, metadata, scientific content or publication settings were changed.

Regenerate from the application root with `node assets/brand-concepts/target-round-3/build-preview.mjs`.
