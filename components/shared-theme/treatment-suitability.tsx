import type {ReactNode} from 'react';
import {ContraindicationsInfo} from '@/components/contraindications-info';
import {suitabilityCategoryLabels, type SuitabilityRow} from '@/lib/treatment-suitability';

export function TreatmentSuitability({rows, scope, renderStatement, showHeading = true}: {
  rows: SuitabilityRow[]; scope: string; showHeading?: boolean;
  renderStatement: (row: SuitabilityRow) => ReactNode;
}) {
  return <div className="treatment-suitability">
    {showHeading?<h3 className="status-heading">Who should not be considered?<ContraindicationsInfo scope={scope}/></h3>:null}
    <table className="clinical-table">
      <caption className="sr-only">Treatment suitability</caption>
      <thead><tr><th scope="col">Treatment / review area</th><th scope="col">Who needs exclusion or further review</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.id}>
        <th scope="row"><span>{row.drug}</span><span>{row.label}</span><small>{suitabilityCategoryLabels[row.category]}</small></th>
        <td>{renderStatement(row)}</td>
      </tr>)}</tbody>
    </table>
  </div>;
}
