# Executive Business Case Summary
## Commercial Bank of Sri Lanka – Data Platform Transformation

**For Panel Presentation**

---

## 1. Executive Summary (2-Minute Pitch)

Commercial Bank of Sri Lanka seeks approval to implement a modern, secure enterprise data platform on Azure Databricks to address critical business challenges:

- **Problem**: Fragmented data across 12+ systems, no real-time analytics, 24-48 hour delays in insights, LKR 150M/year fraud losses
- **Solution**: Unified data lakehouse with real-time fraud detection, customer 360° view, automated regulatory reporting
- **Investment**: LKR 707M (USD 2.36M) over 18 months
- **Returns**: LKR 1,160M benefits over 3 years → **64% ROI, 22-month payback**
- **Strategic Impact**: Foundation for AI/ML, competitive advantage, regulatory compliance

**Decision Sought**: Approval to proceed with Phase 0 (Foundation) and CBSL submission.

---

## 2. Strategic Alignment

### 2.1 Bank's Strategic Priorities (2025-2027)

| Priority | How This Initiative Delivers |
|----------|------------------------------|
| **Digital-First Banking** | Real-time personalization, mobile analytics, omnichannel view |
| **Customer Experience Excellence** | 360° view enables targeted offers, faster service (NPS +12 points) |
| **Operational Efficiency** | Automated data pipelines, self-service analytics (30% cost reduction) |
| **Risk Management** | Real-time fraud detection (60% fraud loss reduction), credit risk models |
| **Regulatory Compliance** | Automated CBSL reporting, PDPA-compliant data governance |
| **Innovation & Growth** | ML/AI platform for new products (churn prediction, next-best-offer) |

### 2.2 Competitive Context

**Industry Trend**: Leading banks globally have migrated to cloud data platforms.
- **DBS Bank (Singapore)**: Databricks for fraud detection, reduced fraud by 70%
- **Standard Chartered**: Azure + Databricks for 360° customer view across 60+ markets
- **Regional Banks**: Nations Trust Bank (Sri Lanka) exploring cloud analytics

**Competitive Risk**: If we delay, competitors gain first-mover advantage in data-driven banking.

---

## 3. Current State Pain Points

### 3.1 Operational Challenges

| Issue | Impact | Cost to Bank |
|-------|--------|--------------|
| **Manual Reconciliation** | 2 FTEs, 40 hrs/week | LKR 12M/year labor + errors |
| **Slow Time-to-Insight** | 3-week average for new reports | Missed revenue opportunities |
| **Fraud Detection Delays** | Daily batch (not real-time) | LKR 150M/year fraud losses |
| **CBSL Reporting** | 5 days to compile, manual | Risk of late filing penalties (LKR 50M) |
| **No Self-Service** | 80% of reports require IT | BI team bottleneck, frustrated users |
| **Aging Infrastructure** | Oracle Exadata 6 years old, 80% capacity | Imminent hardware refresh (LKR 200M) |

### 3.2 Strategic Limitations

- **Cannot launch real-time products** (e.g., instant credit decisioning)
- **Limited ML/AI capability** (no feature store, model registry)
- **Siloed data** → inconsistent customer view → poor targeting
- **Regulatory risk** → slow response to CBSL data requests

---

## 4. Proposed Solution

### 4.1 Target Architecture (High Level)

```
┌─────────────────────────────────────────────────────────────────────┐
│  DATA MOVEMENT ARCHITECTURE                                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  On-Premises (Colombo Data Center)                                 │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ Source Systems: Core Banking, ATM, Internet Banking│           │
│  │             ↓                                       │           │
│  │ Local Data Warehouse (Oracle/SQL Server)           │           │
│  │   - 600 GB historical data                         │           │
│  │   - 10-15 GB daily incremental                     │           │
│  │             ↓                                       │           │
│  │ ON-PREM ETL COMPONENTS (Required):                 │           │
│  │                                                     │           │
│  │ Option A: Azure Data Factory SHIR (Recommended)    │           │
│  │   - Self-Hosted Integration Runtime (2 VMs)        │           │
│  │   - Incremental query: WHERE updated_at > @LastRun │           │
│  │   - Exports to Parquet, uploads to ADLS            │           │
│  │                                                     │           │
│  │ Option B: Debezium CDC (Real-Time)                 │           │
│  │   - Debezium connector (2 VMs)                     │           │
│  │   - On-prem Kafka cluster (3 nodes)                │           │
│  │   - Captures transaction logs (INSERT/UPDATE/DEL)  │           │
│  │                                                     │           │
│  │ Option C: Custom Python/PySpark ETL                │           │
│  │   - Scheduled script (hourly/daily) on 1 VM        │           │
│  │   - SELECT changed records, export, upload         │           │
│  └─────────────────────────────────────────────────────┘           │
│                      ↓                                              │
│         ┌────────────────────────────┐                             │
│         │  ExpressRoute 1 Gbps       │ ← Private, Secure           │
│         │  (125 MB/s = 8.6 TB/day)   │    No Public Internet       │
│         │  Dialog/SLT Provider       │    TLS 1.3 Encrypted        │
│         └────────────────────────────┘                             │
│                      ↓                                              │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ Azure (Southeast Asia - Singapore)                  │           │
│  │                                                     │           │
│  │ Azure Data Lake Gen2 (CMK Encrypted)               │           │
│  │   /raw      ← Initial load (600 GB, one-time)      │           │
│  │   /bronze   ← Daily incremental (10-15 GB)         │           │
│  │   /silver   ← Cleansed, validated                  │           │
│  │   /gold     ← Business-ready analytics             │           │
│  │                                                     │           │
│  │ Databricks Lakehouse                                │           │
│  │   - Auto Loader (batch ingestion)                  │           │
│  │   - Spark Streaming (real-time via Kafka)          │           │
│  │   - Delta Live Tables (ETL pipelines)              │           │
│  │                                                     │           │
│  │ Unity Catalog (Governance)                          │           │
│  │   - Column masking (NIC, email, mobile)            │           │
│  │   - Row-level security (branch-based)              │           │
│  │   - Full audit trail (7-year retention)            │           │
│  │                                                     │           │
│  │ Analytics Layer                                     │           │
│  │   - Power BI (self-service dashboards)             │           │
│  │   - Tableau (executive reporting)                  │           │
│  │   - SQL Warehouse (ad-hoc queries)                 │           │
│  │   - ML Models (fraud detection, churn prediction)  │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

KEY MIGRATION PATTERNS:
1. Initial Bulk Load: 600 GB historical data over 2-3 hours (one-time)
2. Daily Incremental: 10-15 GB changed records over ~2 minutes
3. Real-Time Streaming: Kafka → Event Hubs for fraud detection (<1s latency)
```

### 4.2 Key Capabilities

1. **Real-Time Streaming**: Kafka/Event Hubs → Spark Streaming → <500ms fraud detection
2. **Batch Analytics**: Delta Live Tables for ETL (Bronze/Silver/Gold)
3. **Customer 360°**: Unified view (demographics + accounts + transactions + loans + cards)
4. **ML Platform**: Feature store, model registry, automated retraining
5. **Self-Service**: SQL Warehouse for analysts (no-code SQL queries)
6. **Governance**: Unity Catalog (NIC masking, branch-level row filters, full audit trail)

### 4.3 Regulatory Compliance

**CBSL Material Outsourcing:**
- ✅ Data resides in Southeast Asia region (Singapore)
- ✅ Customer-Managed Keys (CMK) in bank-controlled Key Vault → key revocation capability
- ✅ ExpressRoute private connectivity (no public internet)
- ✅ Comprehensive audit trail (7-year retention)

**PDPA (Personal Data Protection Act):**
- ✅ PII masking via Unity Catalog (NIC, email, mobile)
- ✅ Data minimization (row-level security by branch)
- ✅ Automated breach detection & alerting

---

## 5. Financial Case

### 5.1 Investment Breakdown

| Category | LKR (Millions) | USD | % of Total |
|----------|----------------|-----|------------|
| **Azure Infrastructure** | 180 | 600K | 25% |
| **Databricks Licenses** | 240 | 800K | 34% |
| **Professional Services** | 150 | 500K | 21% |
| **Training & Change Mgmt** | 45 | 150K | 6% |
| **Contingency (15%)** | 92 | 307K | 13% |
| **TOTAL** | **707** | **2.36M** | **100%** |

**Funding**: Capex (Year 1), with Opex for years 2-3 covered by savings.

### 5.2 Benefits (3-Year NPV)

| Benefit Category | Yr 1 | Yr 2 | Yr 3 | Total (LKR M) | Assumptions |
|------------------|------|------|------|---------------|-------------|
| **Fraud Loss Reduction** | 54 | 90 | 90 | **234** | 60% reduction (baseline 150M/yr) |
| **Operational Efficiency** | 72 | 120 | 120 | **312** | 30% cost reduction in data ops |
| **Revenue Growth** | 60 | 120 | 200 | **380** | Cross-sell +10%, retention +5% |
| **Regulatory Fine Avoidance** | 30 | 50 | 50 | **130** | Timely CBSL filing, no penalties |
| **Infra Cost Savings** | 24 | 40 | 40 | **104** | Decommission Oracle Exadata |
| **TOTAL BENEFITS** | **240** | **420** | **500** | **1,160** | |

**Net Benefit (3 Years)**: LKR 1,160M - 707M = **LKR 453M**

**ROI**: (453 / 707) × 100 = **64%**

**Payback Period**: ~22 months (during Year 2)

### 5.3 Sensitivity Analysis

| Scenario | Assumption Change | Impact on ROI |
|----------|-------------------|---------------|
| **Base Case** | As above | 64% |
| **Conservative** | Benefits -20% | 35% (still positive) |
| **Optimistic** | Benefits +20% | 93% |
| **Cost Overrun** | Costs +25% | 41% (still viable) |
| **Delayed Benefits** | Benefits delayed 6 months | 48% (payback 28 months) |

**Conclusion**: Positive ROI even in conservative scenarios.

---

## 6. Implementation Roadmap

### 6.1 Phased Approach (18 Months)

```
Phase 0: Foundation (Month 0-2)        █████
  - CBSL approval, ExpressRoute, Azure setup
  
Phase 1: Cards & Fraud (Month 3-6)    █████████
  - Real-time fraud detection LIVE ← First Win
  
Phase 2: Retail Banking (Month 7-10)  ██████████
  - Customer 360°, transactions, regulatory reporting
  
Phase 3: Loans & Channels (Month 11-14) ████████
  - Complete data lakehouse
  
Phase 4: Optimization (Month 15-18)   ██████
  - Self-service rollout, legacy decommissioning
```

**Early Win**: Fraud detection live in **Month 6** → immediate LKR 54M/year savings.

### 6.2 Key Milestones

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| **M1: CBSL Approval** | Month 2 | Regulatory green light |
| **M2: Dev Environment Live** | Month 2 | Team can start development |
| **M3: Fraud Detection Go-Live** | Month 6 | Real-time fraud alerts |
| **M4: Customer 360° Launch** | Month 9 | Unified customer view |
| **M5: All Domains Operational** | Month 14 | Full lakehouse |
| **M6: Legacy Decommissioned** | Month 17 | Oracle Exadata shutdown |
| **M7: Project Closure** | Month 18 | Handover to BAU |

---

## 7. Risk Management

### 7.1 Top 5 Risks & Mitigation

| Rank | Risk | Mitigation | Status |
|------|------|------------|--------|
| **1** | **CBSL approval delayed** | Pre-submission workshops, compliance consultant hired | Active |
| **2** | **Skills gap (Databricks/Spark)** | 8-week training + implementation partner support | Planned |
| **3** | **ExpressRoute lead time (8-12 weeks)** | Order immediately, parallel VPN backup | Active |
| **4** | **Legacy system integration complexity** | POC in Phase 0, custom connector budget | Mitigated |
| **5** | **User adoption resistance** | Change mgmt program, early wins, exec sponsorship | Planned |

### 7.2 Contingency Plans

- **Technical Failure**: Rollback to legacy system (parallel running for 2-4 weeks per phase)
- **Budget Overrun**: 15% contingency reserve (LKR 92M) + monthly cost tracking
- **Timeline Delay**: Phase-gate approvals, ability to defer Phase 4 if needed

---

## 8. Success Metrics

### 8.1 Technical KPIs

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Fraud Detection Latency** | 24 hours (batch) | <500ms | Databricks metrics |
| **Customer 360° Query Time** | N/A (not available) | <2 seconds | SQL Warehouse |
| **Data Freshness** | 24-48 hours | <1 hour | Pipeline SLAs |
| **Platform Availability** | 99.5% (legacy) | 99.9% | Azure Monitor |
| **Self-Service Adoption** | 20% of users | 80% | User analytics |

### 8.2 Business KPIs

| Metric | Baseline | Target | Impact |
|--------|----------|--------|--------|
| **Fraud Losses** | LKR 150M/year | LKR 60M/year (60% reduction) | Saves 90M/year |
| **CBSL Reporting Time** | 5 days | <24 hours | Regulatory compliance |
| **Time-to-Insight** | 3 weeks | Hours | Business agility |
| **Customer NPS** | 42 | 54 (+12 points) | Customer satisfaction |

---

## 9. Governance & Oversight

### 9.1 Steering Committee

**Members:**
- **Chair**: Chief Operating Officer (COO)
- **Sponsors**: CIO, Chief Risk Officer, CFO
- **Business**: Head of Retail, Head of Cards, Head of Loans
- **Technical**: Chief Data Officer, Head of IT Infrastructure

**Meeting Cadence**: Monthly (or ad-hoc for critical decisions)

**Responsibilities:**
- Approve budget changes >LKR 20M
- Resolve cross-functional conflicts
- Approve Go-Live for each phase
- Escalate to CEO/Board if needed

### 9.2 Decision Rights

| Decision | Authority | Notes |
|----------|-----------|-------|
| **Budget <20M** | Program Manager | Within approved contingency |
| **Budget >20M** | Steering Committee | Requires CFO approval |
| **Scope Changes** | Steering Committee | If >10% impact on timeline/budget |
| **Go-Live Approval** | CIO + Business Sponsor | Per phase |
| **Rollback Decision** | Program Manager | Immediate action, report after |

---

## 10. Alternatives Considered

### 10.1 Option A: Do Nothing

**Pros**: No upfront cost  
**Cons**:
- Fraud losses continue (LKR 150M/year)
- Oracle hardware refresh needed (LKR 200M in Year 2)
- Competitive disadvantage (rivals gain data-driven edge)
- Regulatory risk (slow CBSL response)

**Decision**: ❌ **Rejected** – Not viable long-term

### 10.2 Option B: On-Premises Big Data (Hadoop/Spark)

**Pros**: Data stays 100% on-prem (perceived control)  
**Cons**:
- High capex (LKR 1,200M for hardware + licenses)
- 24-month implementation (longer than cloud)
- Vendor lock-in (e.g., Cloudera)
- No managed services → higher operational burden

**Decision**: ❌ **Rejected** – More expensive, slower, less flexible

### 10.3 Option C: Azure Databricks (Recommended)

**Pros**:
- Lower capex (pay-as-you-go)
- Faster implementation (18 months)
- CMK + ExpressRoute = compliant with CBSL
- Managed services → lower TCO
- Innovation velocity (Databricks R&D)

**Decision**: ✅ **Selected**

---

## 11. Stakeholder Benefits

### 11.1 By Stakeholder Group

| Stakeholder | What They Gain |
|-------------|----------------|
| **Customers** | Faster service, personalized offers, better fraud protection |
| **Retail Banking** | 360° customer view, real-time cross-sell opportunities |
| **Cards Team** | Real-time fraud alerts, reduced chargebacks |
| **Risk & Compliance** | Automated CBSL reporting, PDPA compliance, audit trail |
| **Data Scientists** | ML platform (feature store, model registry), faster experimentation |
| **Business Analysts** | Self-service analytics, no waiting for IT |
| **IT Operations** | Modern platform, reduced maintenance (vs aging Oracle) |
| **Finance** | Cost savings (fraud + efficiency), measurable ROI |

---

## 12. Next Steps

### 12.1 Immediate Actions (Upon Approval)

| Action | Owner | Deadline | Status |
|--------|-------|----------|--------|
| **1. Steering Committee Kickoff** | COO | Week 1 | Pending approval |
| **2. CBSL Submission** | Program Manager | Week 2 | Draft ready |
| **3. Databricks Contract Signature** | Procurement | Week 3 | Negotiation underway |
| **4. ExpressRoute Order** | Network Team | Week 1 | Vendor shortlisted |
| **5. Team Formation** | HR + CIO | Week 4 | JDs approved |
| **6. Implementation Partner RFP** | Procurement | Week 2 | RFP draft ready |

### 12.2 Phase 0 Deliverables (Month 0-2)

- ✅ CBSL approval letter
- ✅ ExpressRoute circuit live
- ✅ Azure prod/QA/dev subscriptions provisioned
- ✅ Databricks workspaces deployed
- ✅ **On-prem data movement components installed**:
  - Azure Data Factory Self-Hosted Integration Runtime (SHIR) on 2 VMs, OR
  - Debezium CDC + on-prem Kafka cluster (if real-time chosen)
- ✅ POC: Extract 1 week of card transactions → validate end-to-end data flow
- ✅ 5 engineers trained (Databricks Associate certification)
- ✅ Dev environment validated (smoke tests passed)

**Go/No-Go for Phase 1**: End of Month 2 (Steering Committee decision)

---

## 13. Appendices (Supporting Documents)

### 13.1 Document Suite

1. **Phase A: Architecture Vision** – Business drivers, stakeholders, scope
2. **Phase C: Data Architecture** – Logical models, Unity Catalog design, governance
3. **Phase D: Technology Architecture** – Azure infra, Databricks platform, security
4. **Phase E & F: Implementation & Migration** – 18-month roadmap, migration strategy
5. **Phase G & H: Governance & Change Mgmt** – Operating model, adoption plan
6. **CBSL Compliance Mapping** – Detailed regulatory alignment
7. **Cost Model** – Detailed TCO calculator (Excel)
8. **Risk Register** – 25+ risks with mitigation plans

### 13.2 Technical Diagrams

1. **High-Level Architecture** – End-to-end data flow
2. **Network Architecture** – ExpressRoute, vNet, private endpoints
3. **Data Model** – Entity-relationship diagrams (Retail, Cards, Loans, Channels)
4. **Migration Roadmap** – Gantt chart (18 months)

---

## 14. Recommendation

**Recommendation to Panel:**

**APPROVE** the Commercial Bank Data Platform Transformation initiative with the following conditions:

1. ✅ **CBSL approval obtained before production deployment** (Phase 1 onwards)
2. ✅ **Phase-gate reviews**: Each phase requires Steering Committee Go-Live approval
3. ✅ **Monthly cost tracking**: Report actuals vs budget to CFO
4. ✅ **Early win validation**: Fraud detection (Phase 1) must demonstrate <500ms latency before proceeding to Phase 2
5. ✅ **Rollback capability**: Maintain legacy systems operational until each domain validated (2-4 weeks parallel run)

**Anticipated Board-Level Questions:**

Q1: **"Can we guarantee CBSL approval?"**  
A: We have engaged a CBSL compliance consultant and will submit a comprehensive architecture dossier. Precedent: Other banks (e.g., Standard Chartered) have received CBSL approval for similar Azure-based platforms.

Q2: **"What if Azure/Databricks has an outage?"**  
A: (1) Azure SLA 99.95% (4 hours downtime/year max), (2) We maintain parallel legacy systems for first 3 months per domain, (3) DR to East Asia region (RTO <2 hours).

Q3: **"Why not on-premises?"**  
A: On-prem Hadoop/Spark would cost LKR 1,200M+ (vs 707M), take 24 months (vs 18), and lack managed services. Azure Databricks with CMK + ExpressRoute gives us cloud benefits with on-prem-like control.

Q4: **"How do we move 600 GB of data from our local data warehouse to Azure? Is ExpressRoute fast enough?"**  
A: Yes, highly practical. 1 Gbps ExpressRoute provides 8.6 TB/day capacity. Our 600 GB initial load completes in ~2 hours (one-time). Daily incremental updates (10-15 GB) transfer in ~2 minutes. Real-time card transactions stream via Kafka with <1 second latency. We migrate domain-by-domain (phased approach), not all at once.

Q5: **"Does our local data warehouse stay operational during migration?"**  
A: Yes. We use Change Data Capture (CDC) or Azure Data Factory Self-Hosted Integration Runtime (SHIR) to extract only changed records from the local DW and push to Azure. The local DW remains the source of truth during migration. For each domain, we run parallel for 2-4 weeks to validate, then cut over. The local DW is decommissioned only after ALL domains are validated (Month 17).

Q7: **"What on-premises infrastructure is needed to move data to Azure?"**  
A: We need lightweight ETL components on-premises: (Option 1) Azure Data Factory Self-Hosted Integration Runtime on 2 VMs - runs scheduled queries to extract changed records and upload to ADLS, OR (Option 2) Debezium CDC with on-prem Kafka (3 nodes) for real-time streaming. Both use ExpressRoute private connectivity. Estimated setup: 2-3 weeks in Phase 0. Cost: LKR 5-8M for hardware/VMs (already included in infrastructure budget).

Q6: **"How do we prevent vendor lock-in?"**  
A: (1) Data stored in open Delta Lake format (Apache open-source), (2) Infrastructure as Code (Terraform) for portability, (3) 3-year contract with exit clause.

---

## 15. Approval Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Program Manager** | [Name] | | |
| **CIO (Sponsor)** | [Name] | | |
| **Chief Risk Officer** | [Name] | | |
| **CFO** | [Name] | | |
| **COO (Steering Committee Chair)** | [Name] | | |
| **CEO** | [Name] | | |

---

## 16. Contact Information

**Program Management Office:**
- **Program Manager**: [Name, Email, Phone]
- **Enterprise Architect**: [Name, Email, Phone]
- **Project Coordinator**: [Name, Email, Phone]

**Steering Committee Secretariat:**
- **Email**: data-platform-steering@combank.lk
- **SharePoint**: [Internal link to project portal]

---

**Document Version**: 1.0  
**Date**: December 2025  
**Classification**: Internal - Board Confidential  
**Next Review**: After Panel Presentation

---

**END OF BUSINESS CASE SUMMARY**
