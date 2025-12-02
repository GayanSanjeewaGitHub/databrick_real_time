# Phase D: Technology Architecture
## Commercial Bank of Sri Lanka – Infrastructure & Platform

---

## 1. Introduction

### 1.1 Purpose
This document defines the Technology Architecture for Commercial Bank's Azure Databricks data platform, including infrastructure components, networking, security, compute resources, and operational considerations.

### 1.2 Scope
- Azure cloud infrastructure
- Network architecture (ExpressRoute, vNets, private endpoints)
- Databricks platform configuration
- Security architecture (CMK, IAM, monitoring)
- Disaster recovery and business continuity
- DevOps and CI/CD pipelines

---

## 2. Technology Architecture Overview

### 2.1 Logical Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                 ON-PREMISES DATA CENTER (Colombo)                    │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  Core Banking (Finacle)  │  Card System (Way4)  │  Channels   │  │
│  │  Loan System │ CRM │ Branch Systems │ ATM Switch               │  │
│  └───────────────┬──────────────────────────────────────────────────┘  │
│                  │                                                   │
│         ┌────────▼────────┐                                          │
│         │ Edge Gateway    │  Firewall, API Gateway, File Staging    │
│         └────────┬────────┘                                          │
│                  │                                                   │
│         ┌────────▼────────┐                                          │
│         │ ExpressRoute    │  1 Gbps Private Circuit                 │
│         │ Gateway (On-Prem)│                                         │
│         └────────┬────────┘                                          │
└──────────────────┼───────────────────────────────────────────────────┘
                   │ (Private Peering)
                   │
┌──────────────────▼───────────────────────────────────────────────────┐
│                     AZURE (Southeast Asia Region)                    │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  Azure Virtual Network (vNet)                  │   │
│  │                      10.10.0.0/16                              │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  ExpressRoute Gateway                                     │ │   │
│  │  │  (UltraPerformance SKU)                                   │ │   │
│  │  └────────┬─────────────────────────────────────────────────┘ │   │
│  │           │                                                    │   │
│  │  ┌────────┴─────────┬──────────────┬────────────────┐        │   │
│  │  │                  │              │                │        │   │
│  │  │ Management       │ Databricks   │ Databricks    │        │   │
│  │  │ Subnet           │ Private      │ Public        │        │   │
│  │  │ 10.10.1.0/24     │ Subnet       │ Subnet        │        │   │
│  │  │                  │ 10.10.10.0/24│ 10.10.11.0/24 │        │   │
│  │  │ ┌─────────────┐  │              │               │        │   │
│  │  │ │Bastion Host │  │              │               │        │   │
│  │  │ └─────────────┘  │              │               │        │   │
│  │  └──────────────────┴──────────────┴───────────────┘        │   │
│  │                                                               │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  Private Endpoints Subnet (10.10.20.0/24)                │ │   │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐      │ │   │
│  │  │  │ ADLS │  │  KV  │  │ SQL  │  │  EH  │  │  DB  │      │ │   │
│  │  │  │  PE  │  │  PE  │  │  PE  │  │  PE  │  │  PE  │      │ │   │
│  │  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘      │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                    Core Azure Services                         │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │  │  ADLS Gen2   │  │  Key Vault   │  │  Event Hubs  │        │   │
│  │  │ (cmbprodlake)│  │ (cmb-kv-prod)│  │(cmb-eh-prod) │        │   │
│  │  │  ┌────────┐  │  │  ┌────────┐  │  │              │        │   │
│  │  │  │  CMK   │◄─┼──┼──┤  CMK   │  │  │              │        │   │
│  │  │  │Encrypted│  │  │  │  HSM   │  │  │              │        │   │
│  │  │  └────────┘  │  │  └────────┘  │  │              │        │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │         Azure Databricks Premium Workspace                     │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  Control Plane (Managed by Databricks)                    │ │   │
│  │  │  - Workspace UI, Notebooks, Jobs, Repos                   │ │   │
│  │  │  - Unity Catalog Metastore (cmb_prod_metastore)           │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  │  ┌──────────────────────────────────────────────────────────┐ │   │
│  │  │  Data Plane (Customer's vNet - Secure Cluster Connectivity)│ │   │
│  │  │  ┌────────────┐  ┌────────────┐  ┌────────────┐          │ │   │
│  │  │  │DLT Pipeline│  │ Streaming  │  │SQL Warehouse│          │ │   │
│  │  │  │  Cluster   │  │   Cluster  │  │  (Serverless)│          │ │   │
│  │  │  └────────────┘  └────────────┘  └────────────┘          │ │   │
│  │  └──────────────────────────────────────────────────────────┘ │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │              Management & Monitoring                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │   │
│  │  │Azure Monitor │  │  Log Analytics│  │  Sentinel    │        │   │
│  │  │ (Metrics)    │  │  (Logs)       │  │  (SIEM)      │        │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘        │   │
│  └───────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 3. Network Architecture

### 3.1 ExpressRoute Configuration

**Circuit Details:**
- **Provider**: Dialog Axiata / SLT (local telco)
- **Bandwidth**: 1 Gbps (upgradeable to 10 Gbps)
- **Peering Type**: Private Peering (for Azure vNet connectivity)
- **Redundancy**: Single circuit + SLA 99.95%
- **Location**: Colombo DC → Singapore ExpressRoute Meet-Me location
- **BGP Setup**: Bank's ASN + Azure ASN, route filtering

**Routing:**
- Default route: All Azure-bound traffic via ExpressRoute
- No public internet route for data platform traffic
- Split-tunnel: Non-Azure traffic via bank's internet gateway

**SLA & Performance:**
- Latency: <40ms (Colombo ↔ Singapore)
- Packet loss: <0.1%
- Availability: 99.95% (4.4 hours downtime/year max)

### 3.2 Virtual Network Design

**vNet: `cmb-prod-vnet` (10.10.0.0/16)**

| Subnet | CIDR | Purpose | NSG Rules |
|--------|------|---------|-----------|
| **GatewaySubnet** | 10.10.0.0/27 | ExpressRoute Gateway | Azure-managed |
| **AzureBastionSubnet** | 10.10.1.0/26 | Secure RDP/SSH bastion | Inbound: 443 from Corp IPs |
| **ManagementSubnet** | 10.10.1.64/26 | Jump boxes, DevOps agents | Inbound: 22/3389 via Bastion only |
| **DatabricksPrivateSubnet** | 10.10.10.0/24 | Databricks worker nodes (private) | Outbound: To ADLS PE, Key Vault PE |
| **DatabricksPublicSubnet** | 10.10.11.0/24 | Databricks worker nodes (public, but no PIP) | Outbound: Controlled egress |
| **PrivateEndpointsSubnet** | 10.10.20.0/24 | Private endpoints for PaaS | Inbound: From Databricks subnets |

**Network Security Groups (NSGs):**
- **DatabricksPrivateSubnet-NSG:**
  - Allow: Intra-subnet (worker-to-worker)
  - Allow: Outbound to ADLS PE (443)
  - Allow: Outbound to Key Vault PE (443)
  - Deny: All other outbound internet
- **PrivateEndpoints-NSG:**
  - Allow: Inbound from Databricks subnets (443)
  - Deny: All public inbound

**Route Tables:**
- **DatabricksSubnetsRT:**
  - 0.0.0.0/0 → ExpressRoute Gateway (force-tunnel all traffic via on-prem)
  - 10.10.0.0/16 → Virtual Network (local vNet traffic)
  - Azure Databricks control plane IPs → Internet (required for management)

### 3.3 Private Endpoints

**Private Endpoint Strategy: All PaaS services accessible via private IPs only**

| Service | Private Endpoint | Private IP | DNS Zone |
|---------|------------------|------------|----------|
| **ADLS Gen2** (`cmbprodlake`) | `pe-adls-prod` | 10.10.20.10 | `privatelink.dfs.core.windows.net` |
| **Key Vault** (`cmb-kv-prod`) | `pe-kv-prod` | 10.10.20.11 | `privatelink.vaultcore.azure.net` |
| **Event Hubs** (`cmb-eh-prod`) | `pe-eh-prod` | 10.10.20.12 | `privatelink.servicebus.windows.net` |
| **SQL Database** (optional) | `pe-sql-prod` | 10.10.20.13 | `privatelink.database.windows.net` |
| **Databricks Workspace** | `pe-dbx-ui` / `pe-dbx-backend` | 10.10.20.20, 10.10.20.21 | `privatelink.azuredatabricks.net` |

**Private DNS Zones:**
- Hosted in Azure DNS (linked to `cmb-prod-vnet`)
- On-prem DNS conditional forwards to Azure DNS for `*.privatelink.*` queries
- Ensures `cmbprodlake.dfs.core.windows.net` resolves to 10.10.20.10 (not public IP)

### 3.4 Secure Cluster Connectivity (No Public IPs)

**Databricks Secure Cluster Connectivity:**
- Worker nodes get **private IPs only** (no public IPs assigned)
- Outbound connectivity to Databricks control plane via NAT or service endpoints
- Benefits: Reduced attack surface, compliance with no-public-IP policies

**Configuration:**
```hcl
# Terraform snippet
resource "azurerm_databricks_workspace" "cmb_prod" {
  name                = "cmb-dbx-prod"
  resource_group_name = azurerm_resource_group.cmb_prod.name
  location            = azurerm_resource_group.cmb_prod.location
  sku                 = "premium"

  custom_parameters {
    no_public_ip        = true
    vnet_address_prefix = "10.10.10.0/23"
    public_subnet_name  = "DatabricksPublicSubnet"
    private_subnet_name = "DatabricksPrivateSubnet"
  }

  network_security_group_rules_required = "NoAzureDatabricksRules"
}
```

---

## 4. Compute Architecture

### 4.1 Databricks Cluster Types

#### 4.1.1 Job Clusters (Ephemeral)

**DLT Pipelines:**
- Auto-provisioned by Delta Live Tables
- Autoscaling: 2 → 10 workers (Standard_E8ds_v5)
- Purpose: Bronze → Silver → Gold transformations
- Photon enabled: Yes
- Lifecycle: Created per pipeline run, terminated after

**Streaming Jobs:**
- Always-on clusters for real-time ingestion
- Configuration:
  - Driver: Standard_E8ds_v5 (8 cores, 64 GB RAM)
  - Workers: 4-8 x Standard_E8ds_v5 (autoscaling)
  - Databricks Runtime: 13.3 LTS (includes Photon)
  - Spot instances: No (requires high availability)
- Use Cases: Card authorizations, mobile sessions, CDC streams

**Batch ETL Jobs:**
- Scheduled daily/hourly runs
- Configuration:
  - Driver: Standard_E4ds_v5 (4 cores, 32 GB RAM)
  - Workers: 2-6 x Standard_E8ds_v5 (autoscaling)
  - Spot instances: Yes (70% cost savings, fault-tolerant workloads)

#### 4.1.2 SQL Warehouses (Serverless)

**Purpose:** Interactive analytics, BI dashboards, ad-hoc queries

**Configuration:**
- **Warehouse Size**: Medium (16 DBUs, ~4 clusters worth)
- **Autoscaling**: Yes (min 1, max 4 clusters)
- **Auto-stop**: 15 minutes idle
- **Photon**: Enabled (2-5x faster for aggregations)
- **Serverless**: Yes (instant start, no cluster management)

**Access:**
- Power BI via Databricks SQL Connector
- Tableau via JDBC
- Python/R notebooks via SQL magic

#### 4.1.3 All-Purpose Clusters (Dev/Test)

**Purpose:** Data scientist exploratory work, notebook development

**Configuration:**
- **Driver**: Standard_D4ds_v5 (4 cores, 16 GB)
- **Workers**: 0-2 (single-node for small datasets, or autoscaling)
- **Auto-termination**: 60 minutes
- **Spot instances**: Yes
- **Access Control**: Unity Catalog controls which users can create clusters

### 4.2 Cluster Policies

**Policy: Production Jobs (Enforced for `cmb_prod_service_principal`)**
```json
{
  "spark_version": {
    "type": "fixed",
    "value": "13.3.x-scala2.12"
  },
  "node_type_id": {
    "type": "allowlist",
    "values": ["Standard_E8ds_v5", "Standard_E4ds_v5"]
  },
  "autoscale": {
    "type": "fixed",
    "value": {
      "min_workers": 2,
      "max_workers": 10
    }
  },
  "spark_conf": {
    "type": "fixed",
    "value": {
      "spark.databricks.delta.optimizeWrite.enabled": "true",
      "spark.databricks.delta.autoCompact.enabled": "true"
    }
  },
  "enable_elastic_disk": {
    "type": "fixed",
    "value": true
  }
}
```

**Policy: Data Scientist Dev Clusters (For `cmb_data_scientists` group)**
```json
{
  "spark_version": {
    "type": "allowlist",
    "values": ["13.3.x-scala2.12", "14.0.x-scala2.12"]
  },
  "node_type_id": {
    "type": "allowlist",
    "values": ["Standard_D4ds_v5", "Standard_D8ds_v5"]
  },
  "autotermination_minutes": {
    "type": "range",
    "minValue": 30,
    "maxValue": 120
  },
  "num_workers": {
    "type": "range",
    "minValue": 0,
    "maxValue": 4
  }
}
```

### 4.3 Databricks Runtime Selection

| Workload | Runtime | Photon | Notes |
|----------|---------|--------|-------|
| **DLT Pipelines** | 13.3 LTS | Yes | Automatic |
| **Streaming Jobs** | 13.3 LTS | Yes | Stability + performance |
| **ML Training** | 14.0 ML | No | Latest ML libraries |
| **SQL Warehouse** | Serverless | Yes | Managed by Databricks |

---

## 5. Storage Architecture

### 5.1 ADLS Gen2 Configuration

**Storage Account: `cmbprodlake`**

**Settings:**
- **Performance Tier**: Premium (Block Blobs) for hot data, Standard for cool/archive
- **Replication**: ZRS (Zone-Redundant Storage) within Southeast Asia region
- **Hierarchical Namespace**: Enabled (required for Delta Lake)
- **Access Tier**: Hot (for `/raw`, `/bronze`, `/silver`, `/gold`), Cool (for older partitions)
- **Blob Versioning**: Enabled (audit trail for regulatory compliance)
- **Soft Delete**: 30 days (recover accidentally deleted data)

**Encryption:**
- **At Rest**: Customer-Managed Key (CMK) from `cmb-kv-prod`
- **In Transit**: TLS 1.3
- **Key Rotation**: Annual (automated via Key Vault policy)

**Network:**
- **Public Network Access**: Disabled
- **Private Endpoint**: `pe-adls-prod` (10.10.20.10)
- **Firewall**: Allow only trusted Azure services (Databricks, Event Hubs)

**Lifecycle Management:**
```json
{
  "rules": [
    {
      "name": "MoveOldRawToCool",
      "enabled": true,
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["lake/raw/"]
        },
        "actions": {
          "baseBlob": {
            "tierToCool": { "daysAfterModificationGreaterThan": 90 },
            "tierToArchive": { "daysAfterModificationGreaterThan": 730 }
          }
        }
      }
    },
    {
      "name": "DeleteOldCheckpoints",
      "enabled": true,
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "prefixMatch": ["lake/_checkpoints/"]
        },
        "actions": {
          "baseBlob": {
            "delete": { "daysAfterModificationGreaterThan": 180 }
          }
        }
      }
    }
  ]
}
```

### 5.2 Delta Lake Configuration

**Table Properties (Standard for Silver/Gold):**
```sql
CREATE TABLE cmb_retail.silver.transactions (...)
USING DELTA
PARTITIONED BY (txn_date)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.deletedFileRetentionDuration' = 'interval 30 days',
  'delta.logRetentionDuration' = 'interval 90 days',
  'delta.enableChangeDataFeed' = 'true'  -- For CDC consumers
);
```

**VACUUM Strategy:**
```sql
-- Weekly maintenance job
VACUUM cmb_retail.silver.transactions RETAIN 720 HOURS;  -- 30 days
```

### 5.3 Unity Catalog Metastore Storage

**Metastore Root Storage:**
- Dedicated ADLS container: `cmbprodlake/unity-metastore-root`
- Encrypted with same CMK
- Stores: Managed table data, audit logs, lineage metadata

---

## 6. Security Architecture

### 6.1 Identity & Access Management

**Azure Active Directory Integration:**
```
Azure AD Tenant: commercialbank.onmicrosoft.com
  ├─ Azure AD Groups (synced to Databricks)
  │   ├─ cmb_data_admins
  │   ├─ cmb_data_engineers
  │   ├─ cmb_data_scientists
  │   ├─ cmb_analysts
  │   └─ cmb_branch_staff
  │
  ├─ Service Principals
  │   ├─ sp_cmb_dlt_retail_prod (DLT pipelines)
  │   ├─ sp_cmb_stream_cards_prod (Streaming jobs)
  │   ├─ sp_cmb_devops_ci_cd (Deployment automation)
  │   └─ sp_cmb_powerbi (Power BI access)
  │
  └─ Managed Identities
      ├─ mi-dbx-workspace (Databricks workspace → ADLS access)
      └─ mi-eventhub-ingest (Event Hubs → Databricks)
```

**Databricks Account-Level Permissions:**
- **Account Admins**: IT infrastructure team (3 users)
- **Workspace Admins**: Data platform team (5 users)
- **Unity Catalog Admins**: Chief Data Officer + 2 delegates

**Unity Catalog Grants (Example):**
```sql
-- Grant SELECT on retail catalog to analysts
GRANT USAGE ON CATALOG cmb_retail TO `cmb_analysts`;
GRANT SELECT ON CATALOG cmb_retail TO `cmb_analysts`;

-- Grant ALL on cards catalog to card data engineers
GRANT ALL PRIVILEGES ON CATALOG cmb_cards TO `cmb_cards_engineers`;

-- Grant CREATE TABLE only to data admins
GRANT CREATE TABLE ON SCHEMA cmb_retail.silver TO `cmb_data_admins`;
```

### 6.2 Encryption Architecture

**Layers of Encryption:**

1. **Network Layer:**
   - ExpressRoute (private circuit, no encryption by default but isolated)
   - TLS 1.3 for all Azure API calls
   - IPsec VPN as backup (optional)

2. **Storage Layer:**
   - ADLS: AES-256 with CMK from Key Vault
   - Databricks managed storage: AES-256 with CMK
   - Delta tables: Inherits ADLS encryption

3. **Application Layer:**
   - Column-level masking (Unity Catalog)
   - Sensitive columns (account numbers) can be encrypted via app logic if needed

**Key Vault Configuration:**
```
cmb-kv-prod (Azure Key Vault Premium + HSM)
  ├─ Keys
  │   ├─ cmk-adls-prod (RSA-HSM 4096-bit)
  │   ├─ cmk-dbx-managed-storage (RSA-HSM 4096-bit)
  │   └─ master-data-encryption-key (for app-level encryption)
  │
  ├─ Secrets
  │   ├─ kafka-bootstrap-password
  │   ├─ eventhub-connection-string
  │   └─ sql-db-connection-string
  │
  └─ Access Policies
      ├─ sp_cmb_dlt_retail_prod: Get Secrets
      ├─ mi-dbx-workspace: Unwrap Key (for ADLS CMK)
      └─ cmb_data_admins: All permissions (emergency access)
```

**CMK Rotation:**
- Automated annual rotation via Key Vault policy
- Zero downtime (Azure seamlessly re-encrypts with new key version)
- Audit log of all key usage

### 6.3 Network Security Controls

**Defense-in-Depth:**

| Layer | Control | Purpose |
|-------|---------|---------|
| **Perimeter** | ExpressRoute only, no public internet | Prevent unauthorized external access |
| **Network** | NSGs on all subnets | Micro-segmentation |
| **Identity** | Azure AD + MFA | Verify user identity |
| **Data** | Private endpoints | Eliminate public endpoints |
| **Application** | Unity Catalog RBAC | Fine-grained access control |
| **Monitoring** | Azure Sentinel | Threat detection |

**Firewall Rules (Azure Firewall - optional for additional control):**
- Allow: Databricks subnets → ADLS private endpoint (443)
- Allow: Databricks subnets → Key Vault private endpoint (443)
- Allow: Databricks subnets → Databricks control plane (443, 8443)
- Deny: All other outbound internet

---

## 7. Disaster Recovery & Business Continuity

### 7.1 RTO/RPO Targets

| Component | RPO (Data Loss) | RTO (Recovery Time) | Strategy |
|-----------|-----------------|---------------------|----------|
| **ADLS (raw/bronze)** | 0 (ZRS + replication) | 1 hour | Geo-redundant copy to East Asia |
| **Silver/Gold tables** | 15 minutes | 2 hours | Delta log replay from bronze |
| **Streaming pipelines** | 0 (Kafka retention) | 30 minutes | Checkpoint-based recovery |
| **Unity Catalog metadata** | 1 hour | 1 hour | Metastore backup to secondary region |
| **Databricks workspace** | 1 hour | 2 hours | IaC-based re-deployment |

### 7.2 Backup Strategy

**ADLS Backup:**
- **Primary**: ZRS (Zone-Redundant Storage) in Southeast Asia (3 copies across AZs)
- **Secondary**: GRS (Geo-Redundant Storage) to East Asia (6 copies total)
- **Backup Frequency**: Continuous (async replication)
- **Restore Process**: `azcopy sync` from secondary to primary (or failover)

**Unity Catalog Backup:**
- **Method**: Delta Sharing export of metastore to secondary ADLS account
- **Frequency**: Hourly
- **Contents**: Table metadata, grants, lineage, audit logs

**Code & Configuration Backup:**
- **Git Repos**: Azure DevOps (geo-replicated by Microsoft)
- **IaC (Terraform)**: Version-controlled in Git
- **Databricks workspace notebooks**: Exported nightly to ADLS

### 7.3 Disaster Recovery Procedures

**Scenario 1: ExpressRoute Circuit Failure**
- **Detection**: Azure Monitor alert on circuit down
- **Mitigation**: Activate backup IPsec VPN (pre-configured)
- **SLA**: 15-minute failover

**Scenario 2: Azure Region Failure (Southeast Asia)**
- **Detection**: Azure Service Health dashboard
- **Action**:
  1. Promote East Asia ADLS (GRS secondary) to primary (15 min)
  2. Deploy Databricks workspace in East Asia via Terraform (30 min)
  3. Point Unity Catalog to restored metastore (15 min)
  4. Resume streaming jobs from last checkpoint (30 min)
- **Total RTO**: ~2 hours

**Scenario 3: Data Corruption (Accidental DELETE)**
- **Detection**: Data quality monitoring, user report
- **Action**: Delta Time Travel to restore previous version
  ```sql
  RESTORE TABLE cmb_retail.silver.customers TO VERSION AS OF 1234;
  ```
- **RTO**: <15 minutes

---

## 8. Monitoring & Observability

### 8.1 Azure Monitor Integration

**Metrics Collected:**
- Databricks: Cluster CPU/memory utilization, job duration, driver/executor metrics
- ADLS: Ingress/egress bandwidth, transaction count, latency
- Key Vault: Key usage, secret access, latency
- Event Hubs: Incoming/outgoing messages, throttling

**Dashboards:**
- **Platform Health**: Uptime, error rates, resource utilization
- **Data Pipelines**: Job success/failure, SLA compliance, data freshness
- **Cost Management**: Databricks DBU consumption, ADLS storage costs

**Alerts:**
| Alert | Condition | Action |
|-------|-----------|--------|
| **Job Failure** | DLT pipeline fails | Email to on-call engineer + Slack |
| **High Latency** | Card auth stream lag >5 min | PagerDuty escalation |
| **CMK Unavailable** | Key Vault access denied | Critical alert to CISO |
| **Cost Spike** | Daily DBU consumption >150% baseline | Email to FinOps team |

### 8.2 Databricks System Tables

**Audit Logging:**
```sql
-- Query who accessed customer PII today
SELECT user_name, action_name, request_params, event_time
FROM system.access.audit
WHERE table_name = 'cmb_retail.silver.customers'
  AND event_date = current_date();
```

**Lineage Tracking:**
```sql
-- Find all downstream dependencies of transactions table
SELECT target_table_full_name, target_column_name
FROM system.access.column_lineage
WHERE source_table_full_name = 'cmb_retail.silver.transactions';
```

**Billing Usage:**
```sql
-- Daily DBU consumption by workspace
SELECT usage_date, workspace_id, SUM(usage_quantity) AS total_dbus
FROM system.billing.usage
WHERE usage_date >= current_date() - INTERVAL 30 DAYS
GROUP BY usage_date, workspace_id;
```

### 8.3 Azure Sentinel (SIEM)

**Use Cases:**
- Detect anomalous data access patterns (e.g., user downloads 1M customer records)
- Alert on failed MFA attempts to Databricks workspace
- Correlate Databricks audit logs with Azure AD sign-in logs
- Automated response: Disable user account if suspicious activity detected

---

## 9. DevOps & CI/CD

### 9.1 Deployment Pipeline

```
Developer Workflow:
  ├─ 1. Code in VS Code (local)
  ├─ 2. Commit to Git feature branch
  ├─ 3. Create Pull Request (PR) in Azure DevOps
  ├─ 4. Automated checks:
  │     ├─ Lint (pylint, sqlfluff)
  │     ├─ Unit tests (pytest)
  │     ├─ Integration tests (against dev workspace)
  │     └─ Security scan (checkov for IaC)
  ├─ 5. Code review + approval
  ├─ 6. Merge to main branch
  └─ 7. CI/CD pipeline triggers:
        ├─ DEV → Deploy notebooks, DLT pipelines, jobs
        ├─ QA → Smoke tests, UAT
        └─ PROD → Blue-green deployment (requires manual approval)
```

**Azure DevOps Pipeline (YAML snippet):**
```yaml
trigger:
  branches:
    include:
      - main
  paths:
    include:
      - 12_bank_commercial_sri_lanka/**

stages:
  - stage: Build
    jobs:
      - job: LintAndTest
        steps:
          - task: UsePythonVersion@0
            inputs:
              versionSpec: '3.10'
          - script: |
              pip install -r requirements.txt
              pylint **/*.py
              pytest tests/
            displayName: 'Lint and Test'

  - stage: DeployDev
    dependsOn: Build
    jobs:
      - job: DeployToDev
        steps:
          - task: DatabricksDeployScripts@0
            inputs:
              authMethod: 'ServicePrincipal'
              databricksWorkspaceUrl: '$(DEV_DBX_WORKSPACE_URL)'
              notebooksPath: '12_bank_commercial_sri_lanka/'
              targetPath: '/Repos/cmb/data-platform'

  - stage: DeployProd
    dependsOn: DeployDev
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployToProd
        environment: 'Production'
        strategy:
          runOnce:
            deploy:
              steps:
                - task: DatabricksDeployScripts@0
                  inputs:
                    databricksWorkspaceUrl: '$(PROD_DBX_WORKSPACE_URL)'
                    # ... same as dev
```

### 9.2 Infrastructure as Code (Terraform)

**Repository Structure:**
```
terraform/
├── modules/
│   ├── networking/        # vNet, subnets, NSGs, ExpressRoute
│   ├── storage/           # ADLS Gen2, lifecycle policies
│   ├── databricks/        # Workspace, metastore, catalogs
│   └── security/          # Key Vault, private endpoints
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   └── terraform.tfvars
│   ├── qa/
│   └── prod/
└── README.md
```

**Sample Terraform (ADLS with CMK):**
```hcl
resource "azurerm_storage_account" "cmb_prod_lake" {
  name                     = "cmbprodlake"
  resource_group_name      = azurerm_resource_group.cmb_prod.name
  location                 = azurerm_resource_group.cmb_prod.location
  account_tier             = "Standard"
  account_replication_type = "ZRS"
  is_hns_enabled           = true

  identity {
    type = "SystemAssigned"
  }

  customer_managed_key {
    key_vault_key_id = azurerm_key_vault_key.cmk_adls.id
  }

  network_rules {
    default_action             = "Deny"
    bypass                     = ["AzureServices"]
    virtual_network_subnet_ids = [
      azurerm_subnet.databricks_private.id,
      azurerm_subnet.databricks_public.id
    ]
  }
}

resource "azurerm_private_endpoint" "adls_pe" {
  name                = "pe-adls-prod"
  location            = azurerm_resource_group.cmb_prod.location
  resource_group_name = azurerm_resource_group.cmb_prod.name
  subnet_id           = azurerm_subnet.private_endpoints.id

  private_service_connection {
    name                           = "adls-privatelink"
    private_connection_resource_id = azurerm_storage_account.cmb_prod_lake.id
    subresource_names              = ["dfs"]
    is_manual_connection           = false
  }
}
```

---

## 10. Cost Management

### 10.1 Cost Breakdown (Monthly Estimate)

| Component | Configuration | Monthly Cost (USD) | Annual (USD) |
|-----------|---------------|--------------------|--------------|
| **ExpressRoute** | 1 Gbps Private Peering | $1,500 | $18,000 |
| **Azure vNet & Networking** | Gateway, NSGs, PE | $300 | $3,600 |
| **ADLS Gen2** | 50 TB hot, 100 TB cool | $2,000 | $24,000 |
| **Key Vault Premium** | CMK + HSM | $200 | $2,400 |
| **Databricks (Compute)** | ~3,000 DBUs/month (avg) | $12,000 | $144,000 |
| **Databricks (Platform)** | Premium workspace, Unity Catalog | $3,000 | $36,000 |
| **Event Hubs** | Standard tier, 4 TUs | $800 | $9,600 |
| **Azure Monitor & Sentinel** | Logs + SIEM | $1,200 | $14,400 |
| **TOTAL** | | **~$21,000/mo** | **~$252,000/yr** |

**3-Year TCO**: ~USD 756K (LKR 226M at 300 exchange rate)

### 10.2 Cost Optimization Strategies

1. **Spot Instances for Batch Jobs**: 70% savings on non-critical workloads
2. **Autoscaling**: Right-size clusters, terminate idle resources
3. **Reserved Capacity**: 3-year commit for Databricks → 40% discount
4. **Lifecycle Policies**: Move old data to cool/archive tiers
5. **SQL Warehouse Serverless**: Pay-per-query (no idle costs)
6. **Photon Acceleration**: Faster queries = less DBU consumption

---

## 11. Technology Standards

### 11.1 Approved Technologies

| Category | Approved | Version | Notes |
|----------|----------|---------|-------|
| **Cloud Platform** | Azure | N/A | Southeast Asia region only |
| **Data Platform** | Databricks | Premium | Unity Catalog required |
| **Runtime** | Databricks Runtime | 13.3 LTS | For production |
| **Storage** | ADLS Gen2 | V2 | Hierarchical namespace |
| **Languages** | Python, SQL, Scala | 3.10, SQL-2016, 2.12 | Python preferred |
| **BI Tools** | Power BI, Tableau | Latest | SQL Warehouse connector |
| **Version Control** | Azure DevOps Git | N/A | Private repos only |
| **IaC** | Terraform | 1.5+ | HCL syntax |

### 11.2 Prohibited Technologies

- ❌ Public-facing Databricks workspaces (must use private connectivity)
- ❌ Non-CMK encrypted storage accounts
- ❌ Direct internet egress from Databricks clusters
- ❌ Hardcoded secrets in notebooks/code
- ❌ Personal Azure subscriptions for production workloads

---

## 12. Compliance & Regulatory Alignment

### 12.1 CBSL Material Outsourcing Compliance

| CBSL Requirement | Technology Implementation |
|------------------|---------------------------|
| **Data Residency** | Azure Southeast Asia region, no cross-region replication |
| **Encryption Control** | CMK in bank-owned Key Vault, revocation capability |
| **Audit Trail** | Unity Catalog audit logs, 7-year retention |
| **Business Continuity** | DR to East Asia, RTO <2 hours |
| **Vendor Lock-in Mitigation** | IaC (Terraform), Delta format (open-source) |

### 12.2 PDPA Technical Controls

| PDPA Article | Control | Technology |
|--------------|---------|------------|
| **Right to Access** | Customer self-service portal | SQL Warehouse API |
| **Right to Erasure** | Soft-delete + VACUUM | Delta Lake GDPR features |
| **Data Minimization** | Column masking | Unity Catalog functions |
| **Breach Notification** | Automated alerting | Azure Sentinel |

---

## 13. Next Steps

### 13.1 Phase D Deliverables Checklist

- [x] Detailed network architecture (ExpressRoute, vNet, PE)
- [x] Compute architecture (clusters, policies, runtimes)
- [x] Storage architecture (ADLS, Delta, Unity Catalog)
- [x] Security architecture (IAM, encryption, NSGs)
- [x] DR/BC strategy
- [ ] Detailed Terraform/Bicep IaC scripts
- [ ] Network architecture diagram (Visio/Draw.io)
- [ ] Cost calculator spreadsheet
- [ ] Performance benchmark results (after pilot)

### 13.2 Implementation Prerequisites

1. **ExpressRoute**: Engage telco provider (SLT/Dialog), order circuit (8-12 weeks lead time)
2. **Azure Subscription**: Create prod subscription, apply policies
3. **Databricks Account**: Sign enterprise agreement, create account
4. **CBSL Approval**: Submit architecture docs, await approval (4-6 weeks)
5. **Team Training**: Databricks certification for 5 engineers (4 weeks)

---

## 14. Approvals

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **CTO** | [Name] | | |
| **Head of Infrastructure** | [Name] | | |
| **CISO** | [Name] | | |
| **Network Architect** | [Name] | | |
| **Enterprise Architect** | [Name] | | |

---

## 15. Document Control

- **Version**: 1.0
- **Status**: Draft for Review
- **Last Updated**: December 2025
- **Next Review**: After technical deep-dive session
- **Classification**: Internal - Confidential
- **Owner**: Technology Architecture Team

---

**End of Phase D: Technology Architecture**
