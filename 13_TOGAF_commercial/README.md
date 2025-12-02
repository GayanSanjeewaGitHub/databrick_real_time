# TOGAF Enterprise Architecture Framework
## Commercial Bank of Sri Lanka – Data Platform Transformation

---

## Executive Summary

This document suite represents the complete Enterprise Architecture (EA) for the Commercial Bank of Sri Lanka's Data Platform Transformation initiative, following the TOGAF 9.2 Architecture Development Method (ADM).

**Project Name:** Enterprise Data Lakehouse Platform on Azure Databricks  
**Bank:** Commercial Bank of Ceylon PLC  
**Framework:** TOGAF 9.2 ADM  
**Timeline:** 18-24 months (Phased approach)  
**Budget:** LKR 500-750M (~USD 1.5-2.5M)

---

## 1. About Commercial Bank of Sri Lanka

**Overview:**
- Established: 1969
- One of Sri Lanka's largest private sector banks
- 268+ branches across Sri Lanka
- 600+ ATMs nationwide
- Workforce: 5,000+ employees
- Services: Retail Banking, Corporate Banking, Cards, Treasury, SME Banking, Digital Channels

**Digital Services:**
- ComBank Digital (Mobile Banking)
- Internet Banking
- SMS Banking
- Card services (VISA, Mastercard)
- Trade & Supply Chain Finance
- Cash Management Solutions

**Strategic Imperatives:**
- Digital transformation and customer experience enhancement
- Real-time fraud detection and risk management
- 360° customer view and personalization
- Regulatory compliance (CBSL, PDPA)
- Data-driven decision making

---

## 2. TOGAF ADM Phases – Documentation Structure

This EA follows the TOGAF ADM cycle:

```
         ┌─────────────────────┐
         │  Preliminary Phase  │
         │  & Requirements     │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │   Phase A: Vision   │
         └──────────┬──────────┘
                    │
    ┌───────────────┼───────────────┐
    │               │               │
┌───▼────┐   ┌─────▼──────┐   ┌───▼────┐
│Phase B │   │  Phase C   │   │Phase D │
│Business│   │Information │   │Tech    │
│ Arch   │   │Systems Arch│   │Arch    │
└───┬────┘   └─────┬──────┘   └───┬────┘
    │               │               │
    └───────────────┼───────────────┘
                    │
         ┌──────────▼──────────┐
         │ Phase E: Opportun.  │
         │    & Solutions      │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │ Phase F: Migration  │
         │      Planning       │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │Phase G: Implementa- │
         │   tion Governance   │
         └──────────┬──────────┘
                    │
         ┌──────────▼──────────┐
         │  Phase H: Change    │
         │    Management       │
         └─────────────────────┘
```

### Documentation Files

| Phase | File | Description |
|-------|------|-------------|
| **Preliminary** | `00_Preliminary_Framework.md` | EA framework setup, principles, governance |
| **Phase A** | `01_Phase_A_Architecture_Vision.md` | Business drivers, vision, scope, stakeholders |
| **Phase B** | `02_Phase_B_Business_Architecture.md` | Business capabilities, processes, org structure |
| **Phase C - Data** | `03_Phase_C_Data_Architecture.md` | Data domains, models, governance, Unity Catalog |
| **Phase C - App** | `04_Phase_C_Application_Architecture.md` | Applications, integrations, data flows |
| **Phase D** | `05_Phase_D_Technology_Architecture.md` | Azure infrastructure, Databricks, networking |
| **Phase E** | `06_Phase_E_Opportunities_Solutions.md` | Implementation roadmap, work packages |
| **Phase F** | `07_Phase_F_Migration_Planning.md` | Migration strategy, dependencies, risks |
| **Phase G** | `08_Phase_G_Implementation_Governance.md` | Governance model, controls, compliance |
| **Phase H** | `09_Phase_H_Change_Management.md` | Change control, monitoring, continuous improvement |
| **Artifacts** | `10_Architecture_Artifacts.md` | Catalogs, matrices, diagrams |
| **Requirements** | `11_Requirements_Traceability.md` | Detailed requirements with traceability |
| **Standards** | `12_Standards_and_Guidelines.md` | Technical standards, design patterns |

---

## 3. Key Architecture Principles

### 3.1 Business Principles

1. **Customer-Centric**: All architecture decisions prioritize customer experience
2. **Regulatory Compliance First**: CBSL, PDPA, and international standards compliance
3. **Data as Strategic Asset**: Treat data as a core business asset
4. **Risk-Based Approach**: Comprehensive risk assessment and mitigation

### 3.2 Data Principles

5. **Single Source of Truth**: Unified data platform with no duplicate systems
6. **Data Sovereignty**: All customer data resides in bank-controlled infrastructure
7. **Data Quality**: Automated quality checks at every layer (bronze/silver/gold)
8. **Privacy by Design**: PII masking and access controls built-in

### 3.3 Application Principles

9. **Cloud-First**: Leverage cloud capabilities while maintaining control
10. **API-First**: All integrations via secure APIs
11. **Real-Time Capability**: Support streaming and batch processing
12. **Modularity**: Domain-driven design with clear boundaries

### 3.4 Technology Principles

13. **Hybrid Connectivity**: Private connectivity (ExpressRoute) only
14. **Zero Trust Security**: Verify every access request
15. **Encryption Everywhere**: Data at-rest and in-transit encryption
16. **Infrastructure as Code**: All infra defined in version-controlled code

---

## 4. Scope & Boundaries

### In-Scope

- **Data Domains:**
  - Retail Banking (customers, accounts, transactions)
  - Cards (authorizations, settlements, disputes)
  - Loans (origination, servicing, collections)
  - Digital Channels (mobile, web, ATM sessions)
  - Treasury & Markets (basic reference data)
  
- **Technology:**
  - Azure Databricks (Unity Catalog, DLT, Streaming)
  - Azure Data Lake Storage Gen2
  - Azure Key Vault (CMK)
  - ExpressRoute connectivity
  - Event Hubs / Kafka ingestion
  
- **Use Cases:**
  - 360° Customer View
  - Real-time Fraud Detection
  - Regulatory Reporting (CBSL)
  - Credit Risk Analytics
  - Customer Segmentation & Personalization

### Out-of-Scope (Phase 1)

- Core Banking System replacement
- Payment gateway modernization
- Mobile/Internet Banking app redesign
- Branch systems modernization
- International operations data

---

## 5. Stakeholder Overview

| Stakeholder Group | Key Roles | Interest Level |
|-------------------|-----------|----------------|
| **Executive Sponsors** | CEO, CIO, CFO | High - Strategic alignment |
| **Business Owners** | Heads of Retail, Cards, Loans, Treasury | High - Business value realization |
| **IT Leadership** | CTO, Head of Infrastructure, Head of Security | High - Technical delivery |
| **Risk & Compliance** | CISO, Chief Risk Officer, Compliance Head | Critical - Regulatory approval |
| **Data & Analytics** | Chief Data Officer, Head of BI | High - Platform capabilities |
| **Operations** | Branch Ops, Contact Center, Operations Head | Medium - Process changes |
| **External** | CBSL, Auditors, Consultants | High - Compliance & assurance |

---

## 6. Critical Success Factors

1. **Regulatory Approval**: CBSL approval for material outsourcing
2. **Data Sovereignty**: Complete control over encryption keys
3. **Zero Downtime**: No disruption to customer-facing services
4. **User Adoption**: Data scientists and analysts embrace platform
5. **Performance**: Real-time fraud detection <500ms latency
6. **Cost Control**: Stay within budget, demonstrate ROI within 24 months

---

## 7. Architecture Repository Structure

```
13_TOGAF_commercial/
├── README.md (this file)
├── 00_Preliminary_Framework.md
├── 01_Phase_A_Architecture_Vision.md
├── 02_Phase_B_Business_Architecture.md
├── 03_Phase_C_Data_Architecture.md
├── 04_Phase_C_Application_Architecture.md
├── 05_Phase_D_Technology_Architecture.md
├── 06_Phase_E_Opportunities_Solutions.md
├── 07_Phase_F_Migration_Planning.md
├── 08_Phase_G_Implementation_Governance.md
├── 09_Phase_H_Change_Management.md
├── 10_Architecture_Artifacts.md
├── 11_Requirements_Traceability.md
├── 12_Standards_and_Guidelines.md
└── diagrams/
    ├── business_capability_map.drawio
    ├── data_flow_diagram.drawio
    ├── technology_architecture.drawio
    └── migration_roadmap.drawio
```

---

## 8. Next Steps for Panel Presentation

### Preparation Checklist

- [ ] Review all ADM phase documents
- [ ] Validate stakeholder matrix with leadership
- [ ] Prepare executive summary (5-10 slides)
- [ ] Review risk register and mitigation strategies
- [ ] Prepare demo environment (if applicable)
- [ ] Cost-benefit analysis and ROI projection
- [ ] CBSL compliance mapping document
- [ ] Security architecture deep-dive
- [ ] Migration timeline with milestones

### Presentation Flow (90 minutes)

1. **Opening (10 min)**: Business context, strategic drivers
2. **Architecture Vision (15 min)**: Target state, principles, scope
3. **Business Architecture (10 min)**: Capabilities, processes
4. **Technical Architecture (20 min)**: Azure + Databricks + Unity Catalog
5. **Data Architecture (15 min)**: Domains, governance, security
6. **Implementation Plan (15 min)**: Roadmap, phases, dependencies
7. **Risk & Compliance (10 min)**: CBSL, PDPA, mitigation
8. **Q&A (15 min)**

---

## 9. Contact & Governance

**Architecture Review Board (ARB):**
- Meets bi-weekly
- Approves architecture decisions
- Escalates to steering committee

**Document Control:**
- Version: 1.0
- Last Updated: December 2025
- Owner: Enterprise Architecture Team
- Classification: Internal - Confidential

---

## 10. References

- TOGAF 9.2 Standard (The Open Group)
- CBSL Guidelines on Material Outsourcing
- Sri Lanka Personal Data Protection Act (PDPA)
- Azure Well-Architected Framework
- Databricks Reference Architecture for Financial Services
- Unity Catalog Security Best Practices

---

**End of README**
