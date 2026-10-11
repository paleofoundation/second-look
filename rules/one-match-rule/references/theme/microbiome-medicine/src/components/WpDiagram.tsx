"use client";
import { useEffect } from "react";

// Renders the inline "Microbiome Signature" preview chart that the original
// front.js drew into the empty <svg class="js-research-diagram-layout"> inside
// .js-research-diagram-preview. Ports front.js's exact draw() algorithm so the
// inline preview is pixel-identical. Clicking the wrapper opens the full modal
// (handled by MicrobiomeSignature via the data-modal-id hook).

type Item = { name: string; value: number; has_info?: boolean; radius: number; angle: number };

const NS = "http://www.w3.org/2000/svg";

function colorFor(value: number, hasInfo?: boolean): string {
  const known = !!hasInfo;
  const pos = value >= 0;
  if (known) return pos ? "#f04c4c" : "#183fab";
  return pos ? "#efbdbd" : "#b5b9d2";
}

export function WpDiagram() {
  useEffect(() => {
    const preview = document.querySelector<HTMLElement>(".js-research-diagram-preview");
    if (!preview) return;
    // Clicking the inline chart opens the full signature modal (global data-modal-id hook).
    preview.setAttribute("data-modal-id", "research-diagram-modal");
    preview.style.cursor = "pointer";
    const svg = preview.querySelector<SVGSVGElement>("svg.js-research-diagram-layout");
    if (!svg || svg.childElementCount > 0) return;

    let items: Item[];
    try {
      items = JSON.parse(svg.getAttribute("data-items") || "[]");
    } catch {
      return;
    }
    if (!items.length) return;

    const W = parseInt(svg.getAttribute("data-size") || "500", 10);
    const H = W;
    const cx = W / 2;
    const cy = H / 2;

    // radii = |value|, capped so the largest is <=50, each floored at 5
    let maxRaw = 0;
    items.forEach((it) => { it.radius = Math.abs(it.value); if (it.radius > maxRaw) maxRaw = it.radius; });
    const scale = maxRaw > 50 ? 50 / maxRaw : 1;
    let totalSpan = 0;
    items.forEach((it) => { const r = Math.max(Math.round(it.radius * scale), 5); totalSpan += 2 * r + 5; it.radius = r; });
    maxRaw *= scale;

    // ring radius from circumference packing
    const baseR = Math.min(W / 2, H / 2);
    const ratio = totalSpan / (2 * Math.PI * baseR);
    const ringR = Math.max(baseR * ratio, maxRaw + 5);

    // per-item angular span proportional to size, normalized to fill 2π
    let sumAng = 0;
    for (let i = 0; i < items.length; i++) {
      const rA = items[i].radius;
      const rB = items[(i + 1) % items.length].radius;
      const a = 2 * Math.asin(Math.max(-1, Math.min(1, (rA + rB + 5) / (2 * ringR))));
      items[i].angle = a;
      sumAng += a;
    }
    const norm = (2 * Math.PI) / sumAng;
    items.forEach((it) => { it.angle *= norm; });

    let angle = -Math.PI / 4; // start at -45°, decrement per item (clockwise)
    let minX = 0, minY = 0, maxX = W, maxY = H;

    for (const it of items) {
      const t = angle;
      const deg = (180 * t) / Math.PI;
      const r = it.radius;
      const color = colorFor(it.value, it.has_info);
      const dx = cx + Math.cos(t) * ringR;
      const dy = cy + Math.sin(t) * ringR;

      const circle = document.createElementNS(NS, "circle");
      circle.setAttribute("cx", String(dx));
      circle.setAttribute("cy", String(dy));
      circle.setAttribute("r", String(r));
      circle.setAttribute("fill", color);
      circle.setAttribute("class", "diagram-circle");
      svg.appendChild(circle);

      const leftSide = deg < -90 && deg > -270;
      const labelR = r + 5;
      const lx = cx + Math.cos(t) * (ringR + labelR);
      const ly = cy + Math.sin(t) * (ringR + labelR);
      const rotDeg = leftSide ? deg + 180 : deg;
      const txt = `[${it.value}] ${it.name}`;

      const label = document.createElementNS(NS, "text");
      label.setAttribute("x", String(lx));
      label.setAttribute("y", String(ly));
      label.setAttribute("fill", color);
      label.setAttribute("class", "diagram-label");
      label.setAttribute("font-size", "10");
      label.setAttribute("font-weight", "500");
      label.setAttribute("dominant-baseline", "middle");
      label.setAttribute("text-anchor", leftSide ? "end" : "start");
      label.setAttribute("transform", `rotate(${rotDeg}, ${lx}, ${ly})`);
      label.textContent = txt;
      svg.appendChild(label);

      const tw = txt.length * 6;
      const ex = lx + (leftSide ? -tw : tw);
      minX = Math.min(minX, dx - r, lx, ex);
      maxX = Math.max(maxX, dx + r, lx, ex);
      minY = Math.min(minY, dy - r, ly - 7);
      maxY = Math.max(maxY, dy + r, ly + 7);

      angle -= it.angle;
    }

    const p = Math.ceil(Math.max(-minX, -minY, maxX - W, maxY - H, 0));
    svg.setAttribute("viewBox", `${-p} ${-p} ${W + 2 * p} ${H + 2 * p}`);
    svg.removeAttribute("width");
    svg.removeAttribute("height");
    svg.style.maxWidth = "600px";
    svg.style.width = "100%";
    svg.style.height = "auto";
  }, []);
  return null;
}
