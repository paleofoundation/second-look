/** Display validated, source-backed assessments; never derive a grade from a design label. */
export type OutcomeCertainty = {
  label: string; rationale: string; assessmentStatus?: 'assessed' | 'pending' | 'held'; method?: string; scope?: string;
  assessmentKind?: string; assessedAt?: string; sourceIds?: string[]; integrity?: string; reviewStatus?: string;
  domains?: {name:string;text:string;sourceIds:string[]}[]; basis?: {sourceId:string;locator:string}[];
};
export type ConfidenceRow = {
  status: string;
  background: boolean;
  sourceIds: string[];
  limits: { text: string; sourceIds: string[] }[];
  pending: string[];
  certainty?: OutcomeCertainty;
};

export type EvidenceConfidence = Omit<PendingConfidence, 'label' | 'category' | 'nextAction'> & {
  label: string;
  category: PendingConfidence['category'] | 'assessed';
  nextAction?: PendingConfidence['nextAction'];
};

/** A design label never earns a rating. The canonical adapter must supply the
 * completed scoped appraisal, its method, and rationale. Integrity holds win. */
export function describeEvidenceConfidence(row: ConfidenceRow, sources: ConfidenceSource[]): EvidenceConfidence {
  const pending = describePendingConfidence(row, sources);
  const appraisal = row.certainty;
  // An explicit Low editorial assessment can explain compromised evidence while
  // the result remains on correction hold. It never releases the held conclusion.
  const correctionExplained = appraisal?.assessmentKind === 'selected-source-editorial-v1' && appraisal.integrity === 'correction_unresolved' && appraisal.label === 'Low';
  const held = pending.category === 'quarantined' || (pending.category === 'correction_hold' && !correctionExplained) || appraisal?.assessmentStatus === 'held';
  if (!held && appraisal?.assessmentStatus === 'assessed' && appraisal.method?.trim() && appraisal.scope?.trim() && appraisal.rationale.trim() && appraisal.label.trim()) {
    return { label: appraisal.label, category: 'assessed', basis: `${appraisal.method} · ${appraisal.scope}`,
      limitation: { text: appraisal.rationale, sourceIds: [...row.sourceIds], input: 'certainty.rationale' } };
  }
  return pending;
}
export type ConfidenceSource = {
  id: string;
  primary: boolean;
  quarantined?: boolean;
  access?: string;
  status?: string;
  design?: string;
};
export type PendingConfidence = {
  label: 'Confidence not yet rated';
  category: 'quarantined' | 'correction_hold' | 'background' | 'computational' | 'exploratory' | 'abstract' | 'partial_text' | 'randomized' | 'unassessed';
  basis: string;
  limitation: { text: string; sourceIds: string[]; input: string };
  nextAction: { text: string; input: string };
};

export function describePendingConfidence(row: ConfidenceRow, sources: ConfidenceSource[]): PendingConfidence {
  const records = sources.filter(source => row.sourceIds.includes(source.id));
  const state = row.status.toLowerCase().replace(/[\s-]+/g, '_');
  const access = records.map(source => source.access || '').join(' ').toLowerCase();
  let category: PendingConfidence['category'];
  let basis: string;
  let preferredLimit: RegExp | undefined;

  // Source-integrity holds take precedence over design or access labels.
  if (state.includes('quarantin') || records.some(source => source.quarantined || /quarantin|withdrawn/i.test(source.status || ''))) {
    category = 'quarantined'; basis = 'Source excluded from conclusions'; preferredLimit = /quarantin|retract|withdraw/i;
  } else if (state.includes('hold')) {
    category = 'correction_hold'; basis = 'Result remains on hold'; preferredLimit = /correction|provisional|retract/i;
  } else if (row.background) {
    category = 'background'; basis = 'Background sources only';
  } else if (state === 'computational_result') {
    category = 'computational'; basis = 'Computer model; no treatment trial'; preferredLimit = /patient benefit|not tested|neither drug/i;
  } else if (state === 'exploratory') {
    category = 'exploratory'; basis = 'Exploratory analysis';
  } else if (records.length > 0 && records.every(source => /abstract/i.test(source.access || ''))) {
    category = 'abstract'; basis = 'Abstract evidence only'; preferredLimit = /abstract|full text|full report/i;
  } else if (/partial/.test(access)) {
    category = 'partial_text'; basis = 'Incomplete full-text access'; preferredLimit = /snapshot|part of|partial|full text/i;
  } else if (records.some(source => /randomi[sz]ed/i.test(source.design || ''))) {
    category = 'randomized'; basis = 'Randomized trial evidence';
  } else {
    category = 'unassessed'; basis = 'Study appraisal incomplete';
  }

  const limitPattern = preferredLimit || /not extracted|not present|missing|confidence interval|closed early|per-protocol/i;
  const preferredIndex = row.limits.findIndex(limit => limitPattern.test(limit.text));
  const limitIndex = preferredIndex >= 0 ? preferredIndex : row.limits.findIndex(limit => limit.text.trim());
  const recordedLimit = row.limits[limitIndex];
  const limitation = recordedLimit
    ? { text: recordedLimit.text, sourceIds: [...recordedLimit.sourceIds], input: `limits[${limitIndex}]` }
    : { text: 'A row-specific limitation has not been recorded.', sourceIds: [], input: 'missing' };
  // Keep the recorded action verbatim. Prefer a reader-readable action over an internal question-set label.
  const readableIndex = row.pending.findIndex(action => action.trim() && !/Q01|Q1[–-]Q15|universal question/i.test(action));
  const actionIndex = readableIndex >= 0 ? readableIndex : row.pending.findIndex(action => action.trim());
  const nextAction = actionIndex >= 0
    ? { text: row.pending[actionIndex], input: `pending[${actionIndex}]` }
    : { text: 'The next review step has not been recorded.', input: 'missing' };

  return { label: 'Confidence not yet rated', category, basis, limitation, nextAction };
}
