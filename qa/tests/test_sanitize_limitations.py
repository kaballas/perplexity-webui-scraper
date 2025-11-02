from pplx_harness.sanitize.limitations import sanitize_limitations_output


RAW_WITH_VALIDATION = """1. Route map approvals cannot be sequenced for teaching staff to meet compliance obligations (SAP Help 123456).
2. HR notifications cannot be triggered for non-teaching hires as required by policy (SAP Help 654321).
{"validation":[
  {"item":1,"object":"Route Map","module":"rcm","impact":"Approvals blocked","config_required":"yes","evidence_pointer":"https://help.sap.com/viewer/123","control":"governance"},
  {"item":2,"object":"Notifications","module":"rcm","impact":"HR not alerted","config_required":"no","evidence_pointer":"https://help.sap.com/viewer/456","control":"governance"}
]}"""


def test_sanitize_limitations_output_preserves_numbering_and_validation() -> None:
    description = "Workflow approvals for teaching staff with routing gaps."

    result = sanitize_limitations_output(RAW_WITH_VALIDATION, description, min_items=2)

    assert result["text"].startswith(
        "1. Route map approvals cannot be sequenced for teaching staff"
    )
    assert "2. HR notifications cannot be triggered" in result["text"]
    assert result["validation"]["validation"]
    assert len(result["validation"]["validation"]) == 2


def test_sanitize_limitations_output_returns_sentinel_when_no_items() -> None:
    raw = "1. Approvals are available for all processes."
    description = "Generic description without negative cues."

    result = sanitize_limitations_output(raw, description, min_items=2)

    assert result["text"] == "1. No verified limitations found within the specified scope."
    assert result["validation"]["validation"] == []
