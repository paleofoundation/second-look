from copy import deepcopy
from pathlib import Path
import unittest

from scripts.research_ingest.cli import load
from scripts.research_ingest.source_validation import schema_errors


class MechanismSchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = load(Path(__file__).resolve().parents[2] / 'research/batches/RRX-INGEST-001/schemas/mechanism-candidate.schema.json')
        loc = dict(source_id='S1',source_sha256='a'*64,kind='html',pdf_page=None,native_path='/html/body/section[1]',section='Results',anchor='Figure 1',table=None,figure='Figure 1',row_column=None,quoted_text='The measured activity decreased in the cell model.')
        missing = dict(status='not_extracted',value=None,units=None,reason='Not extracted in this bounded fixture.',source_locators=[])
        step = dict(id='STEP1',statement='Measured activity decreased in the specified cells.',basis='tested',measured_readout=dict(status='reported',value='Activity',units='assay units',reason=None,source_locators=[loc]),result_ids=['R1'],source_locators=[loc],causal_limitations='A cellular assay does not establish patient benefit.')
        mechanism = dict(id='M1',source_ids=['S1'],drug_id='D1',condition_ids=[],context_role='shared_pathway',original_use_boundary='This model finding is separate from the original approved use.',pathway_or_target='Example target',tier='PRIMARY',model=dict(system='Cell culture',species='Mouse',tissue='Fibroblast',experimental_unit='Biological culture',independence_notes='Technical replicates are not separate biological units.'),exposure=dict(molecule='Example drug',formulation=missing,route=missing,concentration=missing,duration=missing),causal_steps=[step],translation_limits=['Cell model; clinical effect not established.'],source_locators=[loc],status='partial',source_integrity='No integrity notice in supplied source.',clinical_benefit_established=False)
        self.payload = dict(schema_version='RRX-MECHANISM-CANDIDATE-1.0',sources=[dict(source_id='S1',canonical_report_id='P1',sha256='a'*64,source_url='https://example.org/source')],mechanisms=[mechanism],verification_state='pending',human_review_status='pending',publication_state='draft')

    def test_executable_schema_rejects_vacuous_and_unrelated_payloads(self):
        self.assertEqual(schema_errors(self.schema,self.payload),[])
        self.assertTrue(schema_errors(self.schema,{}))
        self.assertTrue(schema_errors(self.schema,{'anything':'accepted by descriptive schema'}))

    def test_tested_step_needs_reported_measurement_and_result(self):
        self.payload['mechanisms'][0]['causal_steps'][0]['result_ids']=[]
        self.assertTrue(schema_errors(self.schema,self.payload))
        self.payload['mechanisms'][0]['causal_steps'][0]['basis']='proposed'
        self.assertEqual(schema_errors(self.schema,self.payload),[])

    def test_model_limits_source_locator_and_original_context_required(self):
        for key in ['model','translation_limits','source_locators','original_use_boundary']:
            payload=deepcopy(self.payload); payload['mechanisms'][0].pop(key)
            self.assertTrue(schema_errors(self.schema,payload),key)
        self.payload['mechanisms'][0]['clinical_benefit_established']=True
        self.assertTrue(schema_errors(self.schema,self.payload))


if __name__=='__main__': unittest.main()
