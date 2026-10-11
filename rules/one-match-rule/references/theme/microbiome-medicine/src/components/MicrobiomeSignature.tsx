"use client";
import { useEffect, useMemo, useState } from "react";

type Item = { name: string; value: number; has_info?: boolean; tier?: string; direction?: string; agreementBin?: string; domain?: string };
type ConditionEvidence = {
  nStudies?: number; nExperiments?: number;
  methodMix?: Record<string, number>;
  domainCoverage?: Record<string, { frac: number; glyph: string }>;
  methodMonoculture?: boolean; coverageStrip?: string;
};
const LEVEL_ORDER = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus", "Species"];
const SIGNATURE_DEF =
  "A microbiome signature is defined through a comprehensive approach that integrates differential abundance analysis across multiple datasets, followed by interpretation for biological relevance. This rigorous process ensures that the identified signature is both statistically robust and biologically meaningful. Associations that do not meet statistical significance or lack mechanistic relevance are excluded from the final signature.";

function colorFor(value: number, hasInfo?: boolean): string {
  if (value > 0) return hasInfo ? "#f04c4c" : "#efbdbd";
  if (value < 0) return hasInfo ? "#183fab" : "#b5b9d2";
  return "#cbd5e1";
}

// Circumference-packing layout (identical to the inline chart and the original front.js):
// circles are sized up to 50px, the ring radius grows so neighbours never overlap (5px gap).
const W = 600;
function packed(items: Item[]) {
  const cx = W / 2, cy = W / 2;
  const its = items.map((it) => ({ ...it, radius: 0, angle: 0 }));
  if (!its.length) return { list: [] as (Item & { dx: number; dy: number; lx: number; ly: number; rotDeg: number; leftSide: boolean; txt: string; radius: number })[], vb: `0 0 ${W} ${W}` };
  let maxRaw = 0;
  its.forEach((it) => { it.radius = Math.abs(it.value); if (it.radius > maxRaw) maxRaw = it.radius; });
  const scale = maxRaw > 50 ? 50 / maxRaw : 1;
  let totalSpan = 0;
  its.forEach((it) => { const r = Math.max(Math.round(it.radius * scale), 5); totalSpan += 2 * r + 5; it.radius = r; });
  maxRaw *= scale;
  const baseR = W / 2;
  const ringR = Math.max(baseR * (totalSpan / (2 * Math.PI * baseR)), maxRaw + 5);
  let sumAng = 0;
  for (let i = 0; i < its.length; i++) {
    const a = 2 * Math.asin(Math.max(-1, Math.min(1, (its[i].radius + its[(i + 1) % its.length].radius + 5) / (2 * ringR))));
    its[i].angle = a; sumAng += a;
  }
  const norm = (2 * Math.PI) / sumAng;
  its.forEach((it) => { it.angle *= norm; });
  let angle = -Math.PI / 4; // start at -45deg, clockwise
  let minX = 0, minY = 0, maxX = W, maxY = W;
  const list = its.map((it) => {
    const t = angle, deg = (180 * t) / Math.PI;
    const dx = cx + Math.cos(t) * ringR, dy = cy + Math.sin(t) * ringR;
    const leftSide = deg < -90 && deg > -270;
    const labelR = it.radius + 5;
    const lx = cx + Math.cos(t) * (ringR + labelR), ly = cy + Math.sin(t) * (ringR + labelR);
    const rotDeg = leftSide ? deg + 180 : deg;
    const txt = `[${it.value}] ${it.name}`;
    const tw = txt.length * 6, ex = lx + (leftSide ? -tw : tw);
    minX = Math.min(minX, dx - it.radius, lx, ex); maxX = Math.max(maxX, dx + it.radius, lx, ex);
    minY = Math.min(minY, dy - it.radius, ly - 7); maxY = Math.max(maxY, dy + it.radius, ly + 7);
    angle -= it.angle;
    return { ...it, dx, dy, lx, ly, rotDeg, leftSide, txt };
  });
  const p = Math.ceil(Math.max(-minX, -minY, maxX - W, maxY - W, 0));
  return { list, vb: `${-p} ${-p} ${W + 2 * p} ${W + 2 * p}` };
}

export function MicrobiomeSignature({
  slug,
  title,
  levels,
  studies,
  evidence,
  defaultOpen = false,
}: {
  slug: string;
  title: string;
  levels: Record<string, Item[]>;
  studies: { title: string; url: string }[];
  evidence?: ConditionEvidence;
  defaultOpen?: boolean;
}) {
  const available = LEVEL_ORDER.filter((l) => levels[l]?.length);
  const [open, setOpen] = useState(defaultOpen);
  // Default to Genus (the primary signature level shown in the inline chart), as in the original.
  const [level, setLevel] = useState(available.includes("Genus") ? "Genus" : available[available.length - 1] || available[0]);
  const [active, setActive] = useState<string | null>(null);
  const [detail, setDetail] = useState("");
  const [loading, setLoading] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const [hovered, setHovered] = useState<number | null>(null);

  // The hero "Microbiome Signature" button, the inline chart, the Page-Snapshot "Identified
  // MMAs" row, and the signature nav item all carry data-modal-id="research-diagram-modal".
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const t = (e.target as HTMLElement)?.closest?.('[data-modal-id="research-diagram-modal"]');
      if (t) { e.preventDefault(); setOpen(true); }
    };
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("click", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("click", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, []);

  async function openOrg(name: string) {
    setActive(name);
    setLoading(true);
    setDetail("");
    try {
      const r = await fetch(`/api/organism?slug=${encodeURIComponent(slug)}&name=${encodeURIComponent(name)}`);
      const j = await r.json();
      setDetail(j.html || "<p>No details available.</p>");
    } catch {
      setDetail("<p>Could not load details.</p>");
    }
    setLoading(false);
  }

  // On open, auto-select the first info-bearing organism (positive first) so the modal
  // appears with one MMA already showing its sidebar detail (matches the original).
  useEffect(() => {
    if (!open || active) return;
    const its = levels[level] || [];
    const first =
      its.find((x) => x.has_info && x.value > 0) ||
      its.find((x) => x.has_info && x.value < 0) ||
      its.find((x) => x.has_info);
    if (first) openOrg(first.name);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  const { list, vb } = useMemo(() => packed(levels[level] || []), [levels, level]);
  const activeItem = useMemo(() => {
    if (!active) return null;
    for (const L of LEVEL_ORDER) { const f = (levels[L] || []).find((x) => x.name === active); if (f) return f; }
    return null;
  }, [active, levels]);

  if (!open) return null;

  return (
    <div
      onClick={(e) => { if (e.target === e.currentTarget) setOpen(false); }}
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,.55)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}
    >
      <div role="dialog" aria-label={`Microbiome signature for ${title}`} style={{ background: "#fff", borderRadius: 12, maxWidth: 1180, width: "100%", maxHeight: "94vh", overflow: "auto", display: "flex", flexWrap: "wrap", position: "relative" }}>
        <button
          onClick={() => setOpen(false)}
          aria-label="Close"
          style={{ position: "absolute", top: 12, right: 14, border: "none", background: "transparent", fontSize: "1.6rem", lineHeight: 1, cursor: "pointer", color: "#888", zIndex: 2 }}
        >
          ✕
        </button>

        <div style={{ flex: "1 1 620px", minWidth: 0, padding: 0 }}>
          <div style={{ position: "relative" }}>
            <div style={{ background: "#cc3333", color: "#fff", padding: ".7rem 1.25rem", display: "flex", alignItems: "center", justifyContent: "center", gap: ".5rem", fontFamily: "var(--font-serif)", fontSize: "1.1rem", borderRadius: "12px 0 0 0" }}>
              <span
                onMouseEnter={() => setShowInfo(true)}
                onMouseLeave={() => setShowInfo(false)}
                aria-label="What is a microbiome signature?"
                style={{ cursor: "pointer", border: "1.5px solid #fff", borderRadius: "50%", width: 18, height: 18, display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: ".72rem", fontStyle: "italic", flexShrink: 0, fontFamily: "var(--font-sans)" }}
              >i</span>
              Relative Abundance ({level})
            </div>
            {showInfo && (
              <div style={{ position: "absolute", top: "calc(100% - 4px)", left: 16, zIndex: 5, background: "#fff", color: "#222", padding: "1.1rem 1.35rem", borderRadius: 8, boxShadow: "0 14px 34px rgba(0,0,0,.24)", maxWidth: 400, fontSize: ".88rem", lineHeight: 1.55 }}>
                {SIGNATURE_DEF}
              </div>
            )}
          </div>
          <div style={{ padding: "1.25rem 1.5rem" }}>
            <svg viewBox={vb} style={{ width: "100%", height: "auto", display: "block" }}>
              {list.map((it, i) => {
                const col = colorFor(it.value, it.has_info);
                const lit = active === it.name || hovered === i;
                return (
                  <g
                    key={i}
                    style={{ cursor: it.has_info ? "pointer" : "default", transition: "opacity .15s" }}
                    onClick={() => it.has_info && openOrg(it.name)}
                    onMouseEnter={() => setHovered(i)}
                    onMouseLeave={() => setHovered(null)}
                  >
                    <circle cx={it.dx} cy={it.dy} r={it.radius} fill={col} fillOpacity={lit ? 1 : 0.4} stroke={active === it.name ? "#000" : "none"} strokeWidth={2} />
                    <text x={it.lx} y={it.ly} fontSize={11} fill={col} fillOpacity={lit ? 1 : 0.7} textAnchor={it.leftSide ? "end" : "start"} dominantBaseline="middle" transform={`rotate(${it.rotDeg} ${it.lx} ${it.ly})`}>{it.txt}</text>
                  </g>
                );
              })}
            </svg>
            <div style={{ display: "flex", gap: ".35rem", flexWrap: "wrap", justifyContent: "center", marginTop: ".85rem" }}>
              {available.map((l) => (
                <button key={l} onClick={() => setLevel(l)} style={{ padding: ".3rem .7rem", borderRadius: 6, border: "1px solid #e5e7eb", background: l === level ? "#cc3333" : "#fff", color: l === level ? "#fff" : "#333", fontSize: ".78rem", cursor: "pointer" }}>{l}</button>
              ))}
            </div>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center", fontSize: ".72rem", marginTop: ".75rem", color: "#444" }}>
              <span style={{ color: "#f04c4c" }}>● Increased (info)</span>
              <span style={{ color: "#efbdbd" }}>● Increased</span>
              <span style={{ color: "#183fab" }}>● Decreased (info)</span>
              <span style={{ color: "#b5b9d2" }}>● Decreased</span>
            </div>
          </div>
        </div>

        <div style={{ flex: "1 1 300px", minWidth: 0, borderLeft: "1px solid #eee", padding: "1.5rem", background: "#fafafa" }}>
          {evidence && (
            <div style={{ border: "1px solid #e5e7eb", borderRadius: 8, background: "#fff", padding: ".8rem .9rem", marginBottom: "1.1rem", fontSize: ".8rem", lineHeight: 1.5, color: "#374151" }}>
              <div style={{ fontFamily: "var(--font-serif)", color: "#cc3333", fontSize: ".98rem", marginBottom: ".35rem" }}>Evidence &amp; Coverage</div>
              {evidence.domainCoverage && (
                <div style={{ marginBottom: ".3rem" }}>
                  Detection coverage:{" "}
                  {Object.entries(evidence.domainCoverage).map(([d, c], i) => (
                    <span key={d} title={`${(c.frac * 100).toFixed(0)}% capable`} style={{ whiteSpace: "nowrap" }}>
                      {i ? " · " : ""}{d} <span style={{ color: c.glyph === "●" ? "#166534" : c.glyph === "◐" ? "#b45309" : "#b91c1c" }}>{c.glyph}</span>
                    </span>
                  ))}
                </div>
              )}
              {evidence.methodMix && (
                <div style={{ color: "#6b7280", marginBottom: ".3rem" }}>
                  Methods: {Object.entries(evidence.methodMix).map(([m, n], i) => `${i ? ", " : ""}${m}×${n}`)}
                </div>
              )}
              <div style={{ color: "#6b7280" }}>
                {evidence.domainCoverage && evidence.domainCoverage.Fungi && evidence.domainCoverage.Fungi.frac < 0.1
                  ? "Fungi were barely assayed here — a taxon's absence means “not measured,” not “not present.” "
                  : ""}
                Certainty reflects observational association, not causation.
              </div>
            </div>
          )}
          {active ? (
            <>
              <h4 style={{ fontFamily: "var(--font-serif)", fontSize: "1.15rem", marginBottom: ".3rem", color: "#cc3333" }}>{active}</h4>
              {activeItem?.tier && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: ".35rem", alignItems: "center", marginBottom: ".6rem", fontSize: ".74rem" }}>
                  <span style={{ background: "#eef1f4", border: "1px solid #e5e7eb", borderRadius: 999, padding: ".08rem .5rem", color: activeItem.tier === "High" || activeItem.tier === "Moderate" ? "#111827" : "#6b7280" }}>{activeItem.tier} certainty</span>
                  {activeItem.direction && <span style={{ color: "#4b5563" }}>{activeItem.direction === "increased" ? "↑ increased" : activeItem.direction === "decreased" ? "↓ decreased" : "↕ mixed"}</span>}
                  {activeItem.agreementBin && <span style={{ color: "#6b7280" }}>· {activeItem.agreementBin} agreement</span>}
                  {activeItem.domain && activeItem.domain !== "Unknown" && <span style={{ color: "#6b7280" }}>· {activeItem.domain}</span>}
                </div>
              )}
              {loading ? <p>Loading…</p> : <div className="organism-detail" dangerouslySetInnerHTML={{ __html: detail }} />}
            </>
          ) : (
            <p style={{ color: "#6b7280" }}>Select a highlighted organism (solid dot) to see its detail panel.</p>
          )}
          {studies.length > 0 && (
            <details open style={{ marginTop: "1.25rem", borderTop: "1px solid #e5e7eb", paddingTop: "1rem" }}>
              <summary style={{ color: "#cc3333", fontFamily: "var(--font-serif)", fontSize: "1.05rem", cursor: "pointer" }}>Studies</summary>
              <ul style={{ margin: ".6rem 0 0", paddingLeft: "1.1rem", maxHeight: 260, overflowY: "auto", fontSize: ".82rem", lineHeight: 1.5 }}>
                {studies.map((s, i) => (
                  <li key={i} style={{ marginBottom: ".45rem" }}>
                    <a href={s.url} target="_blank" rel="noreferrer" style={{ color: "#cc3333", textDecoration: "none" }}>{s.title}</a>
                  </li>
                ))}
              </ul>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
