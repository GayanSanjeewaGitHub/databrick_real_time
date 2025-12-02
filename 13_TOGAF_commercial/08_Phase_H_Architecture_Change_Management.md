# Phase H: Architecture Change Management
## Commercial Bank of Sri Lanka – Data Platform Transformation

**TOGAF ADM Phase H: Architecture Change Management**

---

## Table of Contents

1. [Overview](#1-overview)
2. [Change Management Framework](#2-change-management-framework)
3. [Architecture Monitoring](#3-architecture-monitoring)
4. [Performance Baselines & KPIs](#4-performance-baselines--kpis)
5. [Technology Refresh Cycle](#5-technology-refresh-cycle)
6. [Capacity Planning](#6-capacity-planning)
7. [Architecture Evolution](#7-architecture-evolution)
8. [Incident Management & Root Cause Analysis](#8-incident-management--root-cause-analysis)
9. [BAU Operating Model](#9-bau-operating-model)
10. [Continuous Improvement Programs](#10-continuous-improvement-programs)
11. [Architecture Debt Management](#11-architecture-debt-management)
12. [Innovation & Emerging Technologies](#12-innovation--emerging-technologies)

---

## 1. Overview

### 1.1 Purpose

Phase H (Architecture Change Management) ensures that:
- The data platform architecture continues to meet evolving business needs
- Changes are managed in a controlled manner
- Platform performance is monitored and optimized
- The architecture remains aligned with technology trends
- Technical debt is managed and minimized

### 1.2 Change Management Lifecycle

```
┌────────────────────────────────────────────────────────────┐
│           ARCHITECTURE CHANGE MANAGEMENT CYCLE             │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Business Need → Assess → Plan → Approve → Implement →    │
│  Monitor → Review → Next Iteration                         │
│                                                            │
│  ┌─────────────────────────────────────────────────┐      │
│  │  FEEDBACK LOOPS                                 │      │
│  ├─────────────────────────────────────────────────┤      │
│  │  • Quarterly Architecture Reviews               │      │
│  │  • Annual Health Checks                         │      │
│  │  • Incident Post-Mortems                        │      │
│  │  • User Feedback                                │      │
│  │  • Technology Trend Analysis                    │      │
│  └─────────────────────────────────────────────────┘      │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 1.3 Objectives

| Objective | Success Criteria |
|-----------|------------------|
| **Platform Stability** | >99.9% availability, <5 Sev 1 incidents/year |
| **Performance** | Fraud detection <500ms, Customer 360° <2s (P95) |
| **Cost Efficiency** | Cloud cost <LKR 22M/month, <5% monthly variance |
| **User Satisfaction** | >85% satisfaction score (quarterly survey) |
| **Architecture Currency** | 100% of tech stack within vendor support lifecycle |
| **Innovation Adoption** | Evaluate 2+ emerging technologies/year, adopt 1 if ROI positive |

---

## 2. Change Management Framework

### 2.1 Change Categories

| Change Type | Definition | Examples | Approval Authority | Typical Frequency |
|-------------|------------|----------|-------------------|-------------------|
| **Minor Change** | No architecture impact, low risk | Add new dashboard, adjust DLT expectation | Platform Owner | Weekly |
| **Standard Change** | Pre-approved, repeatable, low risk | Scale cluster, add new user to Unity Catalog | Data Engineer | Daily |
| **Normal Change** | Architecture change, medium risk | New data pipeline, schema change, new domain | ARB + Platform Owner | Monthly |
| **Major Change** | Significant architecture change, high risk/cost | New technology (e.g., replace Kafka with Confluent Cloud), new region | ARB + Steering Committee | Quarterly |
| **Emergency Change** | Urgent fix for Sev 1 incident | Hotfix for data corruption, security patch | Platform Owner (post-review by ARB) | Ad-hoc |

### 2.2 Change Request Process (BAU)

```
┌────────────────────────────────────────────────────────┐
│  BAU CHANGE REQUEST FLOW                               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Requester submits CR in JIRA (with business case) │
│       ↓                                                │
│  2. Platform Owner reviews & categorizes               │
│       ↓                                                │
│  3a. Minor/Standard → Approve & schedule               │
│  3b. Normal → ARB Review (weekly meeting)              │
│  3c. Major → ARB + Steering Committee                  │
│       ↓                                                │
│  4. Impact assessment:                                 │
│      - Architecture alignment                          │
│      - Security/compliance implications                │
│      - Cost (capex/opex)                               │
│      - Dependencies                                    │
│      - Rollback plan                                   │
│       ↓                                                │
│  5. Approval decision:                                 │
│      ├─→ Approved: Add to backlog, prioritize          │
│      ├─→ Conditional: Request more info, reassess      │
│      ├─→ Rejected: Notify requester with rationale     │
│      └─→ Deferred: Add to roadmap for future           │
│       ↓                                                │
│  6. Implementation (following quality gates)           │
│       ↓                                                │
│  7. Post-Implementation Review (within 2 weeks)        │
│       ↓                                                │
│  8. Close CR, update architecture artifacts            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 2.3 Change Calendar

**Planned Change Windows:**
- **Standard Maintenance**: Every Saturday 22:00-02:00 (4 hours) for routine updates
- **Major Upgrades**: Quarterly (weekend), pre-announced 4 weeks in advance
- **Emergency Maintenance**: 24/7 on-call team available, <1 hour response time

**Blackout Periods** (no non-emergency changes):
- Month-end close (last 3 days of month + first 2 days of new month)
- CBSL reporting windows (first week of each quarter)
- Major business events (e.g., bank holidays with high transaction volume)

---

## 3. Architecture Monitoring

### 3.1 Monitoring Layers

```
┌─────────────────────────────────────────────────────────┐
│  MONITORING ARCHITECTURE                                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌───────────────────────────────────────────────┐     │
│  │  Layer 1: Infrastructure (Azure Monitor)      │     │
│  │  - ADLS metrics (latency, IOPS, capacity)     │     │
│  │  - ExpressRoute (bandwidth, latency, errors)  │     │
│  │  - Key Vault (availability, request rate)     │     │
│  └───────────────────────────────────────────────┘     │
│                     ↓                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │  Layer 2: Platform (Databricks)               │     │
│  │  - Cluster metrics (CPU, memory, disk)        │     │
│  │  - Job run times, success/failure rates       │     │
│  │  - SQL Warehouse query latency (P50/P95/P99)  │     │
│  └───────────────────────────────────────────────┘     │
│                     ↓                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │  Layer 3: Data (Unity Catalog + DLT)          │     │
│  │  - Data freshness (last update timestamp)     │     │
│  │  - Data quality (DLT expectation violations)  │     │
│  │  - Lineage tracking (upstream/downstream)     │     │
│  └───────────────────────────────────────────────┘     │
│                     ↓                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │  Layer 4: Business (Application KPIs)         │     │
│  │  - Fraud detection latency                    │     │
│  │  - Customer 360° query response time          │     │
│  │  - Self-service adoption rate                 │     │
│  └───────────────────────────────────────────────┘     │
│                     ↓                                   │
│  ┌───────────────────────────────────────────────┐     │
│  │  Layer 5: Security & Compliance (Sentinel)    │     │
│  │  - Failed login attempts (anomaly detection)  │     │
│  │  - Data access patterns (unusual queries)     │     │
│  │  - CMK unavailability alerts                  │     │
│  └───────────────────────────────────────────────┘     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Monitoring Metrics & Thresholds

#### 3.2.1 Infrastructure Metrics

| Metric | Target | Warning Threshold | Critical Threshold | Alert Action |
|--------|--------|-------------------|-------------------|--------------|
| **ADLS Latency (P95)** | <100ms | >150ms | >300ms | Investigate storage throttling, consider scaling |
| **ExpressRoute Bandwidth** | <70% utilized | >70% | >85% | Plan bandwidth upgrade |
| **ExpressRoute Packet Loss** | 0% | >0.1% | >0.5% | Engage Dialog/SLT support |
| **Key Vault Availability** | 100% | <99.9% | <99.5% | Escalate to Azure support, check CMK backup |

#### 3.2.2 Platform Metrics (Databricks)

| Metric | Target | Warning Threshold | Critical Threshold | Alert Action |
|--------|--------|-------------------|-------------------|--------------|
| **DLT Pipeline Success Rate** | >99% | <99% | <95% | Review failed pipelines, check source system connectivity |
| **Streaming Job Lag** | <5 mins | >5 mins | >15 mins | Scale cluster, check Kafka throughput |
| **SQL Warehouse Query Latency (P95)** | <2s | >2s | >5s | Optimize queries, scale warehouse |
| **Cluster CPU Utilization** | 50-70% | >80% | >95% | Autoscale or right-size cluster |
| **Job Run Time Anomaly** | Baseline ±20% | >30% variance | >50% variance | Investigate data volume spikes, code regression |

#### 3.2.3 Data Quality Metrics

| Metric | Target | Warning Threshold | Critical Threshold | Alert Action |
|--------|--------|-------------------|-------------------|--------------|
| **DLT Expectation Violations** | <0.1% | >0.1% | >1% | Review source data quality, adjust expectations |
| **Data Freshness (Retail)** | <1 hour | >1 hour | >4 hours | Check CDC replication, investigate source system lag |
| **Data Freshness (Cards - Streaming)** | <1 min | >1 min | >5 mins | Check Kafka connectivity, review streaming job |
| **Schema Drift Detected** | 0 | >0 | >0 | Coordinate with source system team, update schema |

#### 3.2.4 Business KPIs

| KPI | Target | Warning Threshold | Critical Threshold | Alert Action |
|-----|--------|-------------------|-------------------|--------------|
| **Fraud Detection Latency** | <500ms | >500ms | >1s | Review Kafka-to-Databricks latency, optimize ML model |
| **Customer 360° Query Time** | <2s | >2s | >5s | Optimize SQL, consider result caching |
| **Self-Service Adoption** | >80% | <80% | <70% | Launch user re-engagement campaign, additional training |
| **Platform Availability** | >99.9% | <99.9% | <99.5% | RCA on downtime, implement redundancy improvements |

### 3.3 Monitoring Dashboards

**1. Real-Time Operations Dashboard** (Databricks SQL, 5-min refresh)
- **Audience**: Platform Operations Team (24/7 monitoring)
- **Metrics**:
  - Streaming job health (lag, throughput, error rate)
  - Active cluster count & resource utilization
  - Recent failures (last 1 hour)
  - Fraud detection latency (real-time chart)

**2. Daily Platform Health Dashboard** (Power BI)
- **Audience**: Platform Owner, Data Engineering Team
- **Metrics**:
  - Yesterday's pipeline success rate
  - Data freshness by domain
  - Cost (yesterday vs. 7-day avg)
  - DLT expectation violations

**3. Weekly Architecture Dashboard** (Power BI)
- **Audience**: Chief Architect, ARB
- **Metrics**:
  - Architecture compliance score
  - Change request backlog & aging
  - Security exceptions raised
  - Technical debt inventory

**4. Monthly Executive Dashboard** (Power BI)
- **Audience**: Steering Committee, CIO
- **Metrics**:
  - Business KPIs (fraud losses, NPS, self-service adoption)
  - Cost vs. budget
  - Availability & incident trend
  - Benefits realization progress

### 3.4 Alerting Strategy

**Alert Routing:**
- **Critical (Sev 1)**: Page on-call engineer (24/7) + notify Platform Owner
- **High (Sev 2)**: Email + SMS to on-call engineer (8am-8pm) + email to Platform Owner
- **Medium (Sev 3)**: Email to team distribution list
- **Low (Sev 4)**: Logged in monitoring system (no active alert)

**Alert Fatigue Prevention:**
- De-duplicate alerts (same issue within 1 hour → single alert)
- Suppress during known maintenance windows
- Tune thresholds based on historical baseline (quarterly review)
- Implement auto-remediation for common issues (e.g., auto-restart failed job)

---

## 4. Performance Baselines & KPIs

### 4.1 Baseline Establishment

**Baseline Period**: First 3 months post-Go-Live (per domain)

**Baseline Metrics Collection:**
- **Infrastructure**: ADLS latency, ExpressRoute bandwidth, cluster resource utilization
- **Platform**: Job run times, query latency (P50/P95/P99), pipeline throughput
- **Data**: Row counts, data volume (GB), data growth rate
- **Business**: Fraud detection latency, customer 360° query time, user query count

**Baseline Review**: Quarterly (first year), then annually

**Example Baseline (Phase 1 - Cards, Month 6-9):**

| Metric | Baseline (3-month avg) | Variance (±) |
|--------|------------------------|--------------|
| **Fraud Detection Latency (P95)** | 420ms | ±50ms |
| **Card Authorization Volume** | 800K/day | ±100K |
| **Streaming Job Throughput** | 12K events/sec | ±2K |
| **ADLS Storage Growth** | 5 GB/day | ±1 GB |
| **SQL Warehouse Concurrent Users** | 25 | ±5 |

### 4.2 Performance Degradation Detection

**Anomaly Detection (using Databricks System Tables + Azure Monitor):**
- **Static Thresholds**: E.g., fraud latency >500ms → alert
- **Dynamic Thresholds**: E.g., job run time >30% longer than 30-day moving average → alert
- **ML-Based Anomaly Detection**: Azure Sentinel machine learning detects unusual access patterns

**Performance Degradation Response:**
1. **Detect**: Automated alert triggered
2. **Triage**: On-call engineer investigates (target: <15 mins)
3. **Diagnose**: Review metrics, logs, recent changes
4. **Remediate**: Apply fix (scale cluster, optimize query, restart job)
5. **Validate**: Confirm metrics return to baseline
6. **Root Cause Analysis**: If Sev 1/2, conduct RCA within 48 hours

### 4.3 Performance Optimization Cycle

**Quarterly Performance Review (Led by Chief Architect):**
- Review all KPIs vs. baseline
- Identify degradation trends (e.g., query latency creeping up)
- Prioritize optimization opportunities (cost/benefit analysis)
- Plan optimization sprints (2-week focused effort)

**Optimization Techniques:**
- **Data**: Z-ordering, partitioning strategy, data compaction
- **Compute**: Right-size clusters, use Photon, adjust autoscaling
- **Code**: Query optimization (avoid full scans), vectorized UDFs
- **Architecture**: Introduce caching (e.g., Databricks Delta Cache), materialize views

---

## 5. Technology Refresh Cycle

### 5.1 Technology Lifecycle Management

**Technology Inventory (Maintain in Confluence):**

| Technology | Current Version | Vendor Support End Date | Refresh Cycle | Upgrade Path |
|------------|-----------------|-------------------------|---------------|--------------|
| **Azure Databricks** | Premium (Databricks Runtime 13.3 LTS) | June 2025 | Upgrade to 14.x LTS (Q4 2025) | In-place upgrade (blue/green) |
| **Delta Lake** | 2.4 (bundled with Runtime) | Same as Runtime | Upgrade with Runtime | Automatic |
| **Unity Catalog** | Managed (always latest) | N/A (SaaS) | N/A | Auto-updated by Databricks |
| **Azure ADLS Gen2** | Managed (always latest) | N/A (PaaS) | N/A | Auto-updated by Azure |
| **Azure Key Vault** | Managed (always latest) | N/A (PaaS) | N/A | Auto-updated by Azure |
| **ExpressRoute** | 1 Gbps circuit | N/A (circuit contract 3 years) | Review capacity annually | Upgrade to 2 Gbps if >70% utilized |
| **Power BI** | Pro licenses | N/A (SaaS) | N/A | Auto-updated by Microsoft |
| **Azure DevOps** | Managed (always latest) | N/A (SaaS) | N/A | Auto-updated by Microsoft |

### 5.2 Upgrade Planning

**Databricks Runtime Upgrades (Major LTS Releases):**

**Timeline:**
- **T-12 weeks**: New LTS released, review release notes
- **T-10 weeks**: Test in Dev environment (smoke tests, compatibility checks)
- **T-8 weeks**: Migrate Dev workloads to new Runtime, identify issues
- **T-6 weeks**: Test in QA environment (full regression testing)
- **T-4 weeks**: Communicate upgrade plan to stakeholders
- **T-2 weeks**: Deploy to Prod (blue/green deployment: new cluster with new Runtime, gradual traffic shift)
- **T-0**: 100% traffic on new Runtime, retire old cluster
- **T+2 weeks**: Post-upgrade review, document lessons learned

**Upgrade Risks & Mitigation:**
- **Risk**: Breaking changes in Spark APIs
  - **Mitigation**: Review Spark release notes, test in Dev/QA
- **Risk**: Performance regression
  - **Mitigation**: Benchmark before/after, compare metrics
- **Risk**: Data pipeline failures
  - **Mitigation**: Blue/green deployment (parallel run old/new for 1 week)

### 5.3 End-of-Life (EOL) Management

**Process for Technology Reaching EOL:**
1. **T-6 months**: ARB notified of impending EOL
2. **T-5 months**: Evaluate replacement options (same vendor upgrade, alternative tech)
3. **T-4 months**: Business case for upgrade/replacement (cost, effort, risk)
4. **T-3 months**: Steering Committee approval for budget
5. **T-2 months**: Upgrade/migration planning
6. **T-1 month**: Testing in Dev/QA
7. **T-0**: Upgrade/migrate before EOL date

**Example:**
- **Databricks Runtime 13.3 LTS EOL: June 2025**
- **Action**: Upgrade to Runtime 14.x LTS (planned for May 2025)

---

## 6. Capacity Planning

### 6.1 Capacity Planning Cycle

**Frequency**: Quarterly (review), Annually (long-term planning)

**Capacity Metrics:**
- **Storage (ADLS)**: Current usage, growth rate, forecast (12 months)
- **Compute (Databricks)**: DBU consumption trend, cluster utilization, forecast
- **Network (ExpressRoute)**: Bandwidth utilization, peak hours, forecast
- **Unity Catalog**: Table count, metadata size (for scaling considerations)

### 6.2 Storage Capacity Planning

**Current State (Example - Month 12):**
- **Total ADLS Storage**: 1.2 TB
- **Growth Rate**: 10 GB/day (~300 GB/month)
- **Forecast (12 months)**: 1.2 TB + (300 GB × 12) = ~4.8 TB

**Capacity Actions:**
- Implement lifecycle policies: Move >90-day-old raw data to cool tier (cost optimization)
- Archive >2-year-old data to cold tier
- Monitor for anomalies (e.g., sudden 10× growth → investigate)

**Capacity Thresholds:**
- **Warning (70% of allocated)**: Review growth rate, adjust forecast
- **Critical (85%)**: Request additional storage capacity, accelerate data archival

### 6.3 Compute Capacity Planning

**DBU Consumption Trend:**
- **Current (Month 12)**: 15K DBUs/month (~LKR 5M)
- **Growth Drivers**: +10% monthly (new users, more data, new pipelines)
- **Forecast (Month 24)**: 15K × (1.1)^12 = ~47K DBUs/month (~LKR 15.5M)

**Capacity Actions:**
- Right-size clusters: Review cluster policies quarterly, adjust autoscaling limits
- Use Serverless SQL Warehouses (pay-per-query) for ad-hoc analytics
- Leverage Photon (faster execution = less DBU consumption)
- Consider Databricks Reserved Capacity (discount for committed usage)

### 6.4 Network Capacity Planning

**ExpressRoute Bandwidth Utilization:**
- **Current**: 1 Gbps circuit, 50% avg utilization (peak 70%)
- **Growth**: +15% quarterly due to new domains, more real-time streaming
- **Forecast**: Will exceed 70% by Month 15 (Phase 3 complete)

**Capacity Actions:**
- **T-6 months before 70% threshold**: Initiate upgrade to 2 Gbps circuit (lead time: 8-12 weeks)
- **Interim**: Implement data compression, schedule large batch loads during off-peak hours

---

## 7. Architecture Evolution

### 7.1 Architecture Review Schedule

| Review Type | Frequency | Participants | Duration | Output |
|-------------|-----------|--------------|----------|--------|
| **Quarterly Architecture Review** | Every 3 months | ARB, Platform Owner, Tech Leads | 2 hours | Architecture health report, improvement roadmap |
| **Annual Architecture Health Check** | Yearly | ARB, Steering Committee, external consultant (optional) | 1 day | Comprehensive architecture assessment, 3-year roadmap |
| **Technology Trend Review** | Semi-annual | ARB, Chief Architect | 4 hours | Emerging tech assessment, POC recommendations |
| **Post-Incident Architecture Review** | After Sev 1 incidents | ARB, Platform Owner, incident responders | 2 hours | Architecture changes to prevent recurrence |

### 7.2 Architecture Evolution Triggers

**Triggers for Architecture Change:**
1. **Business-Driven**:
   - New business requirements (e.g., launch new digital product requiring real-time ML)
   - Regulatory changes (e.g., new CBSL data localization rules)
   - M&A activity (acquire another bank → integrate data)

2. **Technology-Driven**:
   - Technology EOL (e.g., Databricks Runtime upgrade)
   - Performance degradation (e.g., query latency >5s despite optimization)
   - Cost optimization (e.g., new Azure region with 20% lower pricing)

3. **Risk-Driven**:
   - Security vulnerability (e.g., CVE discovered in component)
   - Compliance violation (e.g., CBSL audit finding)
   - Vendor risk (e.g., Azure service deprecated)

4. **Innovation-Driven**:
   - Emerging technology with clear ROI (e.g., Databricks Lakehouse AI for GenAI)
   - Competitor adoption (e.g., rival bank launches AI-powered fraud detection)

### 7.3 Architecture Evolution Process

```
┌────────────────────────────────────────────────────────┐
│  ARCHITECTURE EVOLUTION PROCESS                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. Trigger identified (business, tech, risk, etc.)   │
│       ↓                                                │
│  2. ARB evaluates trigger (impact, urgency)            │
│       ↓                                                │
│  3. Feasibility study (2-4 weeks):                     │
│      - Technical feasibility                           │
│      - Cost-benefit analysis                           │
│      - Risk assessment                                 │
│      - POC (if needed)                                 │
│       ↓                                                │
│  4. ARB + Steering Committee review & approve          │
│       ↓                                                │
│  5. Architecture design (update ADRs, diagrams)        │
│       ↓                                                │
│  6. Implementation plan (work packages, timeline)      │
│       ↓                                                │
│  7. Implementation (following Phase G governance)      │
│       ↓                                                │
│  8. Post-implementation review                         │
│       ↓                                                │
│  9. Update architecture repository (Confluence, Git)   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 7.4 Architecture Roadmap (3-Year Vision)

**Year 1 (Months 1-12): Stabilization**
- Complete Phases 1-4 (all domains operational)
- Achieve performance targets (fraud <500ms, availability >99.9%)
- Establish BAU operations
- Pay down initial technical debt

**Year 2 (Months 13-24): Optimization**
- **Q1**: Self-service adoption push (target 80%)
- **Q2**: Advanced analytics (churn prediction, next-best-offer ML models)
- **Q3**: Cost optimization (reserved capacity, lifecycle policies)
- **Q4**: Multi-cloud DR (Azure GRS to East Asia region)

**Year 3 (Months 25-36): Innovation**
- **Q1**: Databricks Lakehouse AI (GenAI for customer service chatbot)
- **Q2**: Real-time customer segmentation (streaming ML)
- **Q3**: Open banking API integration (share data with fintech partners)
- **Q4**: Explore quantum-safe encryption (post-quantum cryptography POC)

---

## 8. Incident Management & Root Cause Analysis

### 8.1 Incident Severity Levels

| Severity | Definition | Response Time | Resolution Target | Examples |
|----------|------------|---------------|-------------------|----------|
| **Sev 1 (Critical)** | Production outage, data breach, CBSL violation | <15 mins | <4 hours | Data corruption, CMK unavailable, ExpressRoute down |
| **Sev 2 (High)** | Major feature degraded, significant user impact | <1 hour | <24 hours | Fraud detection latency >2s, SQL Warehouse down |
| **Sev 3 (Medium)** | Minor feature degraded, workaround available | <4 hours | <5 days | Single pipeline failing, non-critical data stale |
| **Sev 4 (Low)** | Cosmetic issue, no functional impact | <24 hours | <2 weeks | Dashboard display issue, non-urgent report missing |

### 8.2 Incident Response Process

```
┌────────────────────────────────────────────────────────┐
│  INCIDENT RESPONSE LIFECYCLE                           │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. DETECT: Monitoring alert or user report           │
│       ↓                                                │
│  2. TRIAGE: On-call engineer assesses severity        │
│       ↓                                                │
│  3. ESCALATE: Page additional responders if Sev 1/2   │
│       ↓                                                │
│  4. DIAGNOSE: Investigate logs, metrics, recent changes│
│       ↓                                                │
│  5. COMMUNICATE: Update status page, notify stakeholders│
│       ↓                                                │
│  6. RESOLVE: Apply fix (may be temporary workaround)  │
│       ↓                                                │
│  7. VALIDATE: Confirm metrics return to normal        │
│       ↓                                                │
│  8. CLOSE: Update incident ticket, notify users       │
│       ↓                                                │
│  9. POST-MORTEM: Conduct RCA (Sev 1/2 mandatory)      │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 8.3 Root Cause Analysis (RCA) Framework

**RCA Timeline:**
- **Sev 1**: RCA completed within 48 hours of incident resolution
- **Sev 2**: RCA completed within 5 business days
- **Sev 3/4**: RCA optional (only if recurring issue)

**RCA Template:**

```markdown
# Incident Post-Mortem: [Title]

**Incident ID**: INC-YYYYMMDD-###
**Severity**: Sev 1 / Sev 2 / Sev 3 / Sev 4
**Date**: YYYY-MM-DD HH:MM to HH:MM (duration: X hours)
**Status**: Resolved / Monitoring

## Executive Summary
[1-paragraph summary: what happened, impact, root cause, fix]

## Impact
- **Users Affected**: [Number of users, business units]
- **Business Impact**: [e.g., Fraud detection delayed 30 mins, LKR 2M potential fraud undetected]
- **Data Impact**: [e.g., 50K transactions not processed, no data loss]
- **Duration**: [Total downtime/degradation]

## Timeline (All times in IST)
- **HH:MM**: Incident detected (alert fired / user reported)
- **HH:MM**: On-call engineer paged, investigation started
- **HH:MM**: Root cause identified (CMK Key Vault unavailable)
- **HH:MM**: Mitigation applied (switched to backup Key Vault)
- **HH:MM**: Service restored, metrics normal
- **HH:MM**: Incident closed

## Root Cause Analysis
**Symptom**: [What users experienced]
**Immediate Cause**: [Proximate cause, e.g., Key Vault timeout]
**Root Cause**: [Underlying cause, using 5 Whys]

**5 Whys Example**:
1. Why did Databricks fail to read ADLS? → CMK Key Vault unavailable
2. Why was Key Vault unavailable? → Azure region outage (Southeast Asia)
3. Why did outage affect us? → No geo-redundant Key Vault backup
4. Why no backup? → Not in initial architecture (cost trade-off)
5. Root Cause: **Single point of failure in Key Vault design**

## Corrective Actions (Short-Term)
- [Action 1]: Switch to backup Key Vault (completed HH:MM)
- [Action 2]: Validate all ADLS access restored (completed HH:MM)

## Preventive Actions (Long-Term)
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| Deploy geo-redundant Key Vault (East Asia region) | DevOps Lead | 2025-02-15 | In Progress |
| Update architecture to use Key Vault failover (automatic) | Chief Architect | 2025-02-28 | Planned |
| Add Key Vault availability monitoring (alert if <99.9%) | Platform Owner | 2025-01-30 | Completed |
| DR test to validate Key Vault failover | DevOps Lead | 2025-03-15 | Planned |

## Lessons Learned
- **What Went Well**: Incident detected within 5 mins (automated alert)
- **What Didn't Go Well**: Took 45 mins to identify root cause (first suspected ADLS, then Key Vault)
- **Action**: Update runbook with Key Vault troubleshooting checklist

## Architecture Changes
- **ADR-### (New)**: Geo-Redundant Key Vault for High Availability
- **Impact**: +LKR 500K/year for second Key Vault, but eliminates SPOF

## Approval
- **Platform Owner**: [Name, Signature, Date]
- **Chief Architect (ARB Chair)**: [Name, Signature, Date]
- **Chief Risk Officer** (if Sev 1): [Name, Signature, Date]
```

### 8.4 Incident Review Meeting (Sev 1/2)

**Participants**: ARB, Platform Owner, incident responders, stakeholders

**Agenda (1 hour)**:
1. **Incident walkthrough** (10 mins): Timeline, impact
2. **Root cause** (15 mins): 5 Whys, contributing factors
3. **Corrective actions review** (15 mins): What was done to restore service
4. **Preventive actions** (15 mins): Long-term fixes to prevent recurrence
5. **Action item assignment** (5 mins): Owners, due dates

**No Blame Culture**: Focus on process/system failures, not individuals

---

## 9. BAU Operating Model

### 9.1 BAU Team Structure

```
┌─────────────────────────────────────────────────────────┐
│                  BAU ORGANIZATION                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│              Platform Owner (1 FTE)                     │
│              (Strategic direction)                      │
│                       ↓                                 │
│         ┌─────────────┴─────────────┐                  │
│         │                           │                  │
│  Platform Manager (1 FTE)    Governance Lead (1 FTE)   │
│  (Day-to-day operations)     (Compliance, audit)       │
│         ↓                           ↓                  │
│  ┌──────┴───────┐            Data Stewards (domain)    │
│  │              │                                      │
│  Data Engineers  DevOps/SRE                            │
│  (3 FTEs)        (1 FTE)                               │
│  ↓               ↓                                     │
│  L1 Support (2 FTEs, outsourced)                       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Total BAU Team**: 7 FTEs + 2 outsourced L1 support

### 9.2 BAU Roles & Responsibilities

| Role | Responsibilities | Key Activities |
|------|------------------|----------------|
| **Platform Owner** | Strategic direction, budget, stakeholder management | Quarterly architecture reviews, technology roadmap, vendor management |
| **Platform Manager** | Day-to-day operations, incident management, team management | Daily stand-ups, sprint planning, incident response |
| **Data Engineers (3)** | Pipeline development, data quality, performance optimization | Develop new pipelines, troubleshoot failures, optimize queries |
| **DevOps/SRE (1)** | Infrastructure management, CI/CD, monitoring | Cluster management, Azure resource provisioning, cost optimization |
| **Governance Lead (1)** | Compliance monitoring, audit support, policy enforcement | Unity Catalog audits, CBSL reporting, PDPA compliance checks |
| **Data Stewards (domain-based)** | Data quality, metadata management, user support | Business glossary, data quality rules, user training |
| **L1 Support (2, outsourced)** | User helpdesk, ticket triage | Answer user questions, triage incidents to L2 (Data Engineers) |

### 9.3 BAU RACI (Day-to-Day Activities)

| Activity | Platform Owner | Platform Manager | Data Engineers | DevOps/SRE | Governance Lead | L1 Support |
|----------|---------------|------------------|----------------|------------|-----------------|------------|
| **New Pipeline Development** | I | A | R | C | I | I |
| **Incident Response** | I | A | R | R | C | R (L1 triage) |
| **Cluster Scaling** | I | C | C | A | I | I |
| **User Onboarding** | I | C | C | I | R | R (initial request) |
| **Compliance Audit** | I | C | C | C | A | I |
| **Cost Optimization** | A | R | C | R | I | I |
| **Quarterly Architecture Review** | A | R | C | C | R | I |

### 9.4 BAU Operating Rhythm

**Daily:**
- 09:00: Team stand-up (15 mins) - Platform Manager leads
- Continuous: Monitoring, incident response, pipeline troubleshooting

**Weekly:**
- Monday 10:00: Sprint planning (1 hour) - review backlog, prioritize
- Friday 15:00: Sprint retrospective (30 mins) - what went well, improvements

**Monthly:**
- First Monday: Platform Health Review (1 hour) - review metrics, cost, incidents
- Third Thursday: Architecture Review Board (1 hour) - review change requests, ADRs

**Quarterly:**
- Architecture Review (2 hours) - evaluate architecture health, plan improvements
- Business Review (1 hour) - benefits realization, stakeholder satisfaction
- Capacity Planning (1 hour) - forecast storage, compute, network needs

**Annually:**
- Architecture Health Check (1 day) - comprehensive assessment
- CBSL Compliance Attestation - submit annual report
- DR Test - validate failover/failback procedures
- Team Planning - goals, training, succession planning

---

## 10. Continuous Improvement Programs

### 10.1 Innovation Pipeline

**Process for Evaluating Emerging Technologies:**

```
┌────────────────────────────────────────────────────────┐
│  INNOVATION EVALUATION PIPELINE                        │
├────────────────────────────────────────────────────────┤
│                                                        │
│  1. DISCOVER: Technology trend monitoring             │
│      - Databricks product roadmap                     │
│      - Azure announcements                            │
│      - Industry conferences (e.g., Data + AI Summit)  │
│       ↓                                                │
│  2. ASSESS: Initial evaluation (2 weeks)              │
│      - Business value potential                       │
│      - Technical feasibility                          │
│      - Cost (licensing, implementation)               │
│       ↓                                                │
│  3. POC: Proof-of-Concept (4 weeks)                   │
│      - Deploy in sandbox environment                  │
│      - Test with real use case                        │
│      - Measure performance, cost, complexity          │
│       ↓                                                │
│  4. BUSINESS CASE: ROI analysis                       │
│      - Quantify benefits (cost savings, revenue)      │
│      - Estimate total cost (licenses, training, ops)  │
│      - Risk assessment                                │
│       ↓                                                │
│  5. DECISION: ARB + Steering Committee                │
│      ├─→ Approve: Add to roadmap, plan rollout        │
│      ├─→ Defer: Park for future re-evaluation         │
│      └─→ Reject: Document rationale                   │
│       ↓                                                │
│  6. ROLLOUT: Phased deployment (if approved)          │
│      - Dev → QA → Prod                                │
│      - Training, documentation                        │
│       ↓                                                │
│  7. MEASURE: Track adoption, benefits realized        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### 10.2 Innovation Candidates (2025-2027)

| Technology | Description | Potential Value | POC Timeline | Status |
|------------|-------------|-----------------|--------------|--------|
| **Databricks Lakehouse AI** | GenAI integration (chatbot on bank data) | Customer service automation (30% cost reduction) | Q2 2026 | Planned |
| **Databricks Lakehouse Federation** | Query external data (e.g., Snowflake, PostgreSQL) without ETL | Eliminate data duplication, faster integration | Q3 2025 | Under Evaluation |
| **Delta Sharing** | Secure data sharing with external partners (fintechs) | Enable open banking ecosystem | Q1 2026 | Planned |
| **Databricks Serverless** | Serverless job clusters (no cluster management) | Reduce ops overhead, faster job startup | Q4 2025 | POC in Progress |
| **Azure Confidential Computing** | TEE (Trusted Execution Environment) for sensitive data processing | Enhanced security for PII, regulatory compliance | Q2 2027 | Watch List |
| **Quantum-Safe Encryption** | Post-quantum cryptography (PQC) | Future-proof against quantum computers | Q4 2027 | Watch List |

### 10.3 User Feedback Loop

**Feedback Collection Channels:**
- **Quarterly User Satisfaction Survey** (all users, 10 questions, <5 mins)
- **Monthly Power User Forum** (top 20 users, 1-hour discussion)
- **Helpdesk Ticket Analysis** (categorize common issues, identify pain points)
- **Usage Analytics** (Databricks system tables: which features used, query patterns)

**Feedback Categories:**
1. **Usability**: Platform too complex, need more training
2. **Performance**: Query too slow, dashboard timeout
3. **Features**: Missing capability (e.g., "I want to export data to Excel")
4. **Data Quality**: Data inaccurate, stale, missing
5. **Support**: Helpdesk response slow, need better documentation

**Feedback-to-Action Process:**
- **High-impact issues** (affects >50% of users): Prioritize for next sprint
- **Medium-impact**: Add to backlog, address within quarter
- **Low-impact**: Defer or reject (with rationale)

**Feedback Metrics:**
- **User Satisfaction Score (CSAT)**: Target >85%, measured quarterly
- **Net Promoter Score (NPS)**: Target >50, measured semi-annually

---

## 11. Architecture Debt Management

### 11.1 Technical Debt Definition

**Technical Debt**: Shortcuts, workarounds, or suboptimal designs accumulated during implementation (often due to time/budget pressure).

**Examples:**
- **Code Debt**: Hardcoded values instead of config, no unit tests
- **Data Debt**: Non-standard schema (violates naming conventions), no partitioning
- **Infrastructure Debt**: Manual deployment steps (not IaC), no DR setup
- **Documentation Debt**: Missing runbooks, outdated architecture diagrams

### 11.2 Technical Debt Inventory

**Debt Register (Tracked in JIRA with "Tech-Debt" label):**

| ID | Debt Item | Category | Impact | Effort | Priority | Owner | Target Quarter |
|----|-----------|----------|--------|--------|----------|-------|----------------|
| TD-001 | No unit tests for data quality functions | Code | Medium (harder to refactor) | 5 days | Medium | Data Engineer 1 | Q2 2025 |
| TD-002 | Manual Terraform deployment (not CI/CD) | Infrastructure | High (error-prone) | 3 days | High | DevOps | Q1 2025 |
| TD-003 | `transactions` table not Z-ordered | Data | High (slow queries) | 2 days | High | Data Engineer 2 | Q1 2025 |
| TD-004 | Fraud detection ML model not automated (manual retraining) | Code | Medium | 10 days | Medium | Data Scientist | Q3 2025 |
| TD-005 | No DR test plan documented | Documentation | High (compliance risk) | 2 days | High | DevOps | Q1 2025 |

**Debt Metrics:**
- **Total Debt Items**: X
- **High Priority Debt**: Y (target: <5 at any time)
- **Debt Age** (how long debt items remain open): Avg Z weeks (target: <8 weeks)

### 11.3 Debt Paydown Strategy

**Allocation of Capacity:**
- **70% Feature Development**: New capabilities, business requirements
- **20% Technical Debt Paydown**: Each sprint, allocate time to reduce debt
- **10% Innovation/Learning**: Experiment with new tech, training

**Debt Prioritization (using Impact vs. Effort matrix):**

```
     High Impact
          │
   ┌──────┼──────┐
   │ HIGH │ MED  │ High Effort
───┼──────┼──────┼───
   │ HIGH │ LOW  │ Low Effort
   └──────┼──────┘
          │
     Low Impact
```

- **High Impact + Low Effort**: Do immediately (Quick Wins)
- **High Impact + High Effort**: Plan for next quarter (Strategic)
- **Low Impact + Low Effort**: Do when time available (Opportunistic)
- **Low Impact + High Effort**: Reject or defer indefinitely (Not Worth It)

---

## 12. Innovation & Emerging Technologies

### 12.1 Technology Radar (Gartner-Inspired)

**Quadrants:**
1. **Adopt**: Proven, ready for production use
2. **Trial**: Worth investing in POC
3. **Assess**: Monitor, evaluate potential
4. **Hold**: Not recommended

**Current Technology Radar (2025):**

| Technology | Quadrant | Rationale |
|------------|----------|-----------|
| **Databricks Unity Catalog** | **Adopt** | Core governance platform, production-ready |
| **Delta Lake 3.0** | **Adopt** | Stable, all features we need |
| **Photon Engine** | **Adopt** | 2-3× speedup on SQL, production-ready |
| **Databricks Lakehouse AI** | **Trial** | GenAI on lakehouse, POC in Q2 2026 |
| **Delta Sharing** | **Trial** | Open banking use case, POC in Q1 2026 |
| **Databricks Serverless** | **Trial** | POC in Q4 2025, evaluate cost/performance |
| **Azure OpenAI Service** | **Assess** | Chatbot, fraud detection, need business case |
| **Quantum-Safe Encryption** | **Assess** | Future-proof (5-10 years), monitor NIST standards |
| **On-Prem Databricks** | **Hold** | Cloud-first strategy, no on-prem requirement |
| **Apache Iceberg (alternative to Delta Lake)** | **Hold** | Delta Lake meets needs, avoid churn |

### 12.2 Innovation Budget

**Annual Innovation Budget**: LKR 20M (3% of total platform budget)

**Allocation:**
- **POCs**: LKR 10M (up to 5 POCs/year @ LKR 2M each)
- **Training**: LKR 5M (certifications, conferences, e.g., Data + AI Summit)
- **Consulting**: LKR 5M (external experts for emerging tech evaluation)

**ROI Expectation**: Each POC must demonstrate >3:1 ROI to proceed to rollout

### 12.3 External Engagement

**Vendor Engagement:**
- **Databricks**: Quarterly business review (roadmap preview, feature requests)
- **Microsoft Azure**: Annual strategic planning session

**Community Engagement:**
- **Conferences**: Send 2 engineers to Data + AI Summit annually
- **User Groups**: Participate in Databricks Sri Lanka User Group (if exists, else virtual)
- **Open Source**: Contribute bug fixes to Delta Lake (builds expertise, gives back)

**Academic Partnerships:**
- **University of Colombo**: Collaborate on research (e.g., fraud detection ML models)
- **Internship Program**: Host 2 interns/year from top universities (pipeline for hiring)

---

## 13. Conclusion

### 13.1 Governance Success Metrics (Year 1)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Platform Availability** | >99.9% | Azure Monitor + Databricks uptime |
| **Change Success Rate** | >95% (changes deployed without rollback) | Change control log |
| **Mean Time to Resolve (MTTR) Incidents** | <4 hours (Sev 1), <24 hours (Sev 2) | Incident tracking system |
| **Technical Debt Ratio** | <20% of total backlog | JIRA debt vs. feature ratio |
| **User Satisfaction** | >85% | Quarterly survey |
| **Cost Variance** | <10% | Monthly budget review |

### 13.2 Next Steps (Immediate Actions)

1. **Week 1**: Establish BAU team (hire/transition from project team)
2. **Week 2**: Deploy monitoring dashboards (real-time, daily, weekly, monthly)
3. **Week 4**: Conduct first Quarterly Architecture Review
4. **Month 2**: Baseline performance metrics (3-month average)
5. **Month 3**: Initiate first innovation POC (Databricks Serverless)
6. **Month 6**: Annual Architecture Health Check (external consultant)

---

## 14. Approval

**Phase H (Architecture Change Management) Document:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Platform Owner** | [Name] | | |
| **Chief Architect (ARB Chair)** | [Name] | | |
| **Platform Manager** | [Name] | | |
| **CIO (Sponsor)** | [Name] | | |
| **COO (Steering Committee Chair)** | [Name] | | |

---

**Document Version**: 1.0  
**Date**: December 2025  
**Classification**: Internal - Confidential  
**Next Review**: After first year of BAU operations (Month 24)

---

**END OF PHASE H**

---

**🎉 TOGAF ADM COMPLETE 🎉**

All 8 phases (Preliminary through Phase H) have been documented for Commercial Bank of Sri Lanka's Data Platform Transformation initiative. The architecture is now ready for governance, operations, and continuous evolution.
