import {Fragment, type ReactNode} from 'react';
import type {Source} from '@/lib/content';
import {sourceIntegrity, studyFacts, STUDY_QUESTIONS} from '@/lib/study-presentation';

export type StudyProseRenderer = (text: string, sourceIds: string[]) => ReactNode;

export function StudyFacts({source}: {source: Source}) {
  const facts = studyFacts(source);
  return facts.length ? <div className="study-facts"><dl>{facts.map(fact => <div className="study-facts__pair" key={fact.label}><dt>{fact.label}</dt><dd>{fact.value}</dd></div>)}</dl></div> : null;
}

export function StudyIntegrity({source, renderProse}: {source: Source; renderProse: StudyProseRenderer}) {
  const integrity = sourceIntegrity(source);
  return integrity ? <aside className="study-integrity-notice" aria-label={integrity.label}><h4>{integrity.label}</h4>{renderProse(integrity.text, [source.id])}</aside> : null;
}

/** The public version uses public facts and the existing authored preview only. */
export function StudyPublicSummary({source, renderProse, headingLevel = 4, idPrefix = ''}: {source: Source; renderProse: StudyProseRenderer; headingLevel?: 3 | 4; idPrefix?: string}) {
  const Heading = headingLevel === 3 ? 'h3' : 'h4';
  const sentence=(value:string)=>/[.!?]$/.test(value.trim())?value.trim():value.trim()+'.';
  const question = [source.design, source.intervention ? `Intervention: ${source.intervention}` : '', source.comparator ? `Comparator: ${source.comparator}` : ''].filter((value):value is string=>!!value).map(sentence).join(' ');
  const population = [source.population, source.randomizedN != null ? `Randomized participants: ${source.randomizedN}` : '', source.n != null && source.n !== source.randomizedN ? `Reported sample: ${source.n}` : ''].filter((value):value is string=>!!value).map(sentence).join(' ');
  const answers = [question, population, source.preview, source.decisiveLimit];
  const missing = [
    'The detailed study design and treatment comparison have not yet been summarized.',
    'The study population or experimental model has not yet been summarized.',
    'An authored findings summary is not yet available for this source.',
    'A detailed appraisal of applicability and limitations is not yet available.',
  ];
  return <>{STUDY_QUESTIONS.map((title, index) => <section className="study-question" key={title} id={idPrefix ? `${idPrefix}-${index + 1}` : undefined}>
    <Heading>{title}</Heading>{answers[index] ? renderProse(answers[index]!, [source.id]) : <p className="study-missing">{missing[index]}</p>}
  </section>)}</>;
}

export function StudySourceLocations({locations}: {locations: string[]}) {
  return locations.length ? <details className="study-source-locations"><summary>Source locations</summary>{locations.map((location, index) => <Fragment key={index}><p>{location}</p></Fragment>)}</details> : null;
}
