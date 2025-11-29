# Production Readiness Checklist

Before deploying the DBS Data Lakehouse to the Production environment, ensure all items in this checklist are validated.

## 1. Infrastructure & Security
- [ ] **Region Lock:** Verify all Storage Accounts and Databricks Workspaces are in the designated region (e.g., Southeast Asia) for data sovereignty.
- [ ] **Network Isolation:** Ensure VNet Injection is enabled. Databricks should not have public IPs.
- [ ] **Private Link:** Verify Private Link is configured for backend connectivity to Azure Storage / AWS S3.
- [ ] **Secret Scopes:** All credentials (DB passwords, API keys) are in Key Vault-backed secret scopes. No hardcoded secrets in notebooks.
- [ ] **Access Control:** Unity Catalog permissions (Grants) are applied. Verify `dbs_prod` catalog is write-locked to Service Principals only.

## 2. Data Governance (MAS TRM)
- [ ] **Audit Logging:** Verify `system.access.audit` logs are being captured and shipped to the SIEM (Security Information and Event Management) tool.
- [ ] **PII Masking:** Test the Dynamic Views. Ensure a user with `analyst` group sees `*****` for NRIC columns.
- [ ] **Backup:** Verify the Cross-Region Replication (CRR) for the storage bucket is Active.
- [ ] **Retention:** Check that `VACUUM` policies are set to > 7 years for regulatory tables (or Deep Clones are scheduled).

## 3. Pipeline & Performance
- [ ] **DLT Pipelines:** All pipelines are running in `Production` mode (not Development).
- [ ] **Checkpointing:** Verify checkpoint locations are persistent and separate from data.
- [ ] **Autoscaling:** Cluster policies allow autoscaling (e.g., 2-10 nodes) to handle burst loads.
- [ ] **Backpressure:** Streaming jobs have `spark.streaming.backpressure.enabled = true`.
- [ ] **Monitoring:** Databricks SQL Alerts are set up for pipeline failures (e.g., "If DLT failure > 0, email oncall@dbs.com").

## 4. Disaster Recovery Drill
- [ ] **Simulate Outage:** Perform a dry run of spinning up the workspace in the Secondary Region (Hong Kong).
- [ ] **RTO Check:** Measure time taken to mount the replicated storage and start the critical Fraud Detection pipeline. Target: < 1 Hour.

## 5. Cost Management
- [ ] **Tags:** Ensure all clusters have `CostCenter` and `Environment` tags.
- [ ] **Budgets:** Set up Databricks Budget alerts to notify if daily spend exceeds threshold.
