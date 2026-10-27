from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from scripts.research_ingest.cli import Hold, canonical, digest, load, sha
from scripts.research_ingest.source_validation import validate_candidate, validate_source, walk


class SourceCandidateTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2]
        self.schema = load(root / "research/batches/RRX-INGEST-001/schemas/candidate.schema.json")
        self.assignment = {"source_id": "S1", "sha256": "a" * 64, "assignment_id": "ASSIGN-S1",
                           "batch_id": "CAL-1", "canonical_report_id": "P1", "media_type": "application/pdf"}
        loc = {"source_id": "S1", "source_sha256": "a" * 64, "kind": "pdf", "pdf_page": 1,
               "native_path": None, "section": "Results", "anchor": "Table 1", "table": "Table 1",
               "figure": None, "row_column": "row 1, column 2", "quoted_text": "There were 12 events."}
        states = dict(verification_state="pending", human_review_status="pending", publication_state="draft", excluded_from_accepted_support=True)
        result = dict(id="R1", source_id="S1", canonical_report_id="P1", endpoint="Events",
                      endpoint_class="primary", population="Synthetic participants", comparison="A versus B", arms=["A", "B"],
                      timepoint="Day 10", outcome_type="count", estimate_type="count", reported_text="There were 12 events.",
                      numbers=[dict(id="N1", quantity_type="events", value=12, units="events", reported_text="12",
                                    missing_reason=None, source_locators=[deepcopy(loc)])],
                      source_locators=[deepcopy(loc)], missingness={}, analysis_notes="Synthetic test fixture", **states)
        self.candidate = dict(schema_version=self.schema["properties"]["schema_version"]["const"],
                              plan_id=self.schema["properties"]["plan_id"]["const"], plan_sha256="b" * 64,
                              assignment_id="ASSIGN-S1", batch_id="CAL-1", source_id="S1", canonical_report_id="P1", source_sha256="a" * 64,
                              inspection=dict(scope="partial_source", pages_read=[1], total_pages=2, visual_numeric_pages=[1], native_sections_read=[], method="fixture"),
                              source_identity=dict(printed_doi="10.1000/test", observed_type="original_report", evidence_class="human_randomized",
                                                   identity_notes="Synthetic source", applicability="candidate_relevant", applicability_reason="Test scope",
                                                   source_integrity="no_notice_in_supplied_packet"),
                              processing_state="partial_candidate", read_log=[dict(location="page 1", action="read test fixture", limitations="Second page not inspected")],
                              results=[result], claims=[dict(id="CL1", text="Twelve events occurred.", basis="reported_data", result_ids=["R1"], source_locators=[deepcopy(loc)], **states)],
                              questions=[dict(id=f"Q{n:02d}", status="not_extracted", answer=None, reason="Not extracted in this fixture",
                                              next_action="Inspect source", source_locators=[], result_ids=[]) for n in range(1, 16)],
                              mechanism_fields={key: dict(status="not_extracted", value=None, reason="Not extracted", source_locators=[])
                                                for key in self.schema["properties"]["mechanism_fields"]["required"]},
                              mechanism_payload=None, gaps=[], independent_studies=None, **states)

    def errors(self):
        return validate_candidate(self.candidate, self.assignment, "b" * 64, self.schema)

    def test_honest_partial_candidate_passes_without_claiming_review_complete(self):
        self.assertEqual(self.errors(), [])

    def test_duplicate_questions_fail_even_though_array_has_fifteen(self):
        self.candidate["questions"][-1]["id"] = "Q01"
        self.assertIn("Exactly one Q01-Q15 is required", self.errors())

    def test_wrong_locator_hash_and_unread_numeric_page_fail(self):
        self.candidate["results"][0]["numbers"][0]["source_locators"][0]["source_sha256"] = "c" * 64
        self.candidate["inspection"]["visual_numeric_pages"] = []
        errors = self.errors()
        self.assertIn("locator source identity/hash mismatch", errors)
        self.assertIn("table/figure number lacks visual page check", errors)

    def test_missing_claim_result_and_duplicate_result_fail(self):
        self.candidate["claims"][0]["result_ids"] = ["NOT-PRESENT"]
        self.candidate["results"].append(deepcopy(self.candidate["results"][0]))
        self.assertIn("claim references missing result", self.errors())
        self.assertIn("duplicate result identity", self.errors())

    def test_quarantine_and_context_cannot_supply_primary_results(self):
        self.assignment["integrity_hold"] = "existing_quarantine"
        self.assertIn("quarantined/retracted source must remain integrity-only", self.errors())
        self.assignment["integrity_hold"] = True
        self.assertIn("quarantined/retracted source must remain integrity-only", self.errors())
        self.assignment.pop("integrity_hold")
        self.candidate["source_identity"]["observed_type"] = "review"
        self.assertTrue(any("non-original" in error for error in self.errors()))

    def test_not_reported_and_full_source_require_reading_evidence(self):
        self.candidate["questions"][0]["status"] = "not_reported"
        self.assertIn("not_reported requires full-source inspection", self.errors())
        self.candidate["inspection"]["scope"] = "full_source"
        self.assertIn("full_source requires all physical PDF pages", self.errors())
        self.candidate["inspection"]["pages_read"] = [1, 2]
        self.assertEqual(self.errors(), [])
        self.candidate["processing_state"] = "candidate_complete"
        self.assertIn("unfinished questions cannot be candidate_complete", self.errors())

    def test_number_not_in_quote_and_wrong_numeric_type_fail(self):
        self.candidate["results"][0]["numbers"][0]["reported_text"] = "999"
        self.assertIn("reported number text absent from exact source quote", self.errors())
        self.candidate["results"][0]["numbers"][0]["value"] = "twelve"
        self.assertTrue(any(error.startswith("schema:") for error in self.errors()))

    def test_numeric_value_must_equal_reported_scalar(self):
        number = self.candidate["results"][0]["numbers"][0]
        number["value"] = 999
        self.assertTrue(any("numeric value must match" in error for error in self.errors()))

    def test_reported_scalar_normalization_preserves_sign_exponent_and_grouping(self):
        number = self.candidate["results"][0]["numbers"][0]
        for text, value in [("0·05", .05), ("−12", -12), ("1,234", 1234),
                            ("−1.2e−3", -.0012), ("١٢", 12), ("+12.0", 12)]:
            with self.subTest(text=text):
                number.update(reported_text=text, value=value)
                number["source_locators"][0]["quoted_text"] = "Value: " + text
                self.assertEqual(self.errors(), [])
        for text, value in [("12/40", 12), ("1,23", 123), ("12–40", 12),
                            ("<12", 12), ("12%", .12), ("−12", 12), ("1e3", 1),
                            ("12 (95% CI 3–20)", 12)]:
            with self.subTest(text=text):
                number.update(reported_text=text, value=value)
                number["source_locators"][0]["quoted_text"] = "Value: " + text
                self.assertTrue(any("numeric value must match" in error for error in self.errors()))

    def test_mechanism_payload_cannot_skip_schema(self):
        self.candidate["mechanism_payload"] = {}
        self.assertIn("mechanism payload requires its adopted executable schema", self.errors())

    def mechanism_fixture(self):
        import test_mechanism_schema as mechanism_fixture
        fixture=mechanism_fixture.MechanismSchemaTests(); fixture.setUp()
        payload=deepcopy(fixture.payload)
        locator=deepcopy(self.candidate['results'][0]['source_locators'][0])
        for item in walk(payload):
            if 'source_sha256' in item and 'kind' in item:
                item.clear(); item.update(deepcopy(locator))
        self.candidate['mechanism_payload']=payload
        return fixture.schema

    def test_descriptive_and_vacuous_mechanism_schemas_fail(self):
        self.mechanism_fixture()
        for schema in [{},{'sourceFields':['id'],'extractionFields':{'sourceId':'canonical string'}}]:
            errors=validate_candidate(self.candidate,self.assignment,'b'*64,self.schema,schema)
            self.assertTrue(any('descriptive or vacuous' in error for error in errors))

    def test_mechanism_semantic_source_result_and_locator_links(self):
        schema=self.mechanism_fixture()
        self.assertEqual(validate_candidate(self.candidate,self.assignment,'b'*64,self.schema,schema),[])
        payload=self.candidate['mechanism_payload']
        payload['sources'][0]['canonical_report_id']='ANOTHER-REPORT'
        payload['mechanisms'][0]['source_ids']=['ANOTHER-SOURCE']
        payload['mechanisms'][0]['causal_steps'][0]['result_ids']=['ABSENT']
        errors=validate_candidate(self.candidate,self.assignment,'b'*64,self.schema,schema)
        self.assertIn('mechanism source/report/hash outside assignment',errors)
        self.assertIn('mechanism source references outside assignment',errors)
        self.assertIn('mechanism step references missing source result',errors)
        schema=self.mechanism_fixture()
        self.candidate['mechanism_payload']['mechanisms'][0]['causal_steps'][0]['source_locators'][0]['quoted_text']='Another quotation not linked to this result.'
        self.assertIn('tested mechanism step/readout locator must resolve to its linked result',validate_candidate(self.candidate,self.assignment,'b'*64,self.schema,schema))

    def test_mechanism_duplicate_and_false_completeness_fail(self):
        schema=self.mechanism_fixture()
        payload=self.candidate['mechanism_payload']
        payload['sources'].append(deepcopy(payload['sources'][0]))
        payload['mechanisms'][0]['status']='candidate_complete'
        payload['mechanisms'].append(deepcopy(payload['mechanisms'][0]))
        errors=validate_candidate(self.candidate,self.assignment,'b'*64,self.schema,schema)
        self.assertIn('mechanism payload must identify exactly its assigned source version',errors)
        self.assertIn('duplicate mechanism identity',errors)
        self.assertIn('duplicate mechanism step identity',errors)
        self.assertIn('complete mechanism requires full inspection and no unextracted fields',errors)

    def test_entrypoint_binds_assignment_bundle_schema_and_actual_source(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.pdf"
            source.write_bytes(b"%PDF-1.4\nsynthetic validation fixture only")
            assignment = {**self.assignment, "sha256": sha(source), "bytes": source.stat().st_size, "path": str(source)}
            schema_path, assignment_path = root / "schema.json", root / "assignments.json"
            schema_path.write_bytes(canonical(self.schema))
            assignment_path.write_bytes(canonical({"packets": [{"sourceAssignments": [assignment]}]}))
            plan = {"planId": self.candidate["plan_id"], "operations": ["validate"], "inputs": [
                {"path": path.name, "sha256": sha(path)} for path in [schema_path, assignment_path]]}
            plan_path = root / "plan.json"
            plan_path.write_bytes(canonical(plan))
            candidate = deepcopy(self.candidate)
            candidate["plan_sha256"] = sha(plan_path)
            for item in walk(candidate):
                if "source_sha256" in item:
                    item["source_sha256"] = sha(source)
            candidate_path = root / "candidate.json"
            candidate_path.write_bytes(canonical(candidate))
            readiness_path = root / "readiness.json"
            readiness_path.write_bytes(canonical({"schemaVersion": "remaprx-gp-readiness-v1", "status": "PASS", "scope": "GP_PLAN",
                                                   "planId": plan["planId"], "planSha256": sha(plan_path), "checkedAt": "2026-10-12T00:00:00Z"}))
            args = [schema_path, candidate_path, assignment_path, plan_path, readiness_path]
            result = validate_source(*args, project_root=root)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["candidateSha256"], sha(candidate_path))
            self.assertFalse(result["sourceScientificallyVerified"])
            source.write_bytes(b"source changed")
            with self.assertRaisesRegex(Hold, "source bytes/hash"):
                validate_source(*args, project_root=root)
            unpinned = root / "unapproved-assignments.json"
            unpinned.write_bytes(assignment_path.read_bytes())
            with self.assertRaisesRegex(Hold, "not pinned"):
                validate_source(schema_path, candidate_path, unpinned, plan_path, readiness_path, project_root=root)


if __name__ == "__main__":
    unittest.main()
