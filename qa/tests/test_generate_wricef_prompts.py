from __future__ import annotations

from pathlib import Path
from typing import Any

import json
import pytest

import generate_wricef_prompts as wricef_cli


def test_load_records_accepts_list(tmp_path: Path) -> None:
    payload = [
        {"Title": "Requirement One", "Description": "First requirement"},
        {"Title": "Requirement Two", "Description": "Second requirement"},
    ]
    path = tmp_path / "records.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    records = wricef_cli.load_records(path)

    assert len(records) == 2
    assert records[0]["Title"] == "Requirement One"


def test_load_records_accepts_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "records.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"Title": "T1"}),
                json.dumps({"Title": "T2"}),
            ]
        ),
        encoding="utf-8",
    )

    records = wricef_cli.load_records(path)

    assert len(records) == 2
    assert records[1]["Title"] == "T2"


def test_load_records_rejects_non_object(tmp_path: Path) -> None:
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    with pytest.raises(wricef_cli.RecordFormatError):
        wricef_cli.load_records(path)


def test_load_records_flattens_mapping(tmp_path: Path) -> None:
    payload = {
        "Section A": [
            {"requirement": "Req 1"},
            {"requirement": "Req 2"},
        ]
    }
    path = tmp_path / "records.json"
    path.write_text(json.dumps(payload), encoding="utf-8")

    records = wricef_cli.load_records(path)

    assert len(records) == 2
    assert records[0]["requirement"] == "Req 1"
    assert records[0]["section"] == "Section A"


def test_build_prompts_returns_strings() -> None:
    records = [{"Title": "Sample", "Description": "Testing prompt generation"}]

    prompts = wricef_cli.build_prompts(records)

    assert len(prompts) == 1
    assert "Requirement title: Sample" in prompts[0]


def test_build_prompts_infers_requirement_field() -> None:
    prompts = wricef_cli.build_prompts([{"requirement": "Support workflow integration"}])

    assert "Requirement title: Support workflow integration" in prompts[0]
    assert "Requirement summary: Support workflow integration" in prompts[0]


def test_process_records_attaches_completion(monkeypatch: pytest.MonkeyPatch) -> None:
    records = [{"Title": "Req"}]
    prompts = ["Prompt text"]
    expected_completion = "Completion text"
    expected_raw = {"raw": True}

    def fake_call(prompt: str, *, config: wricef_cli.ApiConfig) -> tuple[str, dict[str, Any]]:
        assert prompt == "Prompt text"
        assert config.token == "token"
        return expected_completion, expected_raw

    monkeypatch.setattr(wricef_cli, "call_wricef_api", fake_call)
    config = wricef_cli.ApiConfig(
        url="http://example.com",
        token="token",
        model="model",
        temperature=0.1,
        timeout=5.0,
        include_raw=True,
    )

    enriched = wricef_cli.process_records(records, prompts, api_config=config)

    assert enriched[0]["wricef_prompt"] == "Prompt text"
    assert enriched[0]["wricef_completion"] == expected_completion
    assert enriched[0]["wricef_completion_raw"] == expected_raw
    assert enriched[0]["wricef_record_key"] == "Req"


def test_process_records_handles_api_error(monkeypatch: pytest.MonkeyPatch) -> None:
    records = [{"Title": "Req"}]
    prompts = ["Prompt text"]

    def fake_call(prompt: str, *, config: wricef_cli.ApiConfig) -> tuple[str, dict[str, Any]]:
        raise RuntimeError("boom")

    monkeypatch.setattr(wricef_cli, "call_wricef_api", fake_call)
    config = wricef_cli.ApiConfig(
        url="http://example.com",
        token="token",
        model="model",
        temperature=0.1,
        timeout=5.0,
        include_raw=False,
    )

    enriched = wricef_cli.process_records(records, prompts, api_config=config)

    assert "wricef_completion_error" in enriched[0]
    assert "boom" in enriched[0]["wricef_completion_error"]


def test_format_stdout_includes_prompt_and_completion() -> None:
    records = [
        {
            "wricef_index": 1,
            "wricef_prompt": "Prompt",
            "wricef_completion": "Completion",
        }
    ]

    output = wricef_cli._format_stdout(records)

    assert "--- Record 1 ---" in output
    assert "Prompt" in output
    assert "Completion" in output
    assert output.endswith("\n")


def test_write_output_jsonl(tmp_path: Path) -> None:
    records = [{"wricef_index": 1, "wricef_prompt": "Prompt"}]
    path = tmp_path / "results.jsonl"

    wricef_cli.write_output(path, records)

    content = path.read_text(encoding="utf-8").strip()
    assert json.loads(content)["wricef_index"] == 1


def test_main_respects_max_records(tmp_path: Path) -> None:
    payload = [
        {"requirement": f"Requirement {idx}", "response": "Details"}
        for idx in range(3)
    ]
    input_path = tmp_path / "records.json"
    output_path = tmp_path / "out.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")

    exit_code = wricef_cli.main(
        [
            str(input_path),
            "--output",
            str(output_path),
            "--allow-anonymous",
            "--max-records",
            "2",
        ]
    )

    assert exit_code == 0
    results = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(results) == 2


def test_resume_skips_existing_records(tmp_path: Path) -> None:
    payload = [
        {"id": "FR-1", "requirement": "Existing requirement"},
        {"id": "FR-2", "requirement": "New requirement"},
    ]
    existing = [
        {
            "id": "FR-1",
            "wricef_record_key": "FR-1",
            "wricef_index": 1,
            "wricef_prompt": "old prompt",
        }
    ]
    input_path = tmp_path / "records.json"
    output_path = tmp_path / "out.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    output_path.write_text(json.dumps(existing), encoding="utf-8")

    exit_code = wricef_cli.main(
        [
            str(input_path),
            "--output",
            str(output_path),
            "--allow-anonymous",
            "--resume",
        ]
    )

    assert exit_code == 0
    combined = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(combined) == 2
    keys = {row["wricef_record_key"] for row in combined}
    assert "FR-1" in keys and "FR-2" in keys
    fr2 = next(row for row in combined if row["wricef_record_key"] == "FR-2")
    assert fr2["wricef_index"] == 2


def test_reprocess_index_replaces_existing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    payload = [
        {"id": "FR-1", "requirement": "Existing requirement"},
        {"id": "FR-2", "requirement": "Second requirement"},
    ]
    existing = [
        {
            "id": "FR-1",
            "wricef_record_key": "FR-1",
            "wricef_index": 1,
            "wricef_prompt": "old prompt",
        },
        {
            "id": "FR-2",
            "wricef_record_key": "FR-2",
            "wricef_index": 2,
            "wricef_prompt": "keep prompt",
        },
    ]
    input_path = tmp_path / "records.json"
    output_path = tmp_path / "out.json"
    input_path.write_text(json.dumps(payload), encoding="utf-8")
    output_path.write_text(json.dumps(existing), encoding="utf-8")

    def fake_build(records: list[dict[str, Any]]) -> list[str]:
        return ["PROMPT"] * len(records)

    def fake_process(
        records: list[dict[str, Any]],
        prompts: list[str],
        *,
        api_config: wricef_cli.ApiConfig | None,
        start_index: int,
    ) -> list[dict[str, Any]]:
        assert len(records) == 1
        assert records[0]["id"] == "FR-1"
        assert start_index == 1
        return [
            {
                "wricef_index": start_index,
                "wricef_prompt": "new prompt",
                "wricef_record_key": wricef_cli._record_key(records[0]),
            }
        ]

    monkeypatch.setattr(wricef_cli, "build_prompts", fake_build)
    monkeypatch.setattr(wricef_cli, "process_records", fake_process)

    exit_code = wricef_cli.main(
        [
            str(input_path),
            "--output",
            str(output_path),
            "--allow-anonymous",
            "--reprocess-index",
            "1",
        ]
    )

    assert exit_code == 0
    combined = json.loads(output_path.read_text(encoding="utf-8"))
    assert len(combined) == 2
    combined.sort(key=lambda row: row["wricef_index"])
    assert combined[0]["wricef_prompt"] == "new prompt"
    assert combined[1]["wricef_prompt"] == "keep prompt"
    assert combined[0]["wricef_record_key"] == "FR-1"
    assert combined[1]["wricef_record_key"] == "FR-2"


def test_review_index_adds_review(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Input path is required by the CLI but unused during review.
    input_path = tmp_path / "records.json"
    input_path.write_text("[]", encoding="utf-8")

    existing = [
        {
            "id": "FR-1",
            "wricef_record_key": "FR-1",
            "wricef_index": 1,
            "wricef_prompt": "prompt one",
            "wricef_completion": "completion one",
        },
        {
            "id": "FR-2",
            "wricef_record_key": "FR-2",
            "wricef_index": 2,
            "wricef_prompt": "prompt two",
            "wricef_completion": "completion two",
        },
    ]
    output_path = tmp_path / "out.json"
    output_path.write_text(json.dumps(existing), encoding="utf-8")

    captured_prompt: dict[str, str] = {}

    def fake_call(prompt: str, *, config: wricef_cli.ApiConfig) -> tuple[str, dict[str, Any]]:
        captured_prompt["value"] = prompt
        assert config.token == "token"
        return "Review OK", {"raw": True}

    monkeypatch.setattr(wricef_cli, "call_wricef_api", fake_call)

    exit_code = wricef_cli.main(
        [
            str(input_path),
            "--output",
            str(output_path),
            "--api-token",
            "token",
            "--include-raw",
            "--review-index",
            "2",
        ]
    )

    assert exit_code == 0
    assert "value" in captured_prompt
    assert "Review Output Requirements" in captured_prompt["value"]

    combined = json.loads(output_path.read_text(encoding="utf-8"))
    fr2 = next(row for row in combined if row["wricef_index"] == 2)
    assert fr2["wricef_review"] == "Review OK"
    assert "wricef_review_prompt" in fr2
    assert fr2["wricef_review_prompt"] == captured_prompt["value"]
    assert "wricef_review_raw" in fr2
    assert fr2["wricef_review_record_key"] == "FR-2"


def test_review_index_zero_reviews_all_then_delta(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_path = tmp_path / "records.json"
    input_path.write_text("[]", encoding="utf-8")

    existing = [
        {
            "id": "FR-1",
            "wricef_record_key": "FR-1",
            "wricef_index": 1,
            "wricef_prompt": "prompt one",
            "wricef_completion": "completion one",
        },
        {
            "id": "FR-2",
            "wricef_record_key": "FR-2",
            "wricef_index": 2,
            "wricef_prompt": "prompt two",
            "wricef_completion": "completion two",
        },
    ]
    output_path = tmp_path / "out.json"
    output_path.write_text(json.dumps(existing), encoding="utf-8")

    call_log: list[int] = []

    def fake_call(prompt: str, *, config: wricef_cli.ApiConfig) -> tuple[str, dict[str, Any]]:
        assert config.token == "token"
        json_fragment = prompt.split("Record Under Review (JSON):\n", 1)[1]
        record_json = json_fragment.split("\n\nReview Output Requirements", 1)[0]
        record = json.loads(record_json)
        call_log.append(record["wricef_index"])
        return f"Review for {record['wricef_index']}", {}

    monkeypatch.setattr(wricef_cli, "call_wricef_api", fake_call)

    exit_code = wricef_cli.main(
        [
            str(input_path),
            "--output",
            str(output_path),
            "--api-token",
            "token",
            "--review-index",
            "0",
        ]
    )

    assert exit_code == 0
    assert call_log == [1, 2]

    combined = json.loads(output_path.read_text(encoding="utf-8"))
    fr1 = next(row for row in combined if row["wricef_index"] == 1)
    fr2 = next(row for row in combined if row["wricef_index"] == 2)
    assert fr1["wricef_review"].startswith("Review for 1")
    assert fr2["wricef_review"].startswith("Review for 2")
    assert fr1["wricef_review_record_key"] == "FR-1"
    assert fr2["wricef_review_record_key"] == "FR-2"

    # Add a new record without review, ensuring delta behaviour.
    combined.append(
        {
            "id": "FR-3",
            "wricef_record_key": "FR-3",
            "wricef_index": 3,
            "wricef_prompt": "prompt three",
            "wricef_completion": "completion three",
        }
    )
    output_path.write_text(json.dumps(combined), encoding="utf-8")
    call_log.clear()

    exit_code = wricef_cli.main(
        [
            str(input_path),
            "--output",
            str(output_path),
            "--api-token",
            "token",
            "--review-index",
            "0",
        ]
    )

    assert exit_code == 0
    assert call_log == [3]

    combined = json.loads(output_path.read_text(encoding="utf-8"))
    fr3 = next(row for row in combined if row["wricef_index"] == 3)
    assert fr3["wricef_review"].startswith("Review for 3")
    assert fr3["wricef_review_record_key"] == "FR-3"
