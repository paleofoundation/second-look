"use client";
import { useState } from "react";
import { StudyDrawer, type DrawerRow, type DrawerStudy } from "./StudyDrawer";

type Row = {
  condition: string;
  direction: "enriched" | "depleted" | "mixed";
  grade: string; score: number; magnitude: number;
  nStudies: number; participants: number; studies: DrawerStudy[];
};
type Data = {
  taxon: string;
  summary: { nConditions: number; nStudies: number; participants: number; tier: string; agreement: number; enriched: number; depleted: number; mixed: number };
  rows: Row[];
};

const GRADE_INFO = "Grade is reflected by a gradient of red. Deep red is strong evidence, pale pink is weaker evidence, set by the strongest single study's methodology weight (w = A·D·S·C·R: method aperture · design · statistics · cohort size · contamination control). It grades how the finding was measured, not how important the organism is.";
const EFFECT_INFO = "Effect arrows show how strong and consistent the enrichment (red, up) or depletion (blue, down) signal is across studies. This serves as a proxy for evidence weight and replication, not a measured effect size. Select any row for the studies behind it.";

// Header info tooltip — a white brand tooltip on hover/focus (matches the site's .tooltip look).
function InfoTip({ label, text }: { label: string; text: string }) {
  return (
    <span className="mbio-info">
      <button type="button" className="mbio-info__btn" aria-label={`About ${label}`}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></svg>
      </button>
      <span className="mbio-info__pop" role="tooltip">{text}</span>
    </span>
  );
}

// Grade = a gradient of brand red. Saturated (deep red) = strong evidence; pale pink = weak.
// Delivered via CSS vars (consumed by .mbio-cond .mbio-grade) so a dev-injected sheet can't
// flatten the dynamic background the way it does a plain inline `background`.
function gradeStyle(score: number): React.CSSProperties {
  const t = Math.max(0, Math.min(1, (score - 0.3) / 0.62));
  const lerp = (a: number, b: number) => Math.round(a + (b - a) * t);
  const bg = `rgb(${lerp(0xf2, 0xa0)}, ${lerp(0xd3, 0x1f)}, ${lerp(0xd3, 0x1f)})`;
  return { ["--g-bg"]: bg, ["--g-fg"]: t > 0.42 ? "#fff" : "#7a1616" } as React.CSSProperties;
}

const ARROW_UP = "M8 1.5 14 9h-3.6v5.5H5.6V9H2z";
function Arrow({ dir, active, color }: { dir: "up" | "down"; active: boolean; color: string }) {
  return (
    <svg viewBox="0 0 16 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <path d={ARROW_UP} transform={dir === "down" ? "rotate(180 8 10)" : undefined} fill={active ? color : "#e6d6d6"} />
    </svg>
  );
}
// Effect arrows encode how STRONG + consistent the signal is (evidence weight × replication),
// not a measured effect size — the corpus carries no per-taxon effect sizes.
function EffectArrows({ direction, magnitude }: { direction: Row["direction"]; magnitude: number }) {
  const cap = magnitude >= 3 ? "Strong" : magnitude >= 2 ? "Moderate" : "Weak";
  if (direction === "mixed") {
    return (
      <div className="mbio-eff">
        <span className="mbio-eff__arrows"><Arrow dir="up" active color="#9aa0ac" /><Arrow dir="down" active color="#9aa0ac" /></span>
        <span className="mbio-eff__cap">Conflicting</span>
      </div>
    );
  }
  const up = direction === "enriched";
  const strong = up ? "#cc3333" : "#183fab";
  const faint = up ? "#e7cccc" : "#ccd2e6";
  return (
    <div className="mbio-eff">
      <span className="mbio-eff__arrows">
        {[0, 1, 2].map((i) => <Arrow key={i} dir={up ? "up" : "down"} active={i < magnitude} color={i < magnitude ? strong : faint} />)}
      </span>
      <span className="mbio-eff__cap">{cap} signal</span>
    </div>
  );
}

function DirectionCell({ direction }: { direction: Row["direction"] }) {
  const label = direction === "enriched" ? "Enriched" : direction === "depleted" ? "Depleted" : "Mixed";
  return (
    <span className={"mbio-cond__dir mbio-cond__dir--" + direction}>
      {direction !== "mixed" && (
        <svg viewBox="0 0 16 20" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d={ARROW_UP} transform={direction === "depleted" ? "rotate(180 8 10)" : undefined} fill="currentColor" />
        </svg>
      )}
      {label}
    </span>
  );
}

const DocIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>
);
const PersonIcon = () => (
  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
);

export function ConditionsTable({ data }: { data: Data }) {
  const [open, setOpen] = useState<DrawerRow | null>(null);
  return (
    <div className="mbio-cond">
      <div className="mbio-cond__wrap">
        <div className="mbio-cond__grid" role="table" aria-label={`Conditions where ${data.taxon} is differentially abundant`}>
          <div className="mbio-cond__head" role="row">
            <div role="columnheader">Condition</div>
            <div role="columnheader">Direction</div>
            <div role="columnheader">Grade<InfoTip label="Grade" text={GRADE_INFO} /></div>
            <div role="columnheader">Effect<InfoTip label="Effect" text={EFFECT_INFO} /></div>
            <div role="columnheader">Evidence</div>
          </div>
          {data.rows.map((r) => (
            <button
              key={r.condition}
              type="button"
              className="mbio-cond__row"
              role="row"
              onClick={() => setOpen(r)}
              aria-label={`${r.condition}: open ${r.nStudies} stud${r.nStudies === 1 ? "y" : "ies"}`}
            >
              <div className="mbio-cond__c-cond" role="cell">
                {r.condition}
                {r.studies.some((x) => x.caveats.length > 0) && <span className="mbio-cond__flag" title="Detection caveats, see study details">ⓘ</span>}
              </div>
              <div role="cell"><DirectionCell direction={r.direction} /></div>
              <div role="cell"><span className="mbio-grade" style={gradeStyle(r.score)} title={`Grade ${r.grade}`}>{r.grade}</span></div>
              <div role="cell"><EffectArrows direction={r.direction} magnitude={r.magnitude} /></div>
              <div className="mbio-cond__ev" role="cell">
                <span className="mbio-cond__studies"><DocIcon /><span>{r.nStudies} Stud{r.nStudies === 1 ? "y" : "ies"}</span></span>
                <span className="mbio-cond__parts"><PersonIcon /> Participants: {r.participants.toLocaleString()}</span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <StudyDrawer row={open} onClose={() => setOpen(null)} />
    </div>
  );
}
