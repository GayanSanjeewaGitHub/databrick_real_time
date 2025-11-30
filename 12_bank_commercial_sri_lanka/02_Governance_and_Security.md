# Governance and Security – Commercial Bank on Azure

## 1. Data Sovereignty & Connectivity

- Traffic from Colombo DC to Azure uses **ExpressRoute**; no public internet exposure.
- Azure region: `southeastasia` or `eastasia` (closest to Sri Lanka).
- All storage accounts enforce **private endpoint** access only.

## 2. Encryption (Customer Managed Keys)

- ADLS Gen2 accounts use CMK stored in **Azure Key Vault / HSM**.
- Databricks workspace configured with CMK for managed storage.
- If the bank revokes the key in Colombo, cloud data becomes unreadable.

## 3. Identity and Access Management

- Azure AD as central identity provider.
- Databricks uses **account groups** and **service principals**.
- Unity Catalog grants use **least privilege** by domain (Retail, Cards, Loans, Channels).

## 4. Unity Catalog Controls

- **Column masking** for NIC, passport numbers, etc.
- **Row filters** to limit staff by branch or region.
- **System tables** for audit of all access and modifications.

## 5. Compliance Mapping

- Aligns with CBSL outsourcing and technology risk guidelines.
- Compatible with Sri Lanka Personal Data Protection Act (PDPA) and global best practices.
