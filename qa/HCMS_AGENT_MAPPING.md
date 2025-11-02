# HCMS Agent Roles Mapping

## Agent Prompt → HCMS Team Role Mapping

This document maps the updated debate agent prompts to the HCMS implementation team structure.

---

## Updated Agent Prompts

### 1. HCMS_PROGRAM_DIRECTOR_PROMPT (NEW)
**Maps to:** Program Director (Desmond Rodgers)
**Responsibilities:**
- End-to-end delivery, budget, and stakeholder alignment
- PCG leadership and executive decision-making
- Financial management and vendor contracts
- Governance and compliance oversight
- Strategic direction across all workstreams

---

### 2. HUGGING_DEBATER_PROMPT (Enterprise Architect)
**Maps to:** Enterprise Architect (SAP/Azure Hybrid)
**Responsibilities:**
- Unified architecture across SAP HXM and Microsoft Fabric
- Design Authority alignment
- Cross-platform integration standards
- Hybrid SAP + Azure implementation oversight
- Multi-partner coordination (SI, Data#3, SAP Partner)

---

### 3. PERPLEXITY_DEBATER_PROMPT (Fact-Check Analyst)
**Maps to:** Technical Auditor / Quality Assurance
**Responsibilities:**
- Fact-checking technical documentation
- Validating SAP and Azure best practices
- Compliance verification (IS18:2018, IPOLA, ACSC)
- Integration feasibility validation
- Cross-platform technical validation

---

### 4. INTEGRATION_EXPERT_DEBATER_PROMPT
**Maps to:** Integration Architect
**Responsibilities:**
- SAP Integration Suite design
- Azure Fabric connectivity patterns
- 46+ downstream system integration
- Identity federation (Ping/Entra ID ↔ SAP IAS/IPS)
- Parallel run data flow orchestration
- Master Data Management (MDM) golden record

---

### 5. FUNCTIONAL_SPEC_DEBATER_PROMPT
**Maps to:** SAP Process Analyst (Signavio) + Solution Architect
**Responsibilities:**
- Business process analysis and mapping
- Functional design specifications
- Gap and fit analysis
- User story creation
- Configuration vs customization decisions
- Business workflow design

---

### 6. TECHNICAL_SPEC_DEBATER_PROMPT
**Maps to:** Technical Director (HCMS Technical Stream Lead)
**Responsibilities:**
- SAP BTP and Azure Fabric technical design
- Unified DevOps model architecture
- Terraform infrastructure as code
- Security and compliance technical specs
- Performance and scalability design
- Cross-platform technical standards

---

### 7. CONFIGURATION_AGENT_PROMPT
**Maps to:** SAP HXM Lead + SAP BTP Developer
**Responsibilities:**
- SuccessFactors module configuration
- BTP extension configuration
- Data Sphere model configuration
- Role-based permissions setup
- Workflow and approval processes
- MDF object configuration

---

### 8. DATA_MIGRATION_AGENT_PROMPT
**Maps to:** Data Migration Lead + Fabric Data Engineer
**Responsibilities:**
- TSS to SAP SuccessFactors data migration
- TSS to Azure HR RG data ingestion
- Data cleansing and validation
- Data transformation and mapping
- Azure DataHub pipeline development
- Data quality validation

---

### 9. REPORTING_AGENT_PROMPT
**Maps to:** Fabric Data Engineer + Data Quality Analyst
**Responsibilities:**
- SuccessFactors reporting (Ad Hoc, Canvas, People Analytics)
- Azure Fabric HR RG reporting (gold layer)
- Microsoft Purview data lineage reporting
- Dashboard and KPI design
- Executive reporting and scorecards

---

### 10. SECURITY_AGENT_PROMPT
**Maps to:** Cybersecurity Lead + IAM Specialist
**Responsibilities:**
- IS18:2018 and IPOLA compliance
- SAP RBP and BTP security design
- Azure RBAC and Entra ID configuration
- Identity federation (Ping/Entra ID ↔ SAP IAS/IPS)
- Microsoft Sentinel/Splunk security monitoring
- Data privacy and PII protection
- Audit and access logging

---

### 11. TESTING_AGENT_PROMPT
**Maps to:** Test Manager + Parallel Payroll Run Test Lead
**Responsibilities:**
- SAP HXM and Azure testing coordination
- SAP ALM test management
- Azure DevOps test automation
- Parallel payroll run execution and reconciliation
- Integration testing (end-to-end scenarios)
- Non-functional testing (performance, security)
- Defect management and resolution

---

### 12. CHANGE_MGMT_AGENT_PROMPT
**Maps to:** Cutover Manager + Change Manager
**Responsibilities:**
- Phased cutover planning (Oct 2025 - Mar 2026)
- Parallel payroll run management
- Downstream system switchover (46+ systems)
- DoE CAB coordination
- Stakeholder communication and training
- Change resistance management
- Hypercare support planning

---

### 13. MONITORING_AGENT_PROMPT
**Maps to:** Security Engineer (Sentinel/Splunk) + Environment Manager
**Responsibilities:**
- SAP ALM job monitoring
- Azure Fabric pipeline monitoring
- Integration log analysis
- Microsoft Sentinel/Splunk event correlation
- Performance metrics tracking
- Alert configuration and management

---

### 14. LEARNING_AGENT_PROMPT
**Maps to:** Training and Adoption Lead + WalkMe Specialist
**Responsibilities:**
- LMS administration
- Training curriculum development
- WalkMe digital adoption flows
- User enablement content
- Change adoption strategies

---

### 15. METADATA_EXTRACT_AGENT_PROMPT
**Maps to:** Microsoft Purview Administrator + SAP Data Sphere Engineer
**Responsibilities:**
- SAP Data Sphere metadata extraction
- SuccessFactors OData API metadata
- Microsoft Purview catalog management
- Data lineage and classification
- Metadata documentation and cataloging

---

### 16. INTERNET_RESEARCH_AGENT_PROMPT
**Maps to:** Research and Analysis Support (All Roles)
**Responsibilities:**
- Current trends and best practices research
- Official SAP/Microsoft documentation validation
- Compliance standards research (IS18:2018, IPOLA, ACSC)
- Integration pattern research
- Technology feasibility analysis

---

### 17. CRITIQUE_AGENT_PROMPT
**Maps to:** Design Authority + Audit and Risk Analyst
**Responsibilities:**
- Technical design review and approval
- Compliance auditing (SAP IDPs, release notes)
- Quality assurance across deliverables
- Feedback integration
- Governance validation

---

### 18. COMPRESSION_AGENT_PROMPT
**Maps to:** Service Management Lead (ServiceNow) + Release Manager
**Responsibilities:**
- Conversation history compression
- Plan execution tracking
- Status summarization
- Knowledge management
- Conversation reset management

---

## HCMS Team Structure Coverage

### ✅ Program Leadership
- HCMS_PROGRAM_DIRECTOR_PROMPT → Program Director
- HUGGING_DEBATER_PROMPT → Enterprise Architect
- TECHNICAL_SPEC_DEBATER_PROMPT → Technical Director
- CRITIQUE_AGENT_PROMPT → Design Authority

### ✅ Architecture & Integration
- HUGGING_DEBATER_PROMPT → Enterprise Architect (SAP/Azure Hybrid)
- TECHNICAL_SPEC_DEBATER_PROMPT → Solution Architect (SAP/Azure)
- INTEGRATION_EXPERT_DEBATER_PROMPT → Integration Architect
- DATA_MIGRATION_AGENT_PROMPT → MDM Architect (golden record)

### ✅ SAP Delivery Team
- CONFIGURATION_AGENT_PROMPT → SAP HXM Lead, BTP Developer
- DATA_MIGRATION_AGENT_PROMPT → Data Sphere Engineer
- MONITORING_AGENT_PROMPT → SAP ALM Administrator
- FUNCTIONAL_SPEC_DEBATER_PROMPT → SAP Process Analyst
- LEARNING_AGENT_PROMPT → WalkMe/UX Specialist

### ✅ Azure/Fabric Delivery Team
- DATA_MIGRATION_AGENT_PROMPT → Fabric Data Engineer, DataHub Developer
- TECHNICAL_SPEC_DEBATER_PROMPT → Azure DevOps Engineer, Terraform Engineer
- METADATA_EXTRACT_AGENT_PROMPT → Microsoft Purview Administrator
- MONITORING_AGENT_PROMPT → Security Engineer (Sentinel/Splunk)
- REPORTING_AGENT_PROMPT → Data Quality Analyst

### ✅ Testing and Quality Assurance
- TESTING_AGENT_PROMPT → Test Manager, SIT/UAT Coordinator, Parallel Payroll Run Test Lead
- CRITIQUE_AGENT_PROMPT → Defect Manager (Quality Assurance)
- MONITORING_AGENT_PROMPT → Automation Tester (monitoring integration)

### ✅ Cutover and Transition
- CHANGE_MGMT_AGENT_PROMPT → Cutover Manager, Change Manager
- DATA_MIGRATION_AGENT_PROMPT → Data Migration Lead
- INTEGRATION_EXPERT_DEBATER_PROMPT → Downstream Systems Coordinator

### ✅ Security and Compliance
- SECURITY_AGENT_PROMPT → Cybersecurity Lead, IAM Specialist
- METADATA_EXTRACT_AGENT_PROMPT → Records Compliance Officer (Purview)
- CRITIQUE_AGENT_PROMPT → Audit and Risk Analyst

### ✅ Governance and Support
- CRITIQUE_AGENT_PROMPT → Change Advisory Board (CAB)
- COMPRESSION_AGENT_PROMPT → Release Manager, Service Management Lead
- MONITORING_AGENT_PROMPT → Environment Manager
- LEARNING_AGENT_PROMPT → Training and Adoption Lead

### ✅ External Delivery Partners
- All prompts include multi-partner context: SI, Data#3, SAP Partner, Microsoft Engineering Support

---

## Multi-Agent Debate Scenarios

### Scenario 1: Integration Design Review
**Participants:**
1. INTEGRATION_EXPERT_DEBATER_PROMPT (Integration Architect)
2. TECHNICAL_SPEC_DEBATER_PROMPT (Technical Director)
3. SECURITY_AGENT_PROMPT (Cybersecurity Lead)
4. PERPLEXITY_DEBATER_PROMPT (Fact-Check Analyst)
5. CRITIQUE_AGENT_PROMPT (Design Authority)

**Use Case:** Validating SAP Integration Suite ↔ Azure Fabric connectivity design

---

### Scenario 2: Parallel Payroll Run Planning
**Participants:**
1. TESTING_AGENT_PROMPT (Test Manager, Parallel Payroll Run Test Lead)
2. DATA_MIGRATION_AGENT_PROMPT (Data Migration Lead)
3. INTEGRATION_EXPERT_DEBATER_PROMPT (Integration Architect)
4. CHANGE_MGMT_AGENT_PROMPT (Cutover Manager)
5. HCMS_PROGRAM_DIRECTOR_PROMPT (Program Director)

**Use Case:** Planning parallel run execution, reconciliation strategy, and go/no-go criteria

---

### Scenario 3: Security Compliance Validation
**Participants:**
1. SECURITY_AGENT_PROMPT (Cybersecurity Lead)
2. PERPLEXITY_DEBATER_PROMPT (Fact-Check Analyst)
3. CRITIQUE_AGENT_PROMPT (Audit and Risk Analyst)
4. TECHNICAL_SPEC_DEBATER_PROMPT (Technical Director)

**Use Case:** Validating IS18:2018 and IPOLA compliance across SAP and Azure platforms

---

### Scenario 4: Cutover Wave Planning
**Participants:**
1. CHANGE_MGMT_AGENT_PROMPT (Cutover Manager)
2. TESTING_AGENT_PROMPT (Test Manager)
3. INTEGRATION_EXPERT_DEBATER_PROMPT (Downstream Systems Coordinator)
4. HCMS_PROGRAM_DIRECTOR_PROMPT (Program Director)
5. LEARNING_AGENT_PROMPT (Training and Adoption Lead)

**Use Case:** Planning phased cutover waves (Oct 2025 - Mar 2026) with downstream system switchover

---

### Scenario 5: Technical Architecture Decision
**Participants:**
1. HUGGING_DEBATER_PROMPT (Enterprise Architect)
2. TECHNICAL_SPEC_DEBATER_PROMPT (Technical Director)
3. INTEGRATION_EXPERT_DEBATER_PROMPT (Integration Architect)
4. SECURITY_AGENT_PROMPT (Cybersecurity Lead)
5. CRITIQUE_AGENT_PROMPT (Design Authority)
6. PERPLEXITY_DEBATER_PROMPT (Fact-Check Analyst)

**Use Case:** Approving unified DevOps model (SAP ALM ↔ Azure DevOps) with Design Authority

---

## Summary

All 18 agent prompts have been updated to reflect the HCMS Technical Overview and implementation team structure. The prompts now include:

- Queensland Department of Education context
- Hybrid SAP HXM and Microsoft Azure architecture
- 46+ downstream systems coordination
- Phased cutover timeline (Oct 2025 - Mar 2026)
- Parallel payroll run with TSS reconciliation
- Multi-partner delivery model
- Governance through PCG, Design Authority, DoE CAB
- Compliance with IS18:2018, IPOLA, ACSC guidelines
- Unified DevOps model (SAP ALM ↔ Azure DevOps)

The prompts comprehensively cover all roles in the HCMS team structure and support multi-agent debate scenarios for complex technical and governance decisions.
