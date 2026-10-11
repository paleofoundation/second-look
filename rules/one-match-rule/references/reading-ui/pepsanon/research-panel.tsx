'use client';

import type {ReactNode} from 'react';
import {ChevronDown, X} from 'lucide-react';
import {Sheet, SheetTrigger, SheetContent, SheetTitle, SheetDescription, SheetClose} from '@/components/ui/sheet';
import type {Question, Source} from '@/lib/peptides';
import {CitedText} from './cited-text';

export type StudyDetail = {
  id: string;
  label: string;
  source: Source;
  species: string;
  sentences: string[];
  locators: number[];
  pdfUrl: string;
  hold: boolean;
};

export const ResearchPanelTrigger = SheetTrigger;

export function ResearchPanel({children, title, citations, references, question, studies = [], expandStudy = false}: {
  children: ReactNode;
  title: string;
  citations: Source[];
  references: Source[];
  question?: Question;
  studies?: StudyDetail[];
  expandStudy?: boolean;
}) {
  const ordered = references.filter(reference => citations.some(source => source.url === reference.url));
  return <Sheet>
    {children}
    <SheetContent side="right" className="research-detail-panel" showCloseButton={false}>
      <header className="research-detail-panel__header">
        <div>
          <SheetTitle>{ordered.length} {ordered.length === 1 ? 'source' : 'sources'}</SheetTitle>
          <SheetDescription>{title}</SheetDescription>
        </div>
        <SheetClose className="research-panel-close" aria-label="Close research details"><X aria-hidden="true"/></SheetClose>
      </header>
      <div className="research-detail-panel__body">
        {question && <details className="research-outcome-details">
          <summary>Findings and limitations <ChevronDown aria-hidden="true"/></summary>
          <div>
            <p><CitedText sentences={question.sentences.map(sentence => ({text: sentence.text, sources: sentence.sourceIndexes.map(index => question.sources[index])}))} references={references} linkToSource/></p>
            <dl className="research-facts">
              <dt>Study design</dt><dd>{question.evidenceType}</dd>
              <dt>Population</dt><dd>{question.population}</dd>
              <dt>Formulation / route</dt><dd>{question.route}</dd>
            </dl>
            <p className="research-panel-limitation"><span>Key limitation: </span><CitedText sentences={[{text: question.limitation, sources: question.sources}]} references={references} linkToSource/></p>
          </div>
        </details>}
        <ul className="research-source-list">
          {ordered.map(source => {
            const study = studies.find(record => record.source.url === source.url);
            const isStudy = source.kind.startsWith('Primary research');
            const index = references.findIndex(reference => reference.url === source.url) + 1;
            const citedSentences = question?.sentences.filter(sentence => sentence.sourceIndexes.some(i => question.sources[i].url === source.url));
            return <li key={source.url}>
              <a className="research-source-title" href={source.url} target="_blank" rel="noreferrer">[{index}] {source.title}</a>
              <span className="research-source-meta">{source.kind} · {source.year || `Accessed ${source.accessedAt || '2026-10-03'}`}</span>
              <details className="research-study-details" open={expandStudy || undefined}>
                <summary aria-label={`${isStudy ? 'Study' : 'Source'} details: ${source.title}`}><span>{isStudy ? 'Study' : 'Source'} details</span><ChevronDown aria-hidden="true"/></summary>
                <div className="research-study-details__body">
                  {study ? <>
                    <dl className="research-facts"><dt>Population / model</dt><dd>{study.species}</dd></dl>
                    <p><CitedText sentences={study.sentences.map(text => ({text, sources: [source]}))} references={references} linkToSource/></p>
                    {study.hold && <p className="research-panel-limitation">Animal dose and sample-size claims are withheld pending clarification of the source’s reporting discrepancies.</p>}
                  </> : citedSentences && citedSentences.length > 0 ? <>
                    <h3>Referenced in this assessment</h3>
                    <p><CitedText sentences={citedSentences.map(sentence => ({text: sentence.text, sources: sentence.sourceIndexes.map(i => question!.sources[i])}))} references={references} linkToSource/></p>
                  </> : null}
                  <div className="research-source-links">
                    <a href={source.url} target="_blank" rel="noreferrer">Read original source</a>
                    {(study?.pdfUrl || source.pdfUrl) && <a href={study?.pdfUrl || source.pdfUrl} target="_blank" rel="noreferrer">Read study PDF</a>}
                  </div>
                  {study && <p className="research-page-locators">Relevant PDF pages: {study.locators.join(', ')}.</p>}
                </div>
              </details>
            </li>;
          })}
        </ul>
      </div>
    </SheetContent>
  </Sheet>;
}
