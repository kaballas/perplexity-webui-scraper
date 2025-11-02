import os
from types import SimpleNamespace

os.environ["REWRITER_ENABLED"] = "0"

from pplx_harness.processing.pipeline import process_single_record


class FakeClient:
    def __init__(self, response: str) -> None:
        self.response = response

    def ask_stream(self, prompt: str):
        chunk = SimpleNamespace(delta=self.response, last_chunk=True, answer=self.response)
        yield chunk

    def ask_once(self, prompt: str) -> str:
        return self.response


RAW_RESPONSE = """1. Route map approvals cannot be sequenced for teaching staff to meet compliance obligations (SAP Help 123456).
2. HR notifications cannot be triggered for non-teaching hires as required by policy (SAP Help 654321).
{"validation":[
  {"item":1,"object":"Route Map","module":"rcm","impact":"Approvals blocked","config_required":"yes","evidence_pointer":"https://help.sap.com/viewer/123","control":"governance"},
  {"item":2,"object":"Notifications","module":"rcm","impact":"HR not alerted","config_required":"no","evidence_pointer":"https://help.sap.com/viewer/456","control":"governance"}
]}"""


def test_process_single_record_smoke() -> None:
    record = {
        "Title": "Sample",
        "Description": "Workflow approvals for teaching staff with routing gaps.",
        "Area": ["HR"],
        "Product": ["Recruiting"],
    }
    client = FakeClient(RAW_RESPONSE)

    processed = process_single_record(record, 1, 1, client, min_items=2)

    assert processed["processed"] is True
    assert processed["validation"]["validation"]
    assert processed["human_readable"]
