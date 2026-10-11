// Page Snapshot box — the canonical ".snapshot" hero card. The captured migration CSS
// flattened it to a translucent-white box with 📄 emoji bullets; the `.snapshot--brand`
// class (globals.css) restores it to an on-brand red card with a darker header and per-row
// SVG icons. Optional `stats` (a taxon page's meta.conditions.summary) adds the
// participants / conditions / evidence rows, Examine "Research Snapshot" style.
const MBTI_DEF =
  " are validated using a dual-evidence logical framework. First, the intervention must realign the condition’s microbiome signature by increasing beneficial taxa that are consistently depleted and reducing pathogenic taxa that are consistently enriched. Second, the intervention must demonstrate measurable clinical benefit. Concordance of these effects in the same context validates the intervention as an MBTI and supports the clinical relevance of the microbiome signature.";

export type SnapshotStats = {
  nConditions: number; nStudies: number; participants: number;
  enriched: number; depleted: number; mixed: number; tier: string;
};

const ico = { fill: "none", stroke: "currentColor", strokeWidth: 1.9, strokeLinecap: "round" as const, strokeLinejoin: "round" as const, className: "snapshot__ico", viewBox: "0 0 24 24", "aria-hidden": true };
const DocIcon = () => (<svg {...ico}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /></svg>);
const PersonIcon = () => (<svg {...ico}><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>);
const GridIcon = () => (<svg {...ico}><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /></svg>);

export function PageSnapshot({ refs, mmas, stats }: { refs: number; mmas: number | null; stats?: SnapshotStats }) {
  return (
    <div className="snapshot snapshot--brand">
      <header className="snapshot__header">
        <h4 className="snapshot__title">Page Snapshot</h4>
        <span className="research-hero__right-meta-tooltip rgbc-tooltip" data-options="position:left" title=".snapshot__tooltip">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" stroke="currentColor" strokeWidth="1.5" className="h-5 w-5" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M11.3 11.3h0a.8.8 0 0 1 1 .8l-.7 2.8a.8.8 0 0 0 1.1.9h0M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0zm-9-3.8h0v0h0v0z" />
          </svg>
        </span>
        <div className="tooltip snapshot__tooltip">
          <div className="tooltip__content">
            <p>
              <a href="/definition/microbiome-targeted-interventions-mbtis">Microbiome-targeted interventions (MBTIs)</a>
              {MBTI_DEF}
            </p>
          </div>
        </div>
      </header>
      <div className="snapshot__content">
        <ul className="snapshot__list">
          {refs > 0 && (
            <li className="snapshot__list-item">
              <DocIcon />
              <a className="snapshot__link" href="#h-references"><span className="js-count-references">{refs}</span> references on this page</a>
            </li>
          )}
          {stats && (
            <li className="snapshot__list-item">
              <PersonIcon />
              <span>{stats.participants.toLocaleString()} participants in {stats.nStudies} studies</span>
            </li>
          )}
          {stats && (
            <li className="snapshot__list-item">
              <GridIcon />
              <a className="snapshot__link" href="#h-conditions">{stats.nConditions} conditions</a>
            </li>
          )}
          {mmas ? (
            <li className="snapshot__list-item js-show-mmas" data-status="reset" data-modal-id="research-diagram-modal">
              <span className="js-count-mmas">{mmas}</span> Identified MMAs
            </li>
          ) : null}
        </ul>
      </div>
    </div>
  );
}
