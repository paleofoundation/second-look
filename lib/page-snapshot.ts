import {content, guideUrl, isPrimarySource, synthesisRows, type Guide, type Source, type SynthesisRow} from './content';
import {mechanismCitationIds, drugMechanismFor} from './mechanisms';
import {wikiTokens} from './wiki-links';
import {isRetiredArticleSection} from '@/components/shared-theme/universal-article';

/** Group explicit identities, never guess trial membership from similar titles. */
export function studyIdentityIndex(sources: Source[], rows: SynthesisRow[]) {
 const parents = new Map<string, string>();
 const find = (key: string): string => {
  const parent = parents.get(key);
  if (!parent) { parents.set(key, key); return key; }
  if (parent === key) return key;
  const root = find(parent); parents.set(key, root); return root;
 };
 const join = (a: string, b: string) => parents.set(find(a), find(b));
 const primary = sources.filter(isPrimarySource);
 const primaryIds = new Set(primary.map(source => source.id));
 for (const source of primary) {
  const id = 'source:' + source.id;
  find(id);
  if (source.familyId) join(id, 'family:' + source.familyId);
  const doi = source.doi?.trim().replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, '').toLowerCase();
  if (doi) join(id, 'doi:' + doi);
  if (source.pmid) join(id, 'pmid:' + source.pmid);
 }
 for (const row of rows) {
  // A multi-study synthesis is not an assertion that all reports share a trial.
  if (row.studyFamilyIds.length !== 1) continue;
  for (const id of row.sourceIds) if (primaryIds.has(id)) join('source:' + id, 'family:' + row.studyFamilyIds[0]);
 }
 return new Map(primary.map(source => [source.id, find('source:' + source.id)]));
}

const identities = studyIdentityIndex(content.sources, synthesisRows);
export type PageSnapshotData = {studies: number; references: number; peers: {id: string; title: string; href: string}[]; peerType: 'Drug' | 'Condition' | null};

/** Counts the page's cited records and source-backed canonical relationships. */
export function pageSnapshotFor(guide: Guide, sources: Source[], citationOrder: string[]): PageSnapshotData {
 const cited = new Set(citationOrder);
 const references = sources.filter(source => cited.has(source.id));
 const primary = references.filter(isPrimarySource);
 const sourceIds = new Set(primary.map(source => source.id));
 const studyIds = new Set(primary.map(source => identities.get(source.id) || 'source:' + source.id));
 const peerType = guide.type === 'Drug' ? 'Condition' : guide.type === 'Condition' ? 'Drug' : null;
 const peers = new Map<string, PageSnapshotData['peers'][number]>();
 const add = (peer?: Guide) => {
  if (!peer || peer.type !== peerType || guideUrl(peer) === guideUrl(guide)) return;
  const id = peer.entityId || guideUrl(peer);
  peers.set(id, {id, title: peer.title, href: guideUrl(peer)});
 };
 if (peerType && guide.entityId) {
  for (const row of synthesisRows) {
   if ((guide.type === 'Drug' ? row.drugId : row.conditionId) !== guide.entityId || !row.sourceIds.some(id => sourceIds.has(id))) continue;
   const peerId = guide.type === 'Drug' ? row.conditionId : row.drugId;
   add(content.guides.find(peer => peer.entityId === peerId && peer.type === peerType));
  }
  // Count source-bound investigations outside the outcome table as well.
  // Only canonical candidate relationships qualify; incidental safety and
  // original-use mentions do not establish an investigated indication.
  const supportedHrefs = new Set<string>();
  const mention = (text: string, ids: string[]) => {
   if (!ids.some(id => sourceIds.has(id))) return;
   wikiTokens(text, guideUrl(guide)).forEach(token => { if (token.href) supportedHrefs.add(token.href); });
  };
  primary.forEach(source => mention(source.title, [source.id]));
  for (const section of [...guide.sections, ...(guide.scopedSections || [])]) {
   if (isRetiredArticleSection(section) || !/overview|benefit|option|intervention|result|evidence|mechanism/i.test(section.label)) continue;
   if (section.sentences) section.sentences.forEach(sentence => mention(sentence.text, sentence.sources));
   else mention(section.paragraph, section.sources);
   for (const question of section.questions || []) {
    mention(question.question, question.sources);
    if (question.sentences) question.sentences.forEach(sentence => mention(sentence.text, sentence.sources));
    else mention(question.answer, question.sources);
   }
  }
  const mechanism = drugMechanismFor(guide);
  for (const question of mechanism?.questions || []) {
   mention(question.title, question.sourceIds);
   if (question.sentences) question.sentences.forEach(sentence => mention(sentence.text, sentence.sources));
   else mention(question.text, question.sourceIds);
  }
  for (const rationale of mechanism?.rationales || []) {
   if ([...rationale.rationale.sourceIds, ...rationale.tested.sourceIds].some(id => sourceIds.has(id))) supportedHrefs.add(rationale.conditionHref);
  }
  // A bare candidate is only a lead. Require either a primary-supported
  // passage above or a primary study shared by both canonical profiles.
  for (const candidate of guide.candidateLinks || []) {
   const peer = content.guides.find(item => guideUrl(item) === candidate.url && item.type === peerType);
   if (!peer) continue;
   if (supportedHrefs.has(candidate.url) || [...peer.sourceIds, ...mechanismCitationIds(peer)].some(id => {
    const study = identities.get(id);
    return study !== undefined && studyIds.has(study);
   })) add(peer);
  }
 }
 return {studies: studyIds.size, references: new Set(references.map(source => source.id)).size,
  peers: [...peers.values()].sort((a, b) => a.title.localeCompare(b.title)), peerType};
}
