/** Reader copy is derived from evidence gaps; private work instructions never cross this boundary. */
export function readerEvidenceStatus(internalAction: string) {
  let readerSummary = 'The available evidence is incomplete and has not been independently reviewed.';
  let readerNextStep = 'Complete source coverage and an assessment of the studies’ methods, findings and relevance to this question.';
  if (/no human clinical report|no sources|0 sources/i.test(internalAction)) {
    readerSummary = 'No human clinical report was identified in the sources checked. This does not establish that no relevant study exists.';
    readerNextStep = 'A broader source search and assessment of any relevant original studies.';
  } else if (/paywall|full.text|library\/ILL/i.test(internalAction)) {
    readerSummary = 'Some relevant reports are unavailable in full text, which limits assessment of their methods and findings.';
    readerNextStep = 'The complete original reports, including relevant supplements, and an independent assessment.';
  }
  if (/retract|correction|republ/i.test(internalAction)) {
    readerSummary = 'A correction or retraction affects the source record. The affected findings cannot support a settled conclusion.';
    readerNextStep = 'The corrected report and an assessment of how the notice changes its findings.';
  }
  return {readerSummary, readerNextStep};
}
