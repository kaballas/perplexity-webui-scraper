"""
HCMS Prompt Testing Examples
Demonstrates how to use the updated HCMS-specific agent prompts
"""

from debate.prompts import (
    HCMS_PROGRAM_DIRECTOR_PROMPT,
    HUGGING_DEBATER_PROMPT,
    PERPLEXITY_DEBATER_PROMPT,
    INTEGRATION_EXPERT_DEBATER_PROMPT,
    TECHNICAL_SPEC_DEBATER_PROMPT,
    TESTING_AGENT_PROMPT,
    CHANGE_MGMT_AGENT_PROMPT,
    SECURITY_AGENT_PROMPT,
    format_history,
    DebateTurn,
)


def test_integration_design_scenario():
    """
    Scenario: Integration design review for SAP Integration Suite <-> Azure Fabric connectivity
    Participants: Integration Architect, Technical Director, Cybersecurity Lead
    """
    topic = """
    Design Review: SAP Integration Suite to Azure Fabric HR RG Connectivity

    Requirements:
    - Real-time employee data synchronization from SuccessFactors EC to Azure Fabric HR RG
    - Batch payroll data transfer from SAP ECP to HR RG gold layer
    - Support for 46+ downstream systems consuming data from HR RG
    - IS18:2018 and IPOLA compliance for all data transfers
    - Performance target: < 5 min latency for critical HR events
    - Disaster recovery: RPO 4 hours, RTO 8 hours
    """

    # Integration Architect starts the discussion
    integration_turn = DebateTurn(
        speaker="Integration Architect",
        text="I propose a hybrid integration pattern: SAP Integration Suite for real-time events using Event Mesh, and Azure Data Factory for batch payroll transfers. We'll use Azure API Management as the gateway for downstream systems.",
    )

    # Technical Director responds
    technical_turn = DebateTurn(
        speaker="Technical Director",
        text="That approach aligns with our Unified DevOps model. However, we need to ensure SAP BTP and Azure Fabric authentication is properly federated. Also, consider Terraform modules for infrastructure provisioning.",
    )

    # Cybersecurity Lead adds security requirements
    security_turn = DebateTurn(
        speaker="Cybersecurity Lead",
        text="All data transfers must use TLS 1.2+ with mutual TLS for sensitive payroll data. Azure Key Vault for certificate management. Microsoft Sentinel must log all API calls. We need a PIA for PII flowing through the integration layer.",
    )

    history = [integration_turn, technical_turn, security_turn]

    # Format the conversation for the next agent
    conversation = format_history(history)

    print("="*80)
    print("SCENARIO 1: Integration Design Review")
    print("="*80)
    print("\nConversation History:")
    print(conversation)
    print("\n" + "="*80)
    print("Next Agent: Fact-Check Analyst (Perplexity)")
    print("="*80)

    # Generate prompt for fact-checking
    fact_check_prompt = PERPLEXITY_DEBATER_PROMPT.format(
        topic=topic,
        conversation=conversation,
    )

    print("\nFact-Check Prompt Preview:")
    print(fact_check_prompt[:500] + "...\n")


def test_parallel_payroll_run_scenario():
    """
    Scenario: Parallel payroll run planning and reconciliation
    Participants: Test Manager, Cutover Manager, Program Director
    """
    topic = """
    Parallel Payroll Run Planning - Wave 1 (October 2025)

    Scope:
    - 2,000 employees in pilot group
    - Run TSS payroll calculation in parallel with SAP ECP
    - Reconcile pay results within 24 hours
    - Identify and resolve variances > $10
    - Validate downstream feeds (finance, superannuation, tax)
    - Go/no-go decision criteria for Wave 2
    """

    test_manager_turn = DebateTurn(
        speaker="Test Manager",
        text="We need automated reconciliation scripts comparing TSS output with SAP ECP output field-by-field. Tolerance: $0.01 for gross pay, $5 for leave accruals. Azure DevOps pipeline for automated variance reporting.",
    )

    cutover_manager_turn = DebateTurn(
        speaker="Cutover Manager",
        text="Parallel run window: 2 weeks per wave. If variance rate exceeds 5%, we trigger rollback procedures. Downstream systems remain pointed at TSS until final cutover approval from PCG.",
    )

    history = [test_manager_turn, cutover_manager_turn]
    conversation = format_history(history)

    print("\n" + "="*80)
    print("SCENARIO 2: Parallel Payroll Run Planning")
    print("="*80)
    print("\nConversation History:")
    print(conversation)
    print("\n" + "="*80)
    print("Next Agent: Program Director")
    print("="*80)

    program_director_prompt = HCMS_PROGRAM_DIRECTOR_PROMPT.format(
        topic=topic,
        conversation=conversation,
    )

    print("\nProgram Director Prompt Preview:")
    print(program_director_prompt[:500] + "...\n")


def test_security_compliance_scenario():
    """
    Scenario: IS18:2018 and IPOLA compliance validation
    Participants: Cybersecurity Lead, Fact-Check Analyst, Technical Director
    """
    topic = """
    Security Compliance Review: IS18:2018 and IPOLA

    Requirements:
    - All PII data (employee records, payroll) must be encrypted at rest (AES-256)
    - Data in transit: TLS 1.2+ only
    - Audit logging: 7 years retention in OpenText InfoArchive
    - Role-based access control (RBAC) in Azure, RBP in SAP SuccessFactors
    - MFA mandatory for privileged access
    - Penetration testing: quarterly
    - Incident response: 1 hour detection, 4 hour containment
    """

    security_turn = DebateTurn(
        speaker="Cybersecurity Lead",
        text="Current design includes Azure Key Vault for encryption keys, Microsoft Purview for data classification, and Sentinel for SIEM. SAP RBP configured with field-level security for sensitive HR data. Ping Federation handles MFA.",
    )

    history = [security_turn]
    conversation = format_history(history)

    print("\n" + "="*80)
    print("SCENARIO 3: Security Compliance Validation")
    print("="*80)
    print("\nConversation History:")
    print(conversation)
    print("\n" + "="*80)
    print("Next Agent: Fact-Check Analyst")
    print("="*80)

    fact_check_prompt = PERPLEXITY_DEBATER_PROMPT.format(
        topic=topic,
        conversation=conversation,
    )

    print("\nFact-Check Prompt Preview:")
    print(fact_check_prompt[:500] + "...\n")


def test_cutover_wave_planning_scenario():
    """
    Scenario: Planning cutover waves for 46+ downstream systems
    Participants: Cutover Manager, Training Lead, Program Director
    """
    topic = """
    Cutover Wave Planning: Phased Migration (Oct 2025 - Mar 2026)

    Downstream Systems (46+):
    - Wave 1 (Oct 2025): Core HR systems (CIS, IAM) - 2,000 users
    - Wave 2 (Nov 2025): Finance systems (Alloc8, SBS) - 3,000 users
    - Wave 3 (Dec 2025): Educational systems (OneSchool, LMS) - 5,000 users
    - Wave 4 (Jan-Mar 2026): Remaining systems and full rollout

    Considerations:
    - School term schedules (avoid mid-term cutover)
    - Payroll processing windows (avoid pay run dates)
    - Training delivery timelines
    - Hypercare support capacity
    """

    cutover_turn = DebateTurn(
        speaker="Cutover Manager",
        text="Each wave requires 2-week parallel run, 1-week cutover window, and 2-week hypercare. Total: 5 weeks per wave. Detailed runbooks with 500+ tasks per wave, all tracked in Azure DevOps.",
    )

    training_turn = DebateTurn(
        speaker="Training and Adoption Lead",
        text="Training must complete 2 weeks before each wave cutover. WalkMe digital adoption guides deployed to production 1 week prior. Train-the-trainer sessions for 50 DoE HR champions.",
    )

    history = [cutover_turn, training_turn]
    conversation = format_history(history)

    print("\n" + "="*80)
    print("SCENARIO 4: Cutover Wave Planning")
    print("="*80)
    print("\nConversation History:")
    print(conversation)
    print("\n" + "="*80)
    print("Next Agent: Program Director")
    print("="*80)

    program_director_prompt = HCMS_PROGRAM_DIRECTOR_PROMPT.format(
        topic=topic,
        conversation=conversation,
    )

    print("\nProgram Director Prompt Preview:")
    print(program_director_prompt[:500] + "...\n")


def main():
    """Run all test scenarios"""
    print("\n" + "="*80)
    print("HCMS PROMPT TESTING EXAMPLES")
    print("Queensland Department of Education - HCMS Implementation")
    print("="*80)

    test_integration_design_scenario()
    test_parallel_payroll_run_scenario()
    test_security_compliance_scenario()
    test_cutover_wave_planning_scenario()

    print("\n" + "="*80)
    print("All test scenarios completed.")
    print("="*80)


if __name__ == "__main__":
    main()
