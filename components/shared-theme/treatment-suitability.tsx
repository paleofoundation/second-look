import type {ReactNode} from 'react';
import {suitabilityCategoryLabels, type SuitabilityRow} from '@/lib/treatment-suitability';

export function TreatmentSuitability({rows, scope, renderStatement}: {
  rows: SuitabilityRow[]; scope: string;
  renderStatement: (row: SuitabilityRow) => ReactNode;
}) {
  return <div className="treatment-suitability">
    <h3>Who should not be considered?</h3>
    <p>Formal contraindications differ from precautions and interactions that require individual review. Being outside a study population does not, by itself, establish a contraindication.</p>
    <table className="clinical-table">
      <caption>{scope}</caption>
      <thead><tr><th scope="col">Treatment / review area</th><th scope="col">Who needs exclusion or further review</th></tr></thead>
      <tbody>{rows.map(row => <tr key={row.id}>
        <th scope="row"><span>{row.drug}</span><span>{row.label}</span><small>{suitabilityCategoryLabels[row.category]}</small></th>
        <td>{renderStatement(row)}</td>
      </tr>)}</tbody>
    </table>
    <p className="small">A short summary cannot clear someone for treatment. The prescriber should check the complete label and medication list for the exact proposed regimen.</p>
  </div>;
}
