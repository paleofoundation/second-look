import {FileText} from 'lucide-react';
import type {Question, Source} from '@/lib/peptides';
import {Grade} from './evidence';
import {CitedText} from './cited-text';
import {ResearchPanel, ResearchPanelTrigger, type StudyDetail} from './research-panel';

export function EvidenceTable({questions, references, studies = []}: {questions: Question[]; references: Source[]; studies?: StudyDetail[]}) {
  return <figure className="wp-block-table evidence-table evidence-assessments" role="region" aria-label="Evidence table" tabIndex={0}>
    <table>
      <thead><tr><th scope="col">Outcome and study design</th><th scope="col">Grade</th><th scope="col">Evidence</th></tr></thead>
      <tbody>{questions.map(question => {
        const uniqueSources = [...new Map(question.sources.map(source => [source.url, source])).values()];
        const studyCount = uniqueSources.filter(source => source.kind.startsWith('Primary research')).length;
        const documents = uniqueSources.filter(source => !source.kind.startsWith('Primary research'));
        const documentLabel = documents.every(source => source.kind === 'Regulatory assessment') ? 'regulatory source' : 'other source';
        return <ResearchPanel key={question.id} title={question.outcome} citations={uniqueSources} references={references} question={question} studies={studies.filter(study => question.sources.some(source => source.url === study.source.url))}>
        <tr>
          <td><ResearchPanelTrigger asChild><button className="research-outcome-trigger" type="button">{question.outcome}</button></ResearchPanelTrigger><span className="table-sub"><CitedText sentences={[{text:`${question.evidenceType.replace(/[.!?]$/, '')}.`,sources:uniqueSources}]} references={references}/></span></td>
          <td><Grade grade={question.grade}/></td>
          <td><ResearchPanelTrigger asChild><button className="evidence-count-link" type="button" aria-label={`View evidence for ${question.outcome}`}><FileText aria-hidden="true"/><span>{studyCount>0?`${studyCount} ${studyCount===1?'Study':'Studies'}`:`${documents.length} ${documents.length===1?'Source':'Sources'}`}</span></button></ResearchPanelTrigger>{studyCount>0&&documents.length>0&&<span className="evidence-source-note">+ {documents.length} {documentLabel}{documents.length===1?'':'s'}</span>}</td>
        </tr>
      </ResearchPanel>;})}</tbody>
    </table>
  </figure>;
}
