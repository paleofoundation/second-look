import { z } from 'zod';

const text = z.string().trim().min(1).max(20000);
const id = z.string().regex(/^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/);
const citations = z.array(id).max(100).default([]);
export const guideBlockSchema = z.discriminatedUnion('type', [
  z.object({ type: z.literal('paragraph'), text, sourceIds: citations }).strict(),
  z.object({ type: z.literal('callout'), title: text, text, sourceIds: citations }).strict(),
  z.object({ type: z.literal('list'), items: z.array(text).min(1).max(100), sourceIds: citations }).strict(),
  z.object({ type: z.literal('table'), caption: text, columns: z.array(text).min(1).max(8), rows: z.array(z.array(text).min(1).max(8)).min(1).max(100), sourceIds: citations }).strict(),
  z.object({ type: z.literal('questions'), title: text, items: z.array(text).min(1).max(100), sourceIds: citations }).strict(),
]);
/** Plain data only: the private reader never executes manuscript HTML or Markdown. */
export const guideManuscriptSchema = z.object({
  schemaVersion: z.literal(1), productId: id, editionId: id, version: text,
  title: text, description: text, evidenceCutoff: z.string().regex(/^\d{4}-\d{2}-\d{2}$/), updatedAt: z.string().datetime(),
  medicalNotice: text, changeSummary: text,
  contributors: z.array(z.object({ name: text, role: text, qualifications: text.optional(), conflicts: text, orcid: z.string().regex(/^https:\/\/orcid.org\/\d{4}-\d{4}-\d{4}-\d{3}[\dX]$/).optional() }).strict()).min(1).max(40),
  chapters: z.array(z.object({ id, title: text, blocks: z.array(guideBlockSchema).min(1).max(300) }).strict()).min(1).max(60),
  references: z.array(z.object({ id, title: text, url: z.string().url().refine(value => value.startsWith('https://')), note: text.optional() }).strict()).max(1000),
}).strict().superRefine((value, ctx) => {
  const refs = new Set(value.references.map(ref => ref.id));
  if (refs.size !== value.references.length || new Set(value.chapters.map(chapter => chapter.id)).size !== value.chapters.length) ctx.addIssue({ code: 'custom', message: 'Reference and chapter identities must be unique.' });
  for (const chapter of value.chapters) for (const block of chapter.blocks) {
    if (block.sourceIds.some(source => !refs.has(source))) ctx.addIssue({ code: 'custom', message: 'Every citation must resolve to a guide reference.' });
    if (block.type === 'table' && block.rows.some(row => row.length !== block.columns.length)) ctx.addIssue({ code: 'custom', message: 'Table rows must match column headings.' });
  }
});
export type GuideManuscript = z.infer<typeof guideManuscriptSchema>;
