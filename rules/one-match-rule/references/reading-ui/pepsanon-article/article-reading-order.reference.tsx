 const proseSections=guideSections.slice(1,9);
 // Follow the same reading order as the article below, including expanded FAQs.
 const sources=referencesInOrder([
  ...guideSentences(content).flatMap(sentence=>sentence.sources),
  ...qs.flatMap(q=>q.sources),
  ...(isPilot?bpcPilot.studies.map(study=>study.source):[]),
  ...threads.map(t=>({title:t.title,url:t.url,year:t.date,kind:`Community question · r/${t.community}`})),
 ]);
 <section id="overview" data-prose-section><h2 className="wp-block-heading">Overview</h2><p className="answer-paragraph" data-prose><CitedText currentPage={`/peptides/${p.id}`} sentences={content.overview} references={sources}/></p></section>
 {proseSections.map(section=><section key={section.id} id={section.id}><h2 className="wp-block-heading">{section.label}</h2><CanonicalProse currentPage={`/peptides/${p.id}`} blocks={content.sections[section.id]} sources={sources}/></section>)}
 <section id="answers"><h2 className="wp-block-heading">FAQs</h2><GuideFaq currentPage={`/peptides/${p.id}`} questions={[]} entries={content.faqs} sources={sources}/></section>
 <section id="evidence" data-prose-section><h2 className="wp-block-heading">Evidence</h2><p data-prose>{copy.evidence} <a href="/methodology#grading">How we grade evidence.</a></p><EvidenceTable questions={qs} references={sources} studies={isPilot?bpcPilot.studies:[]}/></section>
