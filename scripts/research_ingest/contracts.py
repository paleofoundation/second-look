"""Executable Draft 2020-12 contracts. Export with the CLI's schema command."""

HASH = {"type": "string", "pattern": "^[a-f0-9]{64}$"}
TEXT = {"type": "string", "minLength": 1}


def obj(properties, required=None, additional=False):
    return {"type": "object", "properties": properties,
            "required": list(properties) if required is None else required,
            "additionalProperties": additional}


def array(items, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum}


PIN = obj({"path": TEXT, "sha256": HASH})
KINDS = ["schema", "identity", "source_integrity", "preservation", "idempotence", "independent_audit"]
SCHEMAS = {
    "plan": obj({
        "schemaVersion": {"const": "remaprx-ingest-plan-v1"}, "planId": TEXT,
        "operations": {"type": "array", "uniqueItems": True, "minItems": 1,
                       "items": {"enum": ["validate", "stage", "diff", "apply"]}},
        "allowedTargets": {"type": "array", "items": TEXT, "uniqueItems": True, "minItems": 1},
        "inputs": array(PIN, 1), "contract": {"type": "object"},
    }, ["schemaVersion", "planId", "operations", "allowedTargets", "inputs"], True),
    "manifest": obj({
        "schemaVersion": {"const": "remaprx-candidate-v1"}, "planId": TEXT,
        "planSha256": HASH, "batchId": TEXT, "author": TEXT,
        "files": array(obj({"target": TEXT, "path": TEXT, "sha256": HASH,
                             "baseSha256": {"anyOf": [HASH, {"type": "null"}]}}), 1),
    }),
    "readiness": obj({
        "schemaVersion": {"const": "remaprx-gp-readiness-v1"}, "status": {"const": "PASS"},
        "scope": {"const": "GP_PLAN"}, "planId": TEXT, "planSha256": HASH, "checkedAt": TEXT,
    }, additional=True),
    "acceptance": obj({
        "schemaVersion": {"const": "remaprx-acceptance-v1"}, "status": {"const": "PASS"},
        "scope": {"const": "technical_candidate_integration"}, "planId": TEXT,
        "planSha256": HASH, "batchId": TEXT, "candidateDigest": HASH,
        "author": TEXT, "auditor": TEXT, "reviewedAt": TEXT,
        "reports": array(obj({"kind": {"enum": KINDS}, "path": TEXT, "sha256": HASH}), 6),
    }, additional=True),
    "report": obj({
        "status": {"const": "PASS"}, "candidateDigest": HASH,
        "targets": {"type": "array", "items": TEXT, "uniqueItems": True, "minItems": 1},
        "inputHashes": {"type": "object", "additionalProperties": HASH, "minProperties": 1},
        "checks": {"type": "object", "additionalProperties": {"const": True}, "minProperties": 1},
        "evidence": array(PIN), "author": TEXT, "auditor": TEXT,
    }, ["status", "candidateDigest", "targets", "inputHashes", "checks"], True),
    "journal": obj({
        "schemaVersion": {"const": "remaprx-import-journal-v1"},
        "status": {"enum": ["INTENT", "HOLD_MANUAL_RECOVERY", "ROLLED_BACK", "COMMITTED"]},
        "runId": {"type": "string", "pattern": "^[a-f0-9]{32}$"}, "root": TEXT,
        "candidateDigest": HASH, "planId": TEXT, "planSha256": HASH, "planBackup": TEXT,
        "files": array(obj({"target": TEXT, "before": {"anyOf": [HASH, {"type": "null"}]},
                            "after": HASH, "backup": {"anyOf": [TEXT, {"type": "null"}]}}), 1),
        "perFileAtomic": {"const": True}, "crossFileAtomic": {"const": False},
    }, additional=True),
}
for schema in SCHEMAS.values():
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
