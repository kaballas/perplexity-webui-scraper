from pplx_harness.constants import DEFAULT_MIN_ITEMS
from pplx_harness.prompts.restrictive import build_restrictive_prompt
from pplx_harness.prompts.wricef import (
    DEFAULT_WRICEF_COMPONENTS,
    build_wricef_prompt,
)


def test_build_restrictive_prompt_injects_fields() -> None:
    record = {
        "Title": "Example Title",
        "Description": "Example description",
        "Area": ["HR", "IT"],
        "Product": ["Recruiting"],
        "ObjectOfAnalysis": "Sample object",
        "InScopeModules": "Module A",
        "ConstraintFilter": "Only severe",
    }

    prompt = build_restrictive_prompt(record)

    assert "Title: Example Title" in prompt
    assert "Description: Example description" in prompt
    assert "Area: HR, IT" in prompt
    assert "Product: Recruiting" in prompt
    assert "Object of analysis: Sample object" in prompt
    assert "In-scope modules: Module A" in prompt
    assert f"AT LEAST {DEFAULT_MIN_ITEMS}" in prompt


def test_build_wricef_prompt_injects_context() -> None:
    record = {
        "Title": "Automate Contractor Onboarding",
        "Description": "Need to orchestrate onboarding steps for contingent labor.",
        "Project": "Phoenix",
        "BusinessProcess": ["Onboarding", "Access Provisioning"],
        "Landscape": ["SAP SuccessFactors", "ServiceNow"],
        "Stakeholders": ["HR Ops", "IT Security"],
        "IntegrationPoints": ["ServiceNow -> SuccessFactors"],
        "Assumptions": ["Contractor data provided 48h in advance"],
        "Dependencies": ["Finalize MFA policy"],
        "WRICEFComponents": ["Workflow", "Interfaces"],
        "Timeline": "Q4 2025",
        "Constraints": ["Follow zero-trust principles"],
    }

    prompt = build_wricef_prompt(record)

    assert "Requirement title: Automate Contractor Onboarding" in prompt
    assert "SAP SuccessFactors, ServiceNow" in prompt
    assert "ServiceNow -> SuccessFactors" in prompt
    assert "WRICEF components in focus: Workflow, Interfaces" in prompt
    assert '{"wricef_summary":[' in prompt
    assert "Gating Checklist" in prompt


def test_build_wricef_prompt_defaults_to_standard_components() -> None:
    prompt = build_wricef_prompt({})

    assert DEFAULT_WRICEF_COMPONENTS in prompt
    assert "Gating Checklist" in prompt
