"""Build private, read-only research fanout proposals; never write app records.

Run as `python3 -m scripts.research_fanout --help`. `--contract` prints the
machine-readable binding/audit contracts. GP readiness is separate from source
validation, independent scientific verification, human review and release.
The fanout plan records proposalDate as a canonical YYYY-MM-DD for replay.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

from scripts.research_ingest.cli import Hold, canonical, check_inputs, check_readiness, digest, load, require, safe_path, sha, timestamp
from scripts.research_ingest.source_validation import schema_errors, validate_source, walk

APP_INPUTS = (
    "data/content.json", "data/reader-evidence.json", "data/private-reviews.json",
    "data/review-envelopes.json", "data/article-updates.json", "data/outcome-registry.json",
    "data/public-mechanisms.json",
    "editorial/evidence-assessments.json", "editorial/reader-source-aliases.json",
    "scripts/apply-reader-outcomes.py",
)
TEXT = {"type": "string", "minLength": 1}
PROSE = {"type": "string", "minLength": 30}
HASH = {"type": "string", "pattern": "^[0-9a-f]{64}$"}
STRINGS = {"type": "array", "items": TEXT, "uniqueItems": True}
PIN = {"type": "object", "required": ["path", "sha256"], "properties": {"path": TEXT, "sha256": HASH}, "additionalProperties": False}
DIMENSIONS = ("drugId", "conditionId", "population", "comparison", "endpoint", "formulation", "route", "timepoint")
SCOPE = {"type": "object", "required": list(DIMENSIONS), "properties": {key: {"type": ["string", "null"]} for key in DIMENSIONS}, "additionalProperties": False}
QUESTION = {"type": "object", "required": ["guideId", "route", "rationale", "verifiedScope"], "properties": {
    "guideId": TEXT, "route": TEXT, "rationale": PROSE, "verifiedScope": SCOPE}, "additionalProperties": False}
HISTORY = {"type": "object", "required": ["guideId", "title", "summary"], "properties": {
    "guideId": TEXT, "title": TEXT, "summary": PROSE}, "additionalProperties": False}
SCOPED_CLAIM = {"type": "object", "required": ["id", "sourceClaimId", "resultIds", "text", "scope", "sourceLocators", "scopeExplanation"], "properties": {
    "id": TEXT, "sourceClaimId": TEXT, "resultIds": {**STRINGS, "minItems": 1}, "text": PROSE, "scope": SCOPE,
    "sourceLocators": {"type": "array", "items": {"type": "object"}, "minItems": 1}, "scopeExplanation": PROSE}, "additionalProperties": False}
BINDING = {"type": "object", "required": ["id", "kind", "scope", "resultIds", "claimIds", "rationale", "summary", "magnitude", "limits", "mechanismState", "questionRoutes", "pageHistory"], "properties": {
    "id": TEXT, "kind": {"enum": ["mechanism", "clinical_result"]}, "scope": SCOPE,
    "resultIds": {**STRINGS, "minItems": 1}, "claimIds": {**STRINGS, "minItems": 1},
    "scopedClaims": {"type": "array", "items": SCOPED_CLAIM}, "rationale": PROSE, "summary": PROSE,
    "magnitude": TEXT, "limits": PROSE, "mechanismState": {"enum": [None, "tested", "proposed", "inferred"]},
    "questionRoutes": {"type": "array", "items": QUESTION}, "pageHistory": {"type": "array", "items": HISTORY, "minItems": 1}}, "additionalProperties": False}
BINDINGS_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": [
    "schemaVersion", "author", "sourceId", "canonicalReportId", "appSourceId", "candidateSha256", "sourceSha256", "familyIds", "familyIdentityStatus", "identityRationale", "bindings"], "properties": {
    "schemaVersion": {"const": "remaprx-scientific-bindings-v1"}, "author": TEXT, "sourceId": TEXT, "canonicalReportId": TEXT,
    "appSourceId": TEXT, "candidateSha256": HASH, "sourceSha256": HASH, "familyIds": STRINGS,
    "familyIdentityStatus": {"enum": ["preserved", "unknown"]}, "identityRationale": PROSE,
    "bindings": {"type": "array", "items": BINDING, "minItems": 1}}, "additionalProperties": False}
AUDIT_CHECKS = ("sourceIdentity", "sourceLocators", "numericValues", "claimChain", "scientificRelevance", "scopeAndModelLimits", "questionRoutes", "pageHistory")
AUDIT_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": [
    "schemaVersion", "status", "scope", "author", "auditor", "reviewedAt", "candidateSha256", "bindingsSha256", "sourceSha256", "auditedResultIds", "auditedClaimIds", "auditedScopedClaimIds", "checks", "evidence"], "properties": {
    "schemaVersion": {"const": "remaprx-source-fanout-audit-v1"}, "status": {"const": "PASS"},
    "scope": {"const": "independent_source_and_fanout_verification"}, "author": TEXT, "auditor": TEXT, "reviewedAt": TEXT,
    "candidateSha256": HASH, "bindingsSha256": HASH, "sourceSha256": HASH, "auditedResultIds": STRINGS,
    "auditedClaimIds": STRINGS, "auditedScopedClaimIds": STRINGS,
    "checks": {"type": "object", "required": list(AUDIT_CHECKS), "properties": {key: {"const": True} for key in AUDIT_CHECKS}, "additionalProperties": False},
    "evidence": {"type": "array", "items": PIN, "minItems": 1}}, "additionalProperties": False}
AUTHORSHIP_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": [
    "schemaVersion", "candidateSha256", "assignmentId", "author", "writtenAt"], "properties": {
    "schemaVersion": {"const": "remaprx-source-authorship-v1"}, "candidateSha256": HASH, "assignmentId": TEXT,
    "author": TEXT, "writtenAt": TEXT}, "additionalProperties": False}


def identity_module(root):
    spec = importlib.util.spec_from_file_location("fanout_synthesis_identity", root / "scripts/apply-reader-outcomes.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def object_hash(value):
    return digest(canonical(value)) if value is not None else None


def route(guide):
    return guide.get("route") or guide.get("slug")


def scoped_claim_records(candidate, binding, scope, identities, aliases):
    """Keep broad source claims intact; emit only explicitly scoped support."""
    results = {result["id"]: result for result in candidate["results"]}
    claims = {claim["id"]: claim for claim in candidate["claims"]}
    require(len(claims) == len(candidate["claims"]), "Duplicate source claim identities")
    require(set(binding["claimIds"]) <= claims.keys(), "Binding references unvalidated source claims")
    selected = set(binding["resultIds"])
    require(selected <= results.keys(), "Binding references unvalidated source results")
    records, restated, seen = [], set(), set()
    for scoped in binding.get("scopedClaims", []):
        parent_id = scoped["sourceClaimId"]
        require(parent_id in binding["claimIds"], "Scoped claim must derive from a selected source claim")
        parent = claims[parent_id]
        dependencies = set(parent["result_ids"])
        require(dependencies <= results.keys(), "Source claim references absent source results")
        require(scoped["id"] not in seen and scoped["id"] not in claims, "Scoped claim identity must be distinct and unique")
        seen.add(scoped["id"])
        require(set(scoped["resultIds"]) <= selected & dependencies, "Scoped claim includes an unselected or unrelated result")
        require(identities.exact_scope({**scoped["scope"], "sourceIds": scope["sourceIds"]}, aliases) == scope,
                "Scoped claim scope differs from binding")
        allowed_locators = {canonical(loc) for rid in scoped["resultIds"] for loc in results[rid]["source_locators"]}
        require(all(canonical(loc) in allowed_locators for loc in scoped["sourceLocators"]),
                "Scoped claim locators must come from its selected results")
        restated.add(parent_id)
        records.append({"id": scoped["id"], "text": scoped["text"], "kind": "scoped_restatement", "sourceClaimIds": [parent_id],
                        "sourceClaimSha256": object_hash(parent), "resultIds": scoped["resultIds"], "scope": scope,
                        "sourceLocators": scoped["sourceLocators"], "scopeExplanation": scoped["scopeExplanation"],
                        "excludedSourceClaimResultIds": sorted(dependencies - set(scoped["resultIds"])),
                        "publicationState": "private_ai_draft", "humanApproval": "pending"})
    for claim_id in binding["claimIds"]:
        claim = claims[claim_id]
        dependencies = set(claim["result_ids"])
        require(dependencies and dependencies <= results.keys() and dependencies & selected,
                "Every selected claim must link to validated selected results")
        if claim_id not in restated:
            require(dependencies <= selected, "Cross-scope source claim requires an explicit independently audited scoped restatement")
            records.append({"id": claim_id, "text": claim["text"], "kind": "source_claim", "sourceClaimIds": [claim_id],
                            "sourceClaimSha256": object_hash(claim), "resultIds": claim["result_ids"], "scope": scope,
                            "sourceLocators": claim["source_locators"], "excludedSourceClaimResultIds": [],
                            "publicationState": "private_ai_draft", "humanApproval": "pending"})
    require(selected == {rid for record in records for rid in record["resultIds"]}, "Every selected result must support an emitted claim")
    return records


def build_proposals(candidate, bindings, current, identities, date, known_families=()):
    """Pure proposal construction after external hashes/audit/source validation."""
    errors = schema_errors(BINDINGS_SCHEMA, bindings)
    require(not errors, "; ".join(errors))
    sid = bindings["appSourceId"]
    aliases = current["editorial/reader-source-aliases.json"]
    require(identities.canonical_source(candidate["canonical_report_id"], aliases) == sid,
            "Report-to-app identity must resolve through an existing explicit alias")
    require(bindings["sourceId"] == candidate["source_id"] and bindings["canonicalReportId"] == candidate["canonical_report_id"], "Binding source/report identity mismatch")
    sources = [s for s in current["data/content.json"]["sources"] if s["id"] == sid]
    require(len(sources) == 1, "Existing app source required; new bibliography integration is separate")
    source = sources[0]
    reader = current["data/reader-evidence.json"]
    source_families = {s["familyId"] for s in [source] + reader.get("sources", []) if s.get("id") == sid and s.get("familyId")}
    family_ids = sorted(source_families | set(known_families))
    require(sorted(bindings["familyIds"]) == family_ids, "Family identities must preserve established assignment/app records")
    require(bindings["familyIdentityStatus"] == ("preserved" if family_ids else "unknown"), "Family unknownness must remain explicit")
    require(not any(q.get("sourceId") == sid for q in reader.get("quarantine", [])), "App source remains quarantined")
    guides = current["data/content.json"]["guides"]
    rows = reader["synthesisRows"]
    mapping = current["editorial/synthesis-identity-map.json"]
    results = {r["id"]: r for r in candidate["results"]}
    require(len(results) == len(candidate["results"]), "Duplicate source result identities")
    source_locations = {canonical(loc) for r in candidate["results"] for loc in r["source_locators"]}
    require(source_locations, "A fanout proposal requires source-located results")
    seen_bindings, seen_units, seen_scoped_claims = set(), set(), set()
    synthesis, mechanisms, pages, histories = [], [], [], []
    for binding in bindings["bindings"]:
        require(binding["id"] not in seen_bindings, "Duplicate scientific binding ID")
        seen_bindings.add(binding["id"])
        require(set(binding["resultIds"]) <= results.keys(), "Binding references unvalidated source results")
        fact = {**binding["scope"], "sourceIds": [sid]}
        scope = identities.exact_scope(fact, aliases)
        require(scope["drugId"] and scope["endpoint"] and scope["population"], "Explicit drug, endpoint and population/model are required")
        selected = [results[rid] for rid in binding["resultIds"]]
        for result in selected:
            for key in ("population", "comparison", "endpoint", "timepoint"):
                require(scope[key] == (result[key].strip() or None), "Binding scope differs from validated result: " + key)
        claim_records = scoped_claim_records(candidate, binding, scope, identities, aliases)
        for record in claim_records:
            if record["kind"] == "scoped_restatement":
                require(record["id"] not in seen_scoped_claims, "Scoped claim IDs must be unique across bindings")
                seen_scoped_claims.add(record["id"])
        kind = binding["kind"]
        if kind == "clinical_result":
            require(binding["mechanismState"] is None, "Clinical-result bindings cannot imply a mechanism state")
            require(candidate["source_identity"]["evidence_class"].startswith("human_"), "Nonhuman evidence cannot become a clinical-result synthesis")
            proposal_id = identities.resolve_synthesis_identity(fact, rows, aliases, mapping)
            sections = [{"id": "evidence", "label": "Evidence"}, {"id": "research-feed", "label": "Research Feed"}]
        else:
            require(binding["mechanismState"] is not None, "Mechanism proposal needs tested/proposed/inferred status")
            proposal_id = "MECHANISM-" + identities.scope_hash(scope)[:24].upper()
            sections = [{"id": "mechanisms", "label": "Mechanism of Action"}]
        require(proposal_id not in seen_units, "Duplicate exact-scope proposal; combine its result IDs explicitly")
        seen_units.add(proposal_id)
        parents = []
        for entity in [scope["drugId"], scope["conditionId"]]:
            if entity:
                found = [g for g in guides if g.get("entityId") == entity]
                require(len(found) == 1 and route(found[0]), "Missing or ambiguous parent guide: " + entity)
                parents.append(found[0])
        questions = []
        for question in binding["questionRoutes"]:
            found = [g for g in guides if g["id"] == question["guideId"] and route(g) == question["route"]]
            require(len(found) == 1 and question["route"].startswith("/answers/"), "Question route must resolve to an existing scoped answer")
            require(identities.exact_scope({**question["verifiedScope"], "sourceIds": [sid]}, aliases) == scope, "Question route verified scope mismatch")
            questions.append(found[0])
        targets = parents + questions
        require(len({g["id"] for g in targets}) == len(targets), "Repeated page target")
        page_history = {h["guideId"]: h for h in binding["pageHistory"]}
        require(len(page_history) == len(binding["pageHistory"]) and set(page_history) == {g["id"] for g in targets}, "Each target needs exactly one page-specific history proposal")
        require(len({h["summary"] for h in page_history.values()}) == len(page_history), "History summaries must describe each page specifically")
        provenance = {"sourceId": candidate["source_id"], "appSourceId": sid, "canonicalReportId": candidate["canonical_report_id"],
                      "sourceSha256": candidate["source_sha256"], "candidateSha256": bindings["candidateSha256"], "familyIds": family_ids,
                      "familyIdentityStatus": bindings["familyIdentityStatus"], "resultIds": binding["resultIds"], "claimIds": binding["claimIds"],
                      "scopedClaimIds": [record["id"] for record in claim_records], "bindingId": binding["id"]}
        proposal = {"id": proposal_id, "kind": kind, "scope": scope, "finding": binding["summary"], "magnitude": binding["magnitude"],
                    "limits": binding["limits"], "relevanceRationale": binding["rationale"], "provenance": provenance, "scopedClaimRecords": claim_records,
                    "sourceLocators": [loc for result in selected for loc in result["source_locators"]],
                    "publicationState": "private_ai_draft", "humanApproval": "pending", "scientificAssessment": "pending",
                    "currentRecordSha256": object_hash(next((r for r in rows if r["id"] == proposal_id), None))}
        if kind == "mechanism":
            proposal.update(mechanismState=binding["mechanismState"], clinicalBenefitEstablished=False)
            # The historical "drugs" array also holds condition records.
            prior_mechanisms = [m for m in current["data/public-mechanisms.json"].get("drugs", [])
                                if m.get("drugId") is not None and m.get("drugId") == scope["drugId"]]
            require(len(prior_mechanisms) <= 1, "Ambiguous existing mechanism drug records")
            proposal["currentMechanismDrugSha256"] = object_hash(prior_mechanisms[0] if prior_mechanisms else None)
            mechanisms.append(proposal)
        else:
            synthesis.append(proposal)
        for guide in targets:
            path = route(guide)
            history = page_history[guide["id"]]
            target_sections = sections
            destination = {}
            if kind == "mechanism" and scope["conditionId"] is not None and guide.get("entityId") == scope["conditionId"]:
                require(guide.get("type", "").casefold() == "condition", "Condition parent identity/type mismatch")
                target_sections = [{"id": "interventions", "label": "Interventions"}]
                available_ids = [section["id"] for section in guide.get("sections", [])
                                 if section.get("id") == "interventions" or section.get("label", "").casefold() == "interventions"]
                destination = {"destinationStatus": "private_proposal", "currentGuideSectionIds": available_ids,
                               "currentDataTargetAvailable": bool(available_ids), "renderedTargetVerified": False,
                               "layoutStatus": "pending_rendered_verification" if available_ids else "pending_layout"}
            pages.append({"guideId": guide["id"], "route": path, "sharedRecordId": proposal_id, "recordKind": kind,
                          "sections": target_sections, "sourceIds": [sid], "currentGuideSha256": object_hash(guide), **destination})
            histories.append({"id": "research-draft-" + digest(canonical([proposal_id, guide["id"], date]))[:20], "date": date,
                              "title": history["title"], "summary": history["summary"], "changeType": "evidence",
                              "pagePaths": [path], "affectedSections": target_sections, "sourceIds": [sid], "resultIds": binding["resultIds"],
                              "publicationState": "proposed_only", "dateMeaning": "proposal date; record actual integration date if accepted", **destination})
    dependent_rows = {r["id"] for r in rows if sid in r.get("sourceIds", [])} | {s["id"] for s in synthesis}
    dependent_assessments = [a for a in current["editorial/evidence-assessments.json"]["records"] if a.get("rowId") in dependent_rows or sid in a.get("sourceIds", [])]
    body = current["data/private-reviews.json"].get(sid)
    envelope = current["data/review-envelopes.json"].get(sid)
    return {"synthesisProposals": synthesis, "mechanismProposals": mechanisms, "pageProposals": pages, "historyProposals": histories,
            "reviewProposal": {"sourceId": sid, "canonicalReportId": candidate["canonical_report_id"], "familyIds": family_ids,
                               "route": "/research/" + sid, "operation": "merge_source_question_inputs_for_editorial_review",
                               "questionInputs": candidate["questions"], "reviewCompletion": "pending", "humanApproval": "pending", "release": "pending",
                               "accessPolicy": "free_authenticated", "currentBodySha256": object_hash(body), "currentEnvelopeSha256": object_hash(envelope)},
            "invalidations": {"reason": "If accepted, changed source findings require dependent assessments and approvals to be revalidated against resulting hashes",
                              "synthesisIds": sorted(dependent_rows), "assessmentRecords": [{"rowId": a["rowId"], "currentSha256": object_hash(a)} for a in dependent_assessments],
                              "reviewSourceIds": [sid], "reviewApprovalFields": ["approvedSha256", "humanEditorialApproved", "qualifiedClinicalApproval"],
                              "currentEnvelopeSha256": object_hash(envelope), "applyAutomatically": False}}


def fanout(args):
    root = Path(args.root).resolve()
    plan_path, readiness_path = Path(args.plan), Path(args.readiness)
    plan_hash, readiness_hash = sha(plan_path), sha(readiness_path)
    plan = load(plan_path)
    require(plan.get("schemaVersion") == "remaprx-fanout-plan-v1" and plan.get("operations") == ["fanout"], "Separate read-only fanout plan is required")
    check_readiness(readiness_path, plan, plan_hash)
    from datetime import date
    proposal_date = plan.get("proposalDate")
    try:
        require(isinstance(proposal_date, str) and date.fromisoformat(proposal_date).isoformat() == proposal_date,
                "Fanout plan proposalDate must be a canonical ISO calendar date (YYYY-MM-DD)")
    except (TypeError, ValueError) as error:
        raise Hold("Fanout plan proposalDate must be a canonical ISO calendar date (YYYY-MM-DD)") from error
    pins = check_inputs(root, plan)
    def pinned(path):
        path = Path(path).resolve()
        require(path.is_relative_to(root), "Fanout inputs must be pinned inside the project")
        relative = path.relative_to(root).as_posix()
        require(relative in pins and sha(safe_path(root, relative)) == pins[relative], "Unpinned fanout input: " + relative)
        return load(path)
    candidate, bindings, audit, authorship = [pinned(path) for path in [args.candidate, args.bindings, args.verification, args.authorship]]
    for path in [args.schema, args.assignment, args.source_plan, args.source_readiness]:
        pinned(path)
    if args.mechanism_schema:
        pinned(args.mechanism_schema)
    require(not schema_errors(AUDIT_SCHEMA, audit), "Independent source/fanout audit contract failed")
    require(not schema_errors(BINDINGS_SCHEMA, bindings), "Scientific relevance binding contract failed")
    require(not schema_errors(AUTHORSHIP_SCHEMA, authorship), "Pinned source authorship contract failed")
    timestamp(audit["reviewedAt"])
    timestamp(authorship["writtenAt"])
    require(authorship["candidateSha256"] == sha(args.candidate) and authorship["assignmentId"] == candidate["assignment_id"], "Source authorship receipt is stale or mismatched")
    require(audit["author"] == bindings["author"] and audit["author"].strip().casefold() != audit["auditor"].strip().casefold(), "Independent verifier must differ from the binding/candidate author")
    require(authorship["author"].strip() and audit["auditor"].strip().casefold() != authorship["author"].strip().casefold(), "Independent verifier must differ from the source extractor")
    for key, expected in {"candidateSha256": sha(args.candidate), "bindingsSha256": sha(args.bindings), "sourceSha256": candidate["source_sha256"]}.items():
        require(audit[key] == expected, "Independent audit hash mismatch: " + key)
    require(bindings["candidateSha256"] == sha(args.candidate) and bindings["sourceSha256"] == candidate["source_sha256"], "Binding candidate/source hash mismatch")
    used_results = {result for b in bindings["bindings"] for result in b["resultIds"]}
    claims = {claim["id"]: claim for claim in candidate["claims"]}
    used_claims = {claim for b in bindings["bindings"] for claim in b["claimIds"]}
    scoped_claim_ids = {claim["id"] for b in bindings["bindings"] for claim in b.get("scopedClaims", [])}
    require(used_claims <= claims.keys(), "Binding references unvalidated source claims")
    claim_dependencies = {rid for cid in used_claims for rid in claims[cid]["result_ids"]}
    require(used_results | claim_dependencies <= set(audit["auditedResultIds"]), "Every proposed result and original claim dependency needs independent verification")
    require(used_claims <= set(audit["auditedClaimIds"]), "Every source claim needs independent verification")
    require(scoped_claim_ids <= set(audit["auditedScopedClaimIds"]), "Every scoped claim restatement needs independent verification")
    for evidence in audit["evidence"]:
        path = safe_path(root, evidence["path"])
        require(pins.get(evidence["path"]) == evidence["sha256"] and sha(path) == evidence["sha256"], "Audit evidence must be present and plan-pinned")
    validation = validate_source(args.schema, args.candidate, args.assignment, args.source_plan, args.source_readiness,
                                 source_file=args.source_file, mechanism_schema_path=args.mechanism_schema, project_root=root)
    require(validation["status"] == "PASS", "Source validation HOLD: " + "; ".join(validation["errors"]))
    current = {name: pinned(root / name) for name in APP_INPUTS if name.endswith(".json")}
    current["editorial/synthesis-identity-map.json"] = pinned(args.identity_map or root / "research/batches/RRX-INGEST-001/synthesis-identity-map.json")
    require(pins.get("scripts/apply-reader-outcomes.py") == sha(root / "scripts/apply-reader-outcomes.py"), "Identity implementation must be pinned")
    require(pins.get("scripts/research_fanout.py") == sha(root / "scripts/research_fanout.py"), "Fanout implementation must be pinned")
    bundle = load(args.assignment)
    packets = [p for p in bundle.get("packets", []) if any(s.get("assignment_id") == candidate["assignment_id"] for s in p.get("sourceAssignments", []))]
    require(len(packets) <= 1, "Ambiguous family assignment packet")
    families = packets[0].get("familyCoordination", {}).get("familyIds", []) if packets else []
    proposals = build_proposals(candidate, bindings, current, identity_module(root), proposal_date, families)
    check_inputs(root, plan)
    require(sha(plan_path) == plan_hash and sha(readiness_path) == readiness_hash, "Fanout controls changed during validation")
    return {"schemaVersion": "remaprx-fanout-proposals-v1", "status": "PASS", "scope": "read_only_private_draft_proposals",
            "planId": plan["planId"], "planSha256": plan_hash, "inputHashes": pins, "sourceValidation": validation,
            "verificationSha256": sha(args.verification), "independentVerifier": audit["auditor"], "sourceExtractor": authorship["author"],
            "performedImport": False, "humanApproval": False, "releaseChanged": False, **proposals}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", action="store_true")
    for name in ("root", "plan", "readiness", "candidate", "schema", "assignment", "source-plan", "source-readiness", "bindings", "verification", "authorship", "identity-map", "source-file", "mechanism-schema"):
        parser.add_argument("--" + name)
    args = parser.parse_args()
    if args.contract:
        print(json.dumps({"bindings": BINDINGS_SCHEMA, "audit": AUDIT_SCHEMA, "authorship": AUTHORSHIP_SCHEMA, "requiredAppInputs": APP_INPUTS,
                          "defaultIdentityMap": "research/batches/RRX-INGEST-001/synthesis-identity-map.json",
                          "requiredPlanProposalDate": "Canonical ISO calendar date YYYY-MM-DD; reused for deterministic history proposals"}, indent=2))
        return
    for key in ("root", "plan", "readiness", "candidate", "schema", "assignment", "source_plan", "source_readiness", "bindings", "verification", "authorship"):
        if not getattr(args, key):
            parser.error("--" + key.replace("_", "-") + " is required")
    try:
        result = fanout(args)
    except (Hold, ValueError, KeyError, OSError, TypeError) as error:
        print(json.dumps({"status": "HOLD", "reason": str(error), "performedImport": False}), file=sys.stderr)
        sys.exit(2)
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
