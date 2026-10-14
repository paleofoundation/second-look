import {Fragment} from 'react';
import {articleUpdateDate, articleUpdatesForPath, pageCreatedDate} from '@/lib/update-history';
import './update-history.css';

const changeLabels = {
  presentation: 'Presentation',
  evidence: 'Evidence update',
  correction: 'Correction',
  'new-page': 'New page',
};

/** Timeline structure adapted from Microbiome Medicine's .mbio-update-history. */
export function UpdateHistory({pagePath, sectionIds = []}: {
  pagePath: string;
  sectionIds?: string[];
}) {
  const entries = articleUpdatesForPath(pagePath);
  const created = pageCreatedDate(pagePath);
  if (!entries.length && !created) return <p>No material content updates have been recorded for this page yet.</p>;

  const availableSections = new Set(sectionIds);
  return <div className="mbio-update-history">
    <div className="mbio-update-history__content">
      {entries.map(entry => {
        const affected = (entry.affectedSections || []).filter(section => availableSections.has(section.id));
        return <div className="mbio-card" key={entry.id} data-update-id={entry.id}>
          <div className="mbio-card__border" aria-hidden="true"/>
          <p className="mbio-card__date"><time dateTime={entry.date}>{articleUpdateDate(entry.date)}</time></p>
          <h3 className="mbio-card__title">{entry.title}{' '}
            <span className="mbio-card__type">{changeLabels[entry.changeType]}</span>
          </h3>
          <div className="mbio-card__content">
            <p>{entry.summary}</p>
            {affected.length ? <p className="mbio-card__links">Sections: {affected.map((section, index) => <Fragment key={section.id}>
              {index ? ' · ' : ''}<a href={`#${section.id}`}>{section.label}</a>
            </Fragment>)}</p> : null}
            {entry.references?.length ? <p className="mbio-card__links">Sources: {entry.references.map((reference, index) => <Fragment key={reference.href}>
              {index ? ' · ' : ''}<a href={reference.href}>{reference.label}</a>
            </Fragment>)}</p> : null}
            {entry.reviewedBy ? <p className="mbio-card__reviewer">Reviewed by {entry.reviewedBy}</p> : null}
          </div>
        </div>;
      })}
      {created ? <div className="mbio-card" key="page-created" data-update-id="page-created">
        <div className="mbio-card__border" aria-hidden="true"/>
        <p className="mbio-card__date"><time dateTime={created}>{articleUpdateDate(created)}</time></p>
        <h3 className="mbio-card__title">Page created</h3>
      </div> : null}
    </div>
  </div>;
}
