# Databricks Workspace Fundamentals

## Table of Contents
1. [Introduction](#introduction)
2. [Workspace Components](#workspace-components)
3. [Navigation and UI](#navigation-and-ui)
4. [Creating and Managing Objects](#creating-and-managing-objects)
5. [Practical Examples](#practical-examples)

## Introduction

The Azure Databricks workspace is your central hub for accessing all Databricks objects and features. It provides an environment for accessing assets, organizing objects, and managing computational resources.

### Key Concepts
- **Workspace**: Environment for accessing all Azure Databricks assets
- **Folders**: Organize notebooks, libraries, dashboards, and experiments
- **Collaboration**: Share and collaborate on data science and ML workflows

## Workspace Components

### 1. Notebooks
Web-based interfaces containing runnable commands, visualizations, and narrative text.

**Supported Languages:**
- Python
- SQL
- Scala
- R

### 2. Clusters
Sets of computation resources and configurations for running notebooks and jobs.

**Types:**
- **All-Purpose Clusters**: For interactive analysis
- **Job Clusters**: For automated workloads

### 3. Jobs
Non-interactive mechanisms for orchestrating and scheduling notebooks and tasks.

### 4. Libraries
Packages of code available to notebooks or jobs running on clusters.

### 5. Data Objects
- Tables
- Volumes
- Files in cloud storage

## Navigation and UI

### Sidebar Navigation
```
├── Workspace
│   ├── Shared
│   ├── Users
│   └── Git Folders
├── Data
│   ├── Tables
│   ├── Databases
│   └── Volumes
├── Compute
│   ├── Clusters
│   └── Pools
├── Jobs & Pipelines
│   ├── Jobs
│   ├── Pipelines
│   └── Lakeflow Connect
└── ML
    ├── Experiments
    ├── Models
    └── Feature Store
```

### Workspace Browser
The unified workspace browser allows you to:
- Browse and manage files
- Create folders and organize objects
- Search for workspace objects
- Control access permissions

## Creating and Managing Objects

### Creating a Notebook

**Python Example:**
```python
# This is a Databricks notebook
# Cell 1: Import libraries
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp

# Cell 2: Create SparkSession
spark = SparkSession.builder.appName("MyFirstNotebook").getOrCreate()

# Cell 3: Create sample data
data = [
    (1, "John", "Engineering", 75000),
    (2, "Jane", "Marketing", 68000),
    (3, "Bob", "Sales", 72000),
    (4, "Alice", "Engineering", 80000)
]

columns = ["id", "name", "department", "salary"]
df = spark.createDataFrame(data, columns)

# Display the data
display(df)
```

### Working with Workspace Objects

**Creating a Folder Structure:**
```python
# Using dbutils to create folder structure
dbutils.fs.mkdirs("/FileStore/my-project/data")
dbutils.fs.mkdirs("/FileStore/my-project/models")
dbutils.fs.mkdirs("/FileStore/my-project/outputs")

# List directories
display(dbutils.fs.ls("/FileStore/my-project/"))
```

### Managing Files

**Upload and Read Files:**
```python
# Read CSV file
df_csv = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("/FileStore/tables/sample_data.csv")

# Read JSON file
df_json = spark.read.format("json") \
    .load("/FileStore/tables/sample_data.json")

# Read Parquet file
df_parquet = spark.read.format("parquet") \
    .load("/FileStore/tables/sample_data.parquet")

# Display data
display(df_csv)
```

## Practical Examples

### Example 1: Basic Workspace Setup

**Step 1: Create a Notebook**
```python
# Welcome to Databricks!
# This notebook demonstrates basic workspace operations

# Display Spark version
print(f"Spark Version: {spark.version}")

# Display Databricks Runtime version
print(f"Python Version: {dbutils.notebook.entry_point.getDbutils().notebook().getContext().pythonVersion().get()}")
```

**Step 2: Explore the Environment**
```python
# Get current user
current_user = spark.sql("SELECT current_user()").collect()[0][0]
print(f"Current User: {current_user}")

# List available databases
display(spark.sql("SHOW DATABASES"))

# Get workspace information
workspace_url = dbutils.notebook.entry_point.getDbutils().notebook().getContext().browserHostName().get()
print(f"Workspace URL: {workspace_url}")
```

### Example 2: Create a Sample Project

```python
# Define project structure
import os

username = spark.sql("SELECT regexp_replace(current_user(), '[^a-zA-Z0-9]', '_')").first()[0]
project_base = f"/FileStore/{username}/sample_project"

# Create directory structure
directories = [
    f"{project_base}/raw_data",
    f"{project_base}/processed_data",
    f"{project_base}/models",
    f"{project_base}/checkpoints",
    f"{project_base}/outputs"
]

for directory in directories:
    dbutils.fs.mkdirs(directory)
    print(f"Created: {directory}")

# Verify structure
display(dbutils.fs.ls(project_base))
```

### Example 3: Working with Git Folders

**Clone a Repository:**
```python
# Git integration for version control
# You can clone repositories directly in Databricks

# Example: Using Databricks Repos
# 1. Click on "Repos" in the sidebar
# 2. Click "Add Repo"
# 3. Enter Git URL
# 4. Select branch

# Access files from repo
repo_path = "/Workspace/Repos/your_username/your_repo"
```

### Example 4: Workspace Utilities

```python
# Databricks Utilities (dbutils) - Essential workspace operations

# 1. File System Utilities
print("=== File System Operations ===")
dbutils.fs.help()

# 2. List files
display(dbutils.fs.ls("/databricks-datasets/"))

# 3. Copy files
# dbutils.fs.cp("source_path", "destination_path")

# 4. Remove files (use with caution!)
# dbutils.fs.rm("path", recurse=True)

# 5. Move files
# dbutils.fs.mv("source", "destination")

# 6. Read file as text
# content = dbutils.fs.head("path/to/file.txt")
# print(content)
```

### Example 5: Notebook Workflows

```python
# Run another notebook from current notebook
# This enables modular code organization

# Basic notebook run
result = dbutils.notebook.run(
    "/Workspace/Users/your_email/another_notebook", 
    timeout_seconds=60,
    arguments={"param1": "value1", "param2": "value2"}
)

print(f"Result from child notebook: {result}")

# Example with error handling
try:
    result = dbutils.notebook.run(
        "/Workspace/Users/your_email/data_processing", 
        timeout_seconds=300,
        arguments={"date": "2024-01-01"}
    )
    print(f"Processing completed: {result}")
except Exception as e:
    print(f"Error running notebook: {str(e)}")
```

### Example 6: Widget Parameters

```python
# Create interactive widgets for parameterization

# Text widget
dbutils.widgets.text("environment", "dev", "Environment")

# Dropdown widget
dbutils.widgets.dropdown("region", "us-east", 
                        ["us-east", "us-west", "eu-west", "ap-south"], 
                        "Region")

# Multiselect widget
dbutils.widgets.multiselect("data_sources", "sales", 
                           ["sales", "inventory", "customers", "products"],
                           "Data Sources")

# Get widget values
environment = dbutils.widgets.get("environment")
region = dbutils.widgets.get("region")
data_sources = dbutils.widgets.get("data_sources")

print(f"Environment: {environment}")
print(f"Region: {region}")
print(f"Data Sources: {data_sources}")

# Remove widgets
# dbutils.widgets.removeAll()
```

### Example 7: Secrets Management

```python
# Working with Databricks Secrets for secure credential management

# Create a secret scope (done via CLI or REST API)
# databricks secrets create-scope --scope my-scope

# Store a secret (done via CLI)
# databricks secrets put --scope my-scope --key my-key

# Access secrets in notebooks
# secret_value = dbutils.secrets.get(scope="my-scope", key="my-key")

# List secret scopes
# scopes = dbutils.secrets.listScopes()
# for scope in scopes:
#     print(scope.name)

# Example: Connecting to database with secrets
# jdbc_url = f"jdbc:sqlserver://server.database.windows.net:1433;database=mydb"
# connection_properties = {
#     "user": dbutils.secrets.get(scope="my-scope", key="db-username"),
#     "password": dbutils.secrets.get(scope="my-scope", key="db-password"),
#     "driver": "com.microsoft.sqlserver.jdbc.SQLServerDriver"
# }
```

### Example 8: Display Functions

```python
# Advanced display capabilities

# Create sample data
from pyspark.sql.functions import rand, randn, expr
df = spark.range(1000) \
    .withColumn("random_value", rand(seed=42)) \
    .withColumn("normal_value", randn(seed=42)) \
    .withColumn("category", expr("CASE WHEN random_value < 0.33 THEN 'A' " +
                                  "WHEN random_value < 0.67 THEN 'B' " +
                                  "ELSE 'C' END"))

# Basic display
display(df)

# Display with limit
display(df.limit(10))

# Display summary statistics
display(df.summary())

# Display as HTML
displayHTML("<h1>Custom HTML Content</h1><p>This is a paragraph with <b>bold</b> text.</p>")

# Create visualization-ready data
summary_df = df.groupBy("category") \
    .agg({"random_value": "avg", "normal_value": "avg", "*": "count"})

display(summary_df)
```

## Best Practices

### 1. Organize Your Workspace
- Create logical folder structures
- Use naming conventions
- Separate development, staging, and production environments

### 2. Version Control
- Use Git folders for code versioning
- Commit changes regularly
- Use meaningful commit messages

### 3. Collaboration
- Share notebooks with appropriate permissions
- Document your code with comments and markdown cells
- Use notebooks for reproducible analysis

### 4. Security
- Use secrets for sensitive information
- Follow the principle of least privilege
- Regularly review access permissions

### 5. Performance
- Clean up unused resources
- Use appropriate cluster sizes
- Terminate clusters when not in use

## Workspace Configuration

### Setting Up Personal Preferences

```python
# Check current configuration
spark.conf.get("spark.databricks.clusterUsageTags.clusterOwnerOrgId")

# Display all Spark configurations
for conf in spark.sparkContext.getConf().getAll():
    print(f"{conf[0]} = {conf[1]}")
```

### Workspace Settings

**Key Settings to Configure:**
1. **Cluster Policies**: Control cluster creation and costs
2. **Access Control**: Manage permissions
3. **Workspace Settings**: Customize UI and features
4. **Admin Console**: Configure workspace-level settings

## Summary

The Databricks workspace provides a comprehensive environment for:
- Interactive data analysis and exploration
- Collaborative development
- Managing computational resources
- Organizing data assets
- Version control integration
- Secure secret management

### Key Takeaways
1. Workspaces organize all Databricks assets in one place
2. Multiple languages are supported (Python, SQL, Scala, R)
3. Built-in utilities (dbutils) simplify common tasks
4. Git integration enables version control
5. Secrets management keeps credentials secure
6. Widgets enable parameterized notebooks

## Next Steps
- Explore Compute Resources (Clusters and Pools)
- Learn about Delta Lake
- Dive into Structured Streaming
- Study Data Engineering pipelines

## Additional Resources
- [Azure Databricks Documentation](https://learn.microsoft.com/en-us/azure/databricks/)
- [Databricks Academy](https://www.databricks.com/learn/training)
- [Community Edition](https://community.cloud.databricks.com/)
