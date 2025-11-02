# HCMS Prompt Updates Summary

## Overview
Updated `qa/debate/prompts.py` to align all agent prompts with the Queensland Department of Education's Human Capital Management System (HCMS) Technical Overview and implementation team structure.

## Date
October 18, 2025

## Changes Made

### 1. **HCMS_PROGRAM_DIRECTOR_PROMPT** (NEW)
Added comprehensive Program Director role covering:
- Strategic direction and accountability
- Financial management across all workstreams
- Governance through PCG, Design Authority, and DoE CAB
- Stakeholder engagement (executives, business units, delivery partners)
- Program delivery oversight across 9 major workstreams
- Risk and issue management
- Milestone tracking (parallel run, phased cutover Oct 2025 - Mar 2026)
- Key decision points requiring PCG approval

### 2. **HUGGING_DEBATER_PROMPT** (UPDATED)
Enhanced Enterprise Architect role with:
- Hybrid SAP HXM and Microsoft Azure program context
- SAP HXM Suite: SuccessFactors, BTP, Data Sphere, ALM
- Microsoft Azure: Fabric HR RG (Medallion architecture), DataHub, Purview, Sentinel
- Integration across 46+ downstream systems (CIS, IAM, Alloc8, SBS, OneSchool)
- Phased cutover from legacy TSS (Oct 2025 - Mar 2026)
- Unified DevOps model (SAP ALM ↔ Azure DevOps)
- IS18:2018 and IPOLA compliance
- Multi-partner coordination: SI, Data#3, SAP Partner

### 3. **PERPLEXITY_DEBATER_PROMPT** (UPDATED)
Enhanced fact-checking analyst role with:
- HCMS program context and hybrid architecture
- Expanded source requirements: SAP/Microsoft official docs, ACSC standards
- Special verification areas:
  - SAP BTP ↔ Azure Fabric integration patterns
  - SAP ALM ↔ Azure DevOps synchronization
  - Microsoft Purview ↔ SAP Data Sphere interoperability
  - OpenText xECM/InfoArchive integration
  - Parallel payroll run technical feasibility (TSS vs SAP ECP)
  - Identity federation (Ping/Entra ID ↔ SAP IAS/IPS)
- HCMS-specific notes in output format (version dependencies, cutover impacts)

### 4. **INTEGRATION_EXPERT_DEBATER_PROMPT** (UPDATED)
Enhanced Integration Architect role with:
- Three-layer integration architecture:
  - SAP Integration Layer (Integration Suite, BTP, Data Sphere, OpenText)
  - Azure Integration Layer (Fabric HR RG, DataHub, Purview, API Management)
  - Cross-Platform Integration (SAP ↔ Azure connectivity, MDM golden record)
- Identity & Access Integration (Ping/Entra ID ↔ SAP IAS/IPS)
- Cutover & Parallel Run Integration:
  - Dual data flows: TSS → Azure and SAP → Azure
  - Payroll reconciliation mechanisms (TSS vs SAP ECP)
  - Downstream system switchover strategies (46+ systems)
  - Rollback and failover patterns
- Multi-partner coordination and Design Authority validation

### 5. **TECHNICAL_SPEC_DEBATER_PROMPT** (UPDATED)
Enhanced Technical Director role with five specification domains:
1. **SAP Platform Technical Specs:**
   - BTP architecture, Data Sphere, ALM, API standards
2. **Azure Platform Technical Specs:**
   - Fabric HR RG Lakehouse, DevOps pipelines, Terraform, Purview
3. **Cross-Platform Technical Specs:**
   - SAP ↔ Azure connectivity, Unified DevOps, monitoring, DR
4. **Security & Compliance Technical Specs:**
   - IS18:2018 controls, IPOLA compliance, network architecture, identity federation
5. **Performance & Scalability:**
   - API throttling, pipeline optimization, capacity planning, caching

### 6. **TESTING_AGENT_PROMPT** (UPDATED)
Enhanced Test Manager role with:
- **SAP Testing:** SuccessFactors modules, BTP extensions, Data Sphere, ALM
- **Azure Testing:** Fabric HR RG pipelines, DataHub, Purview, DevOps CI/CD, Terraform
- **Integration Testing:** End-to-end scenarios, API testing, event-driven, MDM, identity federation
- **Parallel Run & Cutover Testing:**
  - Parallel payroll run execution and reconciliation (TSS vs SAP ECP)
  - Variance analysis and root cause investigation
  - Cutover validation and downstream system switchover (46+ systems)
  - Rollback and failover testing
- **Non-Functional Testing:** Performance, security, compliance, DR
- **Test Automation:** SAP ALM, Azure DevOps, API automation, data validation
- Test environment management across SAP and Azure

### 7. **CHANGE_MGMT_AGENT_PROMPT** (UPDATED)
Enhanced Cutover Manager and Change Manager role with six domains:
1. **Cutover Planning & Execution:**
   - Phased migration strategy (Oct 2025 - Mar 2026)
   - Wave-based rollout approach
   - Data migration cutover (TSS → SAP/Azure)
   - Downstream system switchover (46+ systems)
   - Parallel payroll run management and reconciliation
   - Hypercare support planning
2. **Change Control & Release Management:**
   - SAP quarterly releases, Unified DevOps, DoE CAB coordination
3. **Stakeholder Management & Communication:**
   - Communication planning, readiness assessments, resistance management
4. **Training & Adoption:**
   - Role-based training, WalkMe digital adoption, train-the-trainer
5. **Risk Management & Business Continuity:**
   - Rollback procedures, contingency planning, post-cutover monitoring
6. **Governance & Reporting:**
   - Change metrics, governance compliance, status reporting

### 8. **SECURITY_AGENT_PROMPT** (UPDATED)
Enhanced Cybersecurity Lead role with seven security domains:
1. **SAP Security Architecture:**
   - SuccessFactors RBP, BTP security, Data Sphere security
2. **Azure Security Architecture:**
   - Fabric HR RG security, Entra ID, Purview governance, Sentinel SOC
3. **Identity Federation & SSO:**
   - Ping/Entra ID integration, SAP IAS/IPS, unified SSO
4. **Integration Security:**
   - API security, data in transit (TLS 1.2+), data at rest (AES-256)
5. **Compliance & Governance:**
   - IS18:2018, IPOLA, ACSC Essential Eight, audit logging, SoD analysis
6. **Data Privacy & Protection:**
   - PII protection, data masking, OpenText records management, penetration testing
7. **Incident Response & Disaster Recovery:**
   - Security incident management, DR testing, business continuity

## Program-Specific Context Embedded

All prompts now include:
- **Queensland Department of Education** as the client organization
- **46+ downstream systems** requiring coordination (CIS, IAM, Alloc8, SBS, OneSchool, etc.)
- **Phased cutover timeline:** October 2025 - March 2026
- **Parallel payroll run** with TSS vs SAP ECP reconciliation
- **Legacy TSS system** as source for data migration
- **Delivery partners:** System Integrator (SI), Data#3 (Microsoft Partner), SAP Partner
- **Governance bodies:** PCG, Design Authority, DoE CAB
- **Compliance frameworks:** IS18:2018, IPOLA, ACSC guidelines
- **Unified DevOps model:** SAP ALM ↔ Azure DevOps
- **Infrastructure as Code:** Terraform automation
- **Production readiness milestone:** Microsoft Fabric HR RG (Nov 2025)

## Team Structure Alignment

Prompts now reflect the comprehensive HCMS team composition:
- **Program Leadership:** Program Director, Technical Director, PCG, Design Authority
- **Architecture & Integration:** Enterprise Architect, Solution Architects (SAP/Azure), Integration Architect, MDM Architect
- **SAP Delivery Team:** SAP HXM Lead, BTP Developer, Data Sphere Engineer, ALM Admin, Process Analyst, WalkMe Specialist, OpenText Specialists
- **Azure/Fabric Delivery Team:** Fabric Data Engineer, DataHub Developer, DevOps Engineer, Terraform Engineer, Purview Admin, Security Engineer, Data Quality Analyst
- **Testing and QA:** Test Manager, SIT/UAT Coordinator, Parallel Payroll Run Test Lead, Defect Manager, Automation Tester
- **Cutover and Transition:** Cutover Manager, Data Migration Lead, Downstream Systems Coordinator, Change Manager
- **Security and Compliance:** Cybersecurity Lead, IAM Specialist, Records Compliance Officer, Audit and Risk Analyst
- **Governance and Support:** CAB, Release Manager, Environment Manager, Service Management Lead, Training and Adoption Lead
- **External Delivery Partners:** SI, Data#3, Microsoft Engineering Support, SAP Partner

## Next Steps

1. **Test updated prompts** with sample HCMS scenarios
2. **Validate agent responses** against HCMS Technical Overview requirements
3. **Create role-specific test cases** for each updated agent
4. **Document agent interaction patterns** for multi-agent debates
5. **Establish prompt versioning** for future HCMS updates

## Files Modified
- `qa/debate/prompts.py` - All agent prompts updated with HCMS context

## Files Created
- `qa/HCMS_PROMPT_UPDATES.md` - This summary document
