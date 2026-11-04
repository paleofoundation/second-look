import {SectionInfo} from '@/components/section-info';

export function ContraindicationsInfo({scope}: {scope?: string}) {
 return <SectionInfo label="About contraindications">
  <p>Formal contraindications differ from precautions and interactions that require individual review. Being outside a study population does not, by itself, establish a contraindication.</p>
  <p>{scope || 'Product, formulation, indication and jurisdiction matter. This is not the complete label or an interaction checker.'}</p>
  <p>A short summary cannot clear someone for treatment. The prescriber should check the complete label and medication list for the exact proposed regimen.</p>
 </SectionInfo>;
}
