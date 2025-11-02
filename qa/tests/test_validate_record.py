from pplx_harness.constants import SENTINEL_TEXT
from pplx_harness.validate.records import validate_record


def test_validate_record_prunes_invalid_rows() -> None:
    record = {
        "research_analysis": (
            "1. Workflow approvals cannot be sequenced for teaching staff.\n"
            "2. HR notifications cannot be triggered for non-teaching hires."
        ),
        "validation": {
            "validation": [
                {
                    "item": 1,
                    "object": "Route Map",
                    "module": "rcm",
                    "impact": "Approvals blocked",
                    "config_required": "yes",
                    "evidence_pointer": "https://help.sap.com/viewer/123",
                    "control": "governance",
                },
                {
                    "item": 2,
                    "object": "Notifications",
                    "module": "",
                    "impact": "No HR alert",
                    "config_required": "no",
                    "evidence_pointer": "https://example.com/blog",
                    "control": "unknown",
                },
            ]
        },
    }

    validated = validate_record(record, min_items=2)

    rows = validated["validation"]["validation"]
    assert len(rows) == 1
    assert rows[0]["module"] == "RCM"  # normalized
    assert validated["processed"] is False


def test_validate_record_flags_sentinel_with_validation() -> None:
    record = {
        "research_analysis": SENTINEL_TEXT,
        "validation": {
            "validation": [
                {
                    "item": 1,
                    "object": "Route Map",
                    "module": "rcm",
                    "impact": "Approvals blocked",
                    "config_required": "yes",
                    "evidence_pointer": "https://help.sap.com/viewer/123",
                    "control": "governance",
                }
            ]
        },
    }

    validated = validate_record(record, min_items=2)

    assert validated["processed"] is False
    assert "sentinel_with_validation" in validated["failure_reason"]
