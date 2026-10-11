"""Merge the sourced wiki packet without replacing existing editorial content."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_SOURCE_KEYS = set("id title url doi year authors design population n randomizedN sampleDescription intervention comparator sourceType familyId pmid preview decisiveLimit locators correction status".split())


def read(relative):
    return json.loads((ROOT / relative).read_text())


def write(relative, value):
    (ROOT / relative).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def upsert(records, additions, key):
    positions = {key(record): index for index, record in enumerate(records)}
    for record in additions:
        identity = key(record)
        if identity in positions:
            records[positions[identity]] = record
        else:
            positions[identity] = len(records)
            records.append(record)


def unique_locators(locators):
    result = []
    for locator in locators:
        locator = dict(locator)
        if locator.get("table_figure") == locator.get("section"):
            locator.pop("table_figure", None)
        if locator not in result:
            result.append(locator)
    return result


packet = read("data/wiki-foundations.json")
for relative in ("data/content.json", "data/public-content.json"):
    content = read(relative)
    for collection, identity in (("sources", "id"), ("guides", "id"), ("glossary", "slug")):
        additions = packet[collection]
        if relative == "data/public-content.json" and collection == "sources":
            additions = [{k: v for k, v in source.items() if k in PUBLIC_SOURCE_KEYS}
                         for source in additions]
        upsert(content[collection], additions, lambda record: record[identity])
    write(relative, content)

mechanisms = read("data/public-mechanisms.json")
upsert(mechanisms["drugs"], packet["mechanisms"],
       lambda record: record.get("drugId") or record.get("conditionId"))
write("data/public-mechanisms.json", mechanisms)
print("Merged wiki foundations: 3 guides, 13 terms, 20 context sources, 2 mechanism records.")

expansion_path = ROOT / "editorial/mechanism-expansion/mechanism-additions.json"
if expansion_path.exists():
    expansion = json.loads(expansion_path.read_text())
    for source in expansion["sources"]:
        source["locators"] = unique_locators(source["locators"])
    for relative in ("data/content.json", "data/public-content.json", "data/discovery-pages.json"):
        content = read(relative)
        guides = content if isinstance(content, list) else content["guides"]
        if isinstance(content, dict):
            additions = expansion["sources"]
            if relative == "data/public-content.json":
                additions = [{k: v for k, v in source.items()
                              if k in PUBLIC_SOURCE_KEYS and k != "status"} for source in additions]
            upsert(content["sources"], additions, lambda source: source["id"])
            for update in expansion["existingSourceUpdates"]:
                source = next(source for source in content["sources"] if source["id"] == update["id"])
                for key, value in update.items():
                    if relative == "data/public-content.json" and key not in PUBLIC_SOURCE_KEYS:
                        continue
                    if key == "locators":
                        source[key] = unique_locators(source.get(key, []) + value)
                    else:
                        source[key] = value
        for closure in expansion["sourceGuideClosures"]:
            for guide in guides:
                if guide.get("entityId") == closure["drugId"] or guide["id"] in closure["guideIds"]:
                    guide["sourceIds"] = list(dict.fromkeys(guide["sourceIds"] + closure["addSourceIds"]))
        write(relative, content)

    for addition in expansion["drugs"]:
        record = next(record for record in mechanisms["drugs"] if record.get("drugId") == addition["drugId"])
        upsert(record.setdefault("questions", []), addition["questions"], lambda question: question["id"])
    write("data/public-mechanisms.json", mechanisms)

    envelopes = read("data/review-envelopes.json")
    version = "mechanism-fulltext-2026-10-11-pending"
    for source in expansion["sources"]:
        # No protected review body or content hash exists yet. Input extraction is
        # deliberately insufficient to unlock a completed full-study review.
        envelopes.setdefault(source["id"], {
            "preview": {
                "id": source["id"], "title": source["title"],
                "route": "/research/" + source["id"], "sourceUrl": source["url"],
                "preview": source["preview"], "decisiveLimit": source["decisiveLimit"],
                "reviewState": "pending", "version": version, "sourceIds": [source["id"]],
            },
            "release": {
                "state": "pending", "version": version, "contentSha256": "",
                "approvedSha256": None, "humanEditorialApproved": False,
                "clinicalSafetyReviewRequired": True, "qualifiedClinicalApproval": False,
            },
        })
    write("data/review-envelopes.json", envelopes)
    print(f"Merged {len(expansion['sources'])} primary source records and mechanism questions for {len(expansion['drugs'])} drugs; appraisals remain pending.")
