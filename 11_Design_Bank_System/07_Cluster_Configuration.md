# Cluster & Compute Configurations

To ensure stability, cost control, and security in production, we apply strict **Cluster Policies** and configurations.

## 1. Cluster Policies (JSON)

Create these policies in the Compute -> Policies section to enforce standards.

### Policy: `DBS_Job_Cluster_Policy` (For ETL/DLT)
*Enforces the use of Job clusters (cheaper) and specific instance types.*

```json
{
  "cluster_type": {
    "type": "fixed",
    "value": "job"
  },
  "spark_version": {
    "type": "regex",
    "pattern": "13\\.3\\.x-scala2\\.12",
    "defaultValue": "13.3.x-scala2.12"
  },
  "node_type_id": {
    "type": "allowlist",
    "values": ["Standard_DS3_v2", "Standard_DS4_v2"],
    "defaultValue": "Standard_DS3_v2"
  },
  "driver_node_type_id": {
    "type": "fixed",
    "value": "Standard_DS3_v2"
  },
  "autotermination_minutes": {
    "type": "fixed",
    "value": 0
  },
  "custom_tags.Team": {
    "type": "fixed",
    "value": "DataEngineering"
  }
}
```

### Policy: `DBS_Interactive_Policy` (For Analysts)
*Enforces auto-termination and limits max workers to prevent cost overruns.*

```json
{
  "cluster_type": {
    "type": "fixed",
    "value": "all-purpose"
  },
  "autotermination_minutes": {
    "type": "range",
    "minValue": 10,
    "maxValue": 60,
    "defaultValue": 30
  },
  "num_workers": {
    "type": "range",
    "minValue": 1,
    "maxValue": 8,
    "defaultValue": 2
  },
  "spark_conf.spark.databricks.cluster.profile": {
    "type": "fixed",
    "value": "serverless"
  }
}
```

## 2. Production Cluster Configuration (JSON)

Use this configuration for the main **Streaming Ingestion Cluster**.

```json
{
    "cluster_name": "prod-stream-ingest-01",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS4_v2",
    "driver_node_type_id": "Standard_DS4_v2",
    "autoscale": {
        "min_workers": 2,
        "max_workers": 10
    },
    "spark_conf": {
        "spark.databricks.delta.optimizeWrite.enabled": "true",
        "spark.databricks.delta.autoCompact.enabled": "true",
        "spark.streaming.backpressure.enabled": "true",
        "spark.streaming.kafka.maxRatePerPartition": "2000"
    },
    "aws_attributes": {
        "availability": "ON_DEMAND" 
    },
    "custom_tags": {
        "Environment": "Production",
        "CostCenter": "DBS-Retail-Tech"
    }
}
```

## 3. Secret Management (Azure Key Vault / AWS Secrets Manager)

**NEVER** hardcode credentials. Use Databricks Secret Scopes.

**Setup Command (CLI):**
```bash
databricks secrets create-scope --scope dbs-prod-secrets --initial-manage-principal users
```

**Usage in Notebooks:**
```python
# Get JDBC Password
db_password = dbutils.secrets.get(scope="dbs-prod-secrets", key="core-banking-db-pass")

# Get Kafka API Key
kafka_key = dbutils.secrets.get(scope="dbs-prod-secrets", key="kafka-api-key")
```

## 4. Init Scripts (Security Agents)

If DBS requires a security agent (e.g., Splunk Forwarder, CrowdStrike) on every node.

**Path:** `dbfs:/FileStore/init-scripts/install-security-agent.sh`

```bash
#!/bin/bash
# Install corporate security agent
wget https://internal-repo.dbs.com/agents/security-agent-installer.sh
chmod +x security-agent-installer.sh
./security-agent-installer.sh --token $(dbutils secrets get scope=dbs-prod-secrets key=agent-token)
```

**Cluster Config Addition:**
```json
"init_scripts": [
    {
        "dbfs": {
            "destination": "dbfs:/FileStore/init-scripts/install-security-agent.sh"
        }
    }
]
```
