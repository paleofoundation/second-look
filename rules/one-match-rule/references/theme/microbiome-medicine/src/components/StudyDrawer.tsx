"use client";
import { useEffect, useState } from "react";
import { createPortal } from "react-dom";

export type DrawerStudy = {
  title: string; journal: string; year: string; design: string;
  participants: number; site: string; method: string;
  direction: "enriched" | "depleted"; grade: string; paper: string; caveats: string[];
  url?: string; // our internal research-feed summary page (/research-feeds/<slug>)
};
export type DrawerRow = {
  condition: string; direction: "enriched" | "depleted" | "mixed";
  nStudies: number; participants: number; studies: DrawerStudy[];
};

const titleCase = (s: string) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : s);
const fmtDesign = (s: string) => s.split(",").map((p) => titleCase(p.trim())).filter(Boolean).join(", ");
const dirWord = (d: string) =>
  d === "enriched" ? "Enriched (higher in cases)"
  : d === "depleted" ? "Depleted (lower in cases)"
  : "Mixed across studies";

function KV({ k, v }: { k: string; v: string }) {
  return (
    <div className="mbio-kv__row">
      <span className="mbio-kv__k">{k}</span>
      <span className="mbio-kv__v">{v}</span>
    </div>
  );
}

function StudyCard({ s, primary }: { s: DrawerStudy; primary: boolean }) {
  // We reviewed every study behind these signatures, so the study name links to our own
  // research-feed summary page (internal) and sits BELOW the summary, not above it.
  const href = s.url || s.paper;
  const internal = !!s.url;
  return (
    <div className="mbio-study">
      {primary && (
        <div className="mbio-study__band"><span className="mbio-study__band-title">Study Summary</span></div>
      )}
      <div className="mbio-kv">
        <KV k="Effect" v={dirWord(s.direction)} />
        {s.design && <KV k="Trial Design" v={fmtDesign(s.design)} />}
        {s.participants > 0 && <KV k="Participants" v={String(s.participants)} />}
        {s.site && <KV k="Body Site" v={s.site} />}
        {s.method && <KV k="Method" v={s.method} />}
        {(s.journal || s.year) && <KV k="Source" v={[s.journal, s.year].filter(Boolean).join(" · ")} />}
        <KV k="Grade" v={s.grade} />
      </div>
      {s.caveats.length > 0 && (
        <div className="mbio-study__caveat">{s.caveats.map((c) => c.charAt(0).toUpperCase() + c.slice(1)).join(". ")}.</div>
      )}
      {href ? (
        <a className="mbio-study__title mbio-study__title--below" href={href} {...(internal ? {} : { target: "_blank", rel: "noreferrer" })}>{s.title}</a>
      ) : (
        <span className="mbio-study__title mbio-study__title--below">{s.title}</span>
      )}
    </div>
  );
}

export function StudyDrawer({ row, onClose }: { row: DrawerRow | null; onClose: () => void }) {
  const [expanded, setExpanded] = useState(false);
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  useEffect(() => {
    const h = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    document.addEventListener("keydown", h);
    return () => document.removeEventListener("keydown", h);
  }, [onClose]);
  useEffect(() => { setExpanded(false); }, [row]);

  if (!mounted) return null;
  const extra = row ? row.studies.slice(1) : [];
  // Portal to <body> so position:fixed anchors to the viewport (not a transformed ancestor)
  // and the drawer's own styling isn't overridden by .entry-content link rules.
  return createPortal(
    <div className={"mbio-drawer-root" + (row ? " mbio-drawer--open" : "")} aria-hidden={!row}>
      <div className="mbio-drawer__backdrop" onClick={onClose} />
      <aside className="mbio-drawer" role="dialog" aria-modal="true" aria-label="Study details">
        {row && (
          <>
            <div className="mbio-drawer__head">
              <h3 className="mbio-drawer__title">{row.nStudies} Stud{row.nStudies === 1 ? "y" : "ies"} Found</h3>
              <button className="mbio-drawer__close" onClick={onClose} aria-label="Close study drawer">×</button>
            </div>
            <p className="mbio-drawer__sub">{row.condition} · {row.participants.toLocaleString()} participants</p>
            <div className="mbio-drawer__divider" />
            {row.studies[0] && <StudyCard s={row.studies[0]} primary />}
            {extra.length > 0 && (
              <>
                <button className="mbio-cond__studies" onClick={() => setExpanded((v) => !v)} style={{ margin: "0.4rem 0 1rem" }}>
                  <span>{expanded ? "Hide" : "Show"} {extra.length} additional stud{extra.length === 1 ? "y" : "ies"}</span>
                </button>
                {expanded && extra.map((s, i) => <StudyCard key={i} s={s} primary={false} />)}
              </>
            )}
          </>
        )}
      </aside>
    </div>,
    document.body
  );
}
