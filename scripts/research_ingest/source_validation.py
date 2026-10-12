"""Portable adaptation of the SL-F01/F02 source candidate validator.

Read-only structural/provenance checks. Source-reading assertions and scientific
interpretation still require independent evidence and do not become approval.
"""
from pathlib import Path
from decimal import Decimal, InvalidOperation
import re
import unicodedata

from .cli import Hold, canonical, check_inputs, check_readiness, decode, digest, load, require, safe_path, sha


def reported_scalar(text):
    """Parse one reported scalar; never infer a conversion, range or threshold.

    Normalize Unicode decimal digits, mathematical minus, middle-dot decimal,
    and conventional comma thousands groups. Units belong in the units field.
    Qualifiers, percentages, ratios and multiple numbers need another contract.
    """
    if not isinstance(text, str):
        return None
    text = "".join(str(unicodedata.decimal(c)) if c.isdecimal() else c for c in text.strip())
    text = text.translate(str.maketrans({"−": "-", "·": "."}))
    scalar = r"[+-]?(?:(?:[0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?"
    if re.fullmatch(scalar, text) is None:
        return None
    try:
        value = Decimal(text.replace(",", ""))
        return value if value.is_finite() else None
    except InvalidOperation:
        return None


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def schema_errors(schema, value):
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError as error:
        raise Hold("Install scripts/research_ingest/requirements.txt") from error
    require(all(not item.get("$ref") or item["$ref"].startswith("#") for item in walk(schema)),
            "Source schema must use self-contained local references")
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise Hold("Invalid scientific JSON Schema: " + error.message) from error
    return ["schema: " + "/".join(map(str, error.absolute_path)) + ": " + error.message
            for error in Draft202012Validator(schema).iter_errors(value)]


def mechanism_errors(payload, schema, candidate, assignment):
    """Check the adopted executable contract and its source/result graph."""
    if not (isinstance(schema, dict) and schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
            and schema.get("type") == "object" and {"schema_version", "sources", "mechanisms"} <= set(schema.get("required", []))
            and schema.get("properties", {}).get("schema_version", {}).get("const") == "RRX-MECHANISM-CANDIDATE-1.0"):
        return ["mechanism schema must be the adopted executable RRX mechanism contract; descriptive or vacuous schemas are not validators"]
    if not schema_errors(schema, {}):
        return ["vacuous mechanism schema accepts an empty payload"]
    errors = ["mechanisms: " + error for error in schema_errors(schema, payload)]
    if errors:
        return errors
    def check(value, message):
        if not value:
            errors.append(message)
    check(len(payload["sources"]) == 1, "mechanism payload must identify exactly its assigned source version")
    for source in payload["sources"]:
        check(source["source_id"] == assignment["source_id"] and source["sha256"] == assignment["sha256"]
              and source["canonical_report_id"] == assignment["canonical_report_id"], "mechanism source/report/hash outside assignment")
    results = {result["id"]: result for result in candidate["results"]}
    mechanism_ids, step_ids = set(), set()
    for mechanism in payload["mechanisms"]:
        check(mechanism["id"] not in mechanism_ids, "duplicate mechanism identity")
        mechanism_ids.add(mechanism["id"])
        check(mechanism["source_ids"] == [assignment["source_id"]], "mechanism source references outside assignment")
        if candidate["source_identity"]["observed_type"] not in ("original_report", "supplement"):
            check(mechanism["tier"] == "CONTEXT", "non-original mechanism source must remain context")
        if mechanism["status"] == "candidate_complete":
            check(candidate["inspection"]["scope"] == "full_source" and not any(item.get("status") == "not_extracted" for item in walk(mechanism)),
                  "complete mechanism requires full inspection and no unextracted fields")
        for step in mechanism["causal_steps"]:
            check(step["id"] not in step_ids, "duplicate mechanism step identity")
            step_ids.add(step["id"])
            linked = set(step["result_ids"])
            check(linked <= results.keys(), "mechanism step references missing source result")
            if step["basis"] == "tested" and linked <= results.keys():
                locators = {canonical(locator) for rid in linked for locator in results[rid]["source_locators"]}
                for locator in step["source_locators"] + step["measured_readout"]["source_locators"]:
                    check(canonical(locator) in locators, "tested mechanism step/readout locator must resolve to its linked result")
    return errors


def validate_candidate(data, assignment, plan_hash, schema, mechanism_schema=None):
    errors = schema_errors(schema, data)
    if errors:
        return errors
    def check(value, message):
        if not value:
            errors.append(message)
    for key, expected in {
        "plan_sha256": plan_hash, "source_id": assignment["source_id"],
        "source_sha256": assignment["sha256"], "assignment_id": assignment["assignment_id"],
        "batch_id": assignment["batch_id"], "canonical_report_id": assignment["canonical_report_id"],
    }.items():
        check(data[key] == expected, "assignment mismatch: " + key)
    inspection = data["inspection"]
    full = inspection["scope"] == "full_source"
    pdf = assignment["media_type"] == "application/pdf"
    check(len(inspection["pages_read"]) == len(set(inspection["pages_read"])), "duplicate page-read entries")
    check(set(inspection["visual_numeric_pages"]) <= set(inspection["pages_read"]), "visual numeric pages were not read")
    if pdf and full:
        check(bool(inspection["total_pages"]) and set(inspection["pages_read"]) == set(range(1, (inspection["total_pages"] or 0) + 1)),
              "full_source requires all physical PDF pages")
    if not pdf and full:
        check(bool(inspection["native_sections_read"]), "full native source requires a section read log")
    if full:
        check(bool(data["read_log"]), "full_source requires an actual read log")
    if data["processing_state"] == "candidate_complete":
        check(full, "candidate_complete requires full-source inspection")
        check(not any(q["status"] in ("not_extracted", "not_checked", "partial", "not_accessible") for q in data["questions"]),
              "unfinished questions cannot be candidate_complete")
    expected_questions = {f"Q{n:02d}" for n in range(1, 16)}
    check(len(data["questions"]) == 15 and {q["id"] for q in data["questions"]} == expected_questions,
          "Exactly one Q01-Q15 is required")
    for item in walk(data):
        if item.get("status") == "not_reported" or item.get("missing_reason") == "not_reported":
            check(full, "not_reported requires full-source inspection")
        if {"source_sha256", "kind"} <= item.keys():
            check(item.get("source_id") == assignment["source_id"] and item["source_sha256"] == assignment["sha256"],
                  "locator source identity/hash mismatch")
            check(bool(item.get("quoted_text", "").strip()) and bool(item.get("section", "").strip()),
                  "locator needs an exact quotation and section")
            if pdf:
                check(item["kind"] == "pdf" and item.get("pdf_page") in inspection["pages_read"],
                      "PDF locator format/page is outside inspected source")
            else:
                check(item["kind"] in ("html", "xml", "epub", "text") and bool(item.get("native_path")),
                      "native source locator requires a native path")
    result_ids = {r["id"] for r in data["results"]}
    check(len(result_ids) == len(data["results"]), "duplicate result identity")
    number_ids = set()
    for result in data["results"]:
        check(result["source_id"] == assignment["source_id"] and result["canonical_report_id"] == assignment["canonical_report_id"],
              "result identity mismatch")
        check(bool(result["source_locators"]), "result has no source locator")
        for number in result["numbers"]:
            check(number["id"] not in number_ids, "duplicate numeric identity")
            number_ids.add(number["id"])
            check(bool(number["source_locators"]), "numeric result has no source locator")
            if number["value"] is not None:
                check(bool(number["units"]) and number["missing_reason"] is None, "reported number requires units and no missing reason")
                scalar = reported_scalar(number["reported_text"])
                check(scalar is not None and scalar == Decimal(str(number["value"])),
                      "numeric value must match one unambiguous reported scalar; derived or qualified values require a separate contract")
                check(bool(number["reported_text"]) and any(str(number["reported_text"]).strip() in locator["quoted_text"]
                                                          for locator in number["source_locators"]), "reported number text absent from exact source quote")
                for locator in number["source_locators"]:
                    if locator["kind"] == "pdf" and (locator.get("table") or locator.get("figure")):
                        check(locator["pdf_page"] in inspection["visual_numeric_pages"], "table/figure number lacks visual page check")
            else:
                check(bool(number["missing_reason"]), "null number needs explicit missingness")
    claim_ids = {c["id"] for c in data["claims"]}
    check(len(claim_ids) == len(data["claims"]), "duplicate claim identity")
    for claim in data["claims"]:
        check(set(claim["result_ids"]) <= result_ids, "claim references missing result")
        if "source_ids" in claim:
            check(set(claim["source_ids"]) <= {assignment["source_id"]}, "claim references another assigned source")
    for question in data["questions"]:
        check(set(question["result_ids"]) <= result_ids, "question references missing result")
        if question["status"] == "located_candidate":
            check(bool(question["source_locators"]) and bool(question["answer"]), "located question needs answer and locators")
        else:
            check(bool(question["reason"]) and bool(question["next_action"]), "unresolved question needs reason and next action")
    identity = data["source_identity"]
    held = assignment.get("integrity_hold") not in (None, False, "") or identity["source_integrity"] in ("retracted", "replacement_unlinked")
    nonoriginal = identity["observed_type"] not in ("original_report", "supplement")
    if held:
        check(not data["results"] and not data["claims"] and data["processing_state"] == "quarantined",
              "quarantined/retracted source must remain integrity-only")
        check(data["mechanism_payload"] is None and not any(v["status"] == "reported" for v in data["mechanism_fields"].values()),
              "quarantined source cannot support mechanisms")
    if nonoriginal:
        check(not data["results"] and not data["claims"], "non-original source cannot supply primary results/claims; use an explicit context contract")
    if identity["applicability"] == "irrelevant":
        check(not data["results"] and not data["claims"], "irrelevant source cannot supply scoped findings")
    if data["results"]:
        check(identity["applicability"] not in ("not_checked", "uncertain", "irrelevant") and identity["source_integrity"] != "not_checked",
              "supportive results require checked relevance and integrity")
    mechanism = data["mechanism_payload"]
    if mechanism is not None:
        if mechanism_schema is None:
            errors.append("mechanism payload requires its adopted executable schema")
        else:
            errors.extend(mechanism_errors(mechanism, mechanism_schema, data, assignment))
    elif any(v["status"] == "reported" for v in data["mechanism_fields"].values()):
        errors.append("reported mechanism fields require an adopted-schema payload")
    return errors


def validate_source(schema_path, candidate_path, assignment_path, plan_path, readiness_path,
                    source_file=None, mechanism_schema_path=None, project_root=None):
    require(project_root is not None, "--root is required to bind the source contract to plan inputs")
    root = Path(project_root).resolve()
    plan_bytes = Path(plan_path).read_bytes()
    plan = decode(plan_bytes)
    assignment_bytes, candidate_bytes, schema_bytes = (Path(p).read_bytes() for p in (assignment_path, candidate_path, schema_path))
    assignment_bundle, candidate, schema = map(decode, (assignment_bytes, candidate_bytes, schema_bytes))
    plan_hash = digest(plan_bytes)
    check_readiness(readiness_path, plan, plan_hash)
    check_inputs(root, plan)
    pinned = {safe_path(root, pin["path"]).resolve(): pin["sha256"] for pin in plan["inputs"]}
    for artifact, raw in [(assignment_path, assignment_bytes), (schema_path, schema_bytes)]:
        require(pinned.get(Path(artifact).resolve()) == digest(raw), "Scientific schema/assignment is not pinned by GP plan")
    matches = [item for item in walk(assignment_bundle) if item.get("assignment_id") == candidate["assignment_id"]
               and item.get("source_id") == candidate["source_id"] and "sha256" in item]
    require(len(matches) == 1, "Scientific assignment must resolve exactly once in the pinned bundle")
    assignment = matches[0]
    require(candidate["plan_id"] == plan["planId"], "Scientific candidate plan identity mismatch")
    require("validate" in plan["operations"], "Source validation is outside the plan")
    path = Path(source_file or assignment["path"])
    require(path.is_file() and path.stat().st_size == assignment["bytes"] and sha(path) == assignment["sha256"],
            "Assigned source bytes/hash mismatch")
    if assignment["media_type"] == "application/pdf":
        with path.open("rb") as stream:
            require(stream.read(5) == b"%PDF-", "Assigned PDF is a failed or mislabeled download")
    mechanism_schema = None
    if mechanism_schema_path:
        mechanism_bytes = Path(mechanism_schema_path).read_bytes()
        require(pinned.get(Path(mechanism_schema_path).resolve()) == digest(mechanism_bytes), "Mechanism schema is not pinned by GP plan")
        mechanism_schema = decode(mechanism_bytes)
    errors = validate_candidate(candidate, assignment, plan_hash, schema, mechanism_schema)
    check_inputs(root, plan)
    require(sha(plan_path) == plan_hash and sha(path) == assignment["sha256"], "Plan or source changed during validation")
    return {"status": "HOLD" if errors else "PASS", "sourceId": assignment["source_id"],
            "candidateSha256": digest(candidate_bytes), "schemaSha256": digest(schema_bytes),
            "planSha256": plan_hash, "assignmentSha256": digest(assignment_bytes),
            "errors": errors, "scope": "source candidate schema, relationships and provenance assertions",
            "sourceScientificallyVerified": False, "humanApproval": False, "performedImport": False}
