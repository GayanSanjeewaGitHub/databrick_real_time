# Databricks Compute Resources - Clusters and Pools

## Table of Contents
1. [Introduction to Compute](#introduction)
2. [Cluster Types](#cluster-types)
3. [Cluster Configuration](#cluster-configuration)
4. [Cluster Pools](#cluster-pools)
5. [Databricks Runtime](#databricks-runtime)
6. [Practical Examples](#practical-examples)
7. [Best Practices](#best-practices)

## Introduction to Compute

Compute resources in Databricks provide the processing power needed to execute data workloads. Understanding cluster management is essential for cost optimization and performance.

### Key Concepts
- **Cluster**: Set of computation resources and configurations
- **Driver Node**: Coordinates and monitors worker nodes
- **Worker Nodes**: Execute tasks in parallel
- **Cluster Modes**: Standard, High Concurrency, Single Node

## Cluster Types

### 1. All-Purpose Clusters
Interactive clusters for collaborative analysis and development.

**Characteristics:**
- Created manually via UI, CLI, or API
- Can be shared among multiple users
- Supports notebooks and ad-hoc queries
- Can be terminated and restarted
- Higher cost per DBU

**Use Cases:**
- Exploratory data analysis
- Interactive development
- Collaborative work
- Prototyping

### 2. Job Clusters
Automated clusters created for specific jobs.

**Characteristics:**
- Created automatically by job scheduler
- Dedicated to single job
- Terminated after job completion
- Cannot be restarted manually
- Lower cost per DBU

**Use Cases:**
- Production ETL pipelines
- Scheduled batch jobs
- Automated workflows
- Cost-sensitive workloads

## Cluster Configuration

### Basic Cluster Creation

**Python API Example:**
```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.compute import ClusterSpec, AutoScale

# Initialize Databricks client
w = WorkspaceClient()

# Define cluster configuration
cluster_config = ClusterSpec(
    cluster_name="my-analytics-cluster",
    spark_version="13.3.x-scala2.12",
    node_type_id="Standard_DS3_v2",
    num_workers=2,
    autoscale=AutoScale(min_workers=2, max_workers=8),
    spark_conf={
        "spark.databricks.delta.preview.enabled": "true",
        "spark.sql.adaptive.enabled": "true"
    },
    custom_tags={
        "Environment": "Development",
        "Team": "DataEngineering",
        "Project": "Analytics"
    }
)

# Create cluster
# cluster = w.clusters.create_and_wait(**cluster_config)
# print(f"Cluster created: {cluster.cluster_id}")
```

### Cluster Modes

#### 1. Standard Mode
```python
# Standard mode configuration
cluster_config = {
    "cluster_name": "standard-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "num_workers": 4,
    "spark_conf": {
        "spark.speculation": "true"
    }
}
```

#### 2. High Concurrency Mode
```python
# High Concurrency mode for multiple users
cluster_config = {
    "cluster_name": "high-concurrency-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "autoscale": {
        "min_workers": 2,
        "max_workers": 10
    },
    "spark_conf": {
        "spark.databricks.cluster.profile": "serverless",
        "spark.databricks.repl.allowedLanguages": "python,sql,r"
    }
}
```

#### 3. Single Node Mode
```python
# Single node for development/testing
cluster_config = {
    "cluster_name": "single-node-dev",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "spark_conf": {
        "spark.databricks.cluster.profile": "singleNode",
        "spark.master": "local[*]"
    },
    "custom_tags": {
        "ResourceClass": "SingleNode"
    }
}
```

### Autoscaling Configuration

```python
# Configure autoscaling for dynamic workloads
cluster_config = {
    "cluster_name": "autoscaling-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "autoscale": {
        "min_workers": 2,
        "max_workers": 16
    },
    "autotermination_minutes": 30,
    "enable_elastic_disk": True,
    "spark_conf": {
        "spark.databricks.delta.optimizeWrite.enabled": "true",
        "spark.databricks.delta.autoCompact.enabled": "true"
    }
}
```

## Cluster Pools

Pools reduce cluster start and auto-scaling times by maintaining a set of idle instances.

### Creating a Pool

```python
# Define pool configuration
pool_config = {
    "instance_pool_name": "shared-analytics-pool",
    "node_type_id": "Standard_DS3_v2",
    "min_idle_instances": 0,
    "max_capacity": 20,
    "idle_instance_autotermination_minutes": 30,
    "preloaded_spark_versions": [
        "13.3.x-scala2.12",
        "14.0.x-scala2.12"
    ],
    "custom_tags": {
        "Team": "Analytics",
        "CostCenter": "Engineering"
    }
}
```

### Using a Pool

```python
# Create cluster from pool
cluster_from_pool = {
    "cluster_name": "pool-based-cluster",
    "spark_version": "13.3.x-scala2.12",
    "instance_pool_id": "0123-456789-abcdef",
    "num_workers": 4,
    "autotermination_minutes": 20
}
```

## Databricks Runtime

### Runtime Versions

**1. Databricks Runtime (DBR)**
```python
# Standard runtime
runtime_config = {
    "spark_version": "13.3.x-scala2.12",  # Standard runtime
}

# Features:
# - Apache Spark
# - Delta Lake
# - Performance optimizations
# - Security enhancements
```

**2. Databricks Runtime ML**
```python
# ML runtime with pre-installed libraries
ml_runtime_config = {
    "spark_version": "13.3.x-cpu-ml-scala2.12",  # ML runtime
}

# Includes:
# - TensorFlow
# - PyTorch
# - XGBoost
# - scikit-learn
# - MLflow
# - Hyperopt
```

**3. Databricks Runtime for Genomics**
```python
# Genomics runtime
genomics_runtime_config = {
    "spark_version": "13.3.x-hls-scala2.12",  # Genomics runtime
}
```

## Practical Examples

### Example 1: Cluster Management Operations

```python
# Get cluster status
def get_cluster_info(cluster_id):
    """Get detailed cluster information"""
    from databricks.sdk import WorkspaceClient
    
    w = WorkspaceClient()
    cluster = w.clusters.get(cluster_id=cluster_id)
    
    print(f"Cluster Name: {cluster.cluster_name}")
    print(f"State: {cluster.state}")
    print(f"Spark Version: {cluster.spark_version}")
    print(f"Number of Workers: {cluster.num_workers}")
    print(f"Driver Node Type: {cluster.driver_node_type_id}")
    print(f"Worker Node Type: {cluster.node_type_id}")
    
    return cluster

# Start a terminated cluster
def start_cluster(cluster_id):
    """Start a stopped cluster"""
    from databricks.sdk import WorkspaceClient
    
    w = WorkspaceClient()
    w.clusters.start(cluster_id=cluster_id)
    print(f"Starting cluster: {cluster_id}")

# Stop a running cluster
def stop_cluster(cluster_id):
    """Stop a running cluster"""
    from databricks.sdk import WorkspaceClient
    
    w = WorkspaceClient()
    w.clusters.delete(cluster_id=cluster_id)
    print(f"Stopping cluster: {cluster_id}")

# Restart a cluster
def restart_cluster(cluster_id):
    """Restart a cluster"""
    from databricks.sdk import WorkspaceClient
    
    w = WorkspaceClient()
    w.clusters.restart(cluster_id=cluster_id)
    print(f"Restarting cluster: {cluster_id}")
```

### Example 2: Cluster Monitoring

```python
# Monitor cluster metrics
def monitor_cluster_metrics():
    """Monitor cluster performance metrics"""
    
    # Get Spark UI information
    spark_ui_url = spark.sparkContext.uiWebUrl
    print(f"Spark UI: {spark_ui_url}")
    
    # Get executor information
    executor_info = spark.sparkContext._jsc.sc().getExecutorMemoryStatus()
    print(f"Executor Memory Status: {executor_info}")
    
    # Get current cluster ID
    cluster_id = spark.conf.get("spark.databricks.clusterUsageTags.clusterId")
    print(f"Current Cluster ID: {cluster_id}")
    
    # Get cluster configuration
    cluster_name = spark.conf.get("spark.databricks.clusterUsageTags.clusterName")
    print(f"Cluster Name: {cluster_name}")
    
    # Check available cores
    available_cores = spark.sparkContext.defaultParallelism
    print(f"Available Cores: {available_cores}")
    
    return {
        "cluster_id": cluster_id,
        "cluster_name": cluster_name,
        "available_cores": available_cores
    }

# Usage
metrics = monitor_cluster_metrics()
```

### Example 3: Custom Spark Configuration

```python
# Advanced Spark configurations for different workloads

# Configuration for large-scale ETL
etl_cluster_config = {
    "cluster_name": "etl-production-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS4_v2",
    "autoscale": {
        "min_workers": 4,
        "max_workers": 32
    },
    "spark_conf": {
        # Optimize for large shuffles
        "spark.sql.shuffle.partitions": "400",
        "spark.sql.files.maxPartitionBytes": "134217728",  # 128 MB
        
        # Memory configuration
        "spark.executor.memory": "16g",
        "spark.executor.memoryOverhead": "4g",
        
        # Delta Lake optimizations
        "spark.databricks.delta.optimizeWrite.enabled": "true",
        "spark.databricks.delta.autoCompact.enabled": "true",
        "spark.databricks.delta.properties.defaults.autoOptimize.optimizeWrite": "true",
        
        # Adaptive Query Execution
        "spark.sql.adaptive.enabled": "true",
        "spark.sql.adaptive.coalescePartitions.enabled": "true",
        "spark.sql.adaptive.skewJoin.enabled": "true",
        
        # Performance tuning
        "spark.databricks.io.cache.enabled": "true",
        "spark.speculation": "true"
    }
}

# Configuration for streaming workloads
streaming_cluster_config = {
    "cluster_name": "streaming-cluster",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "num_workers": 8,
    "spark_conf": {
        # Streaming-specific settings
        "spark.streaming.backpressure.enabled": "true",
        "spark.streaming.kafka.maxRatePerPartition": "1000",
        
        # Checkpointing
        "spark.sql.streaming.checkpointLocation": "/mnt/checkpoints",
        
        # State management
        "spark.sql.streaming.stateStore.providerClass": 
            "com.databricks.sql.streaming.state.RocksDBStateStoreProvider",
        
        # Delta streaming
        "spark.databricks.delta.streaming.allowSourceColumnRenaming": "true"
    }
}

# Configuration for ML workloads
ml_cluster_config = {
    "cluster_name": "ml-training-cluster",
    "spark_version": "13.3.x-gpu-ml-scala2.12",
    "node_type_id": "Standard_NC6s_v3",  # GPU instance
    "num_workers": 4,
    "spark_conf": {
        # ML-specific settings
        "spark.task.cpus": "1",
        "spark.task.resource.gpu.amount": "1",
        
        # Memory for ML
        "spark.executor.memory": "32g",
        "spark.driver.memory": "32g",
        
        # MLflow integration
        "spark.databricks.mlflow.trackMLlib.enabled": "true"
    },
    "init_scripts": [
        {
            "dbfs": {
                "destination": "dbfs:/databricks/scripts/install-ml-libs.sh"
            }
        }
    ]
}
```

### Example 4: Init Scripts

```bash
# Create init script for custom setup
# File: install-custom-packages.sh

#!/bin/bash

# Install system packages
apt-get update
apt-get install -y htop

# Install Python packages
/databricks/python/bin/pip install \
    great-expectations==0.18.0 \
    pandera==0.17.0 \
    dbt-databricks==1.7.0

# Install custom libraries
/databricks/python/bin/pip install -e /dbfs/FileStore/custom-library/

# Set environment variables
echo "export CUSTOM_VAR=value" >> /etc/environment

# Configure logging
mkdir -p /var/log/custom-app
chmod 755 /var/log/custom-app
```

```python
# Use init script in cluster configuration
cluster_with_init = {
    "cluster_name": "cluster-with-init-script",
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "Standard_DS3_v2",
    "num_workers": 2,
    "init_scripts": [
        {
            "dbfs": {
                "destination": "dbfs:/databricks/init-scripts/install-custom-packages.sh"
            }
        }
    ]
}
```

### Example 5: Library Installation

```python
# Install libraries on cluster

# Method 1: Using cluster UI
# 1. Go to cluster configuration
# 2. Click "Libraries" tab
# 3. Click "Install New"
# 4. Select PyPI, Maven, or upload JAR/Wheel

# Method 2: Using notebook-scoped libraries
%pip install pandas==2.0.0 numpy==1.24.0 scikit-learn==1.3.0

# Method 3: Using cluster libraries API
library_config = {
    "cluster_id": "0123-456789-abcdef",
    "libraries": [
        {
            "pypi": {
                "package": "mlflow==2.8.0"
            }
        },
        {
            "maven": {
                "coordinates": "com.microsoft.azure:azure-eventhubs-spark_2.12:2.3.22"
            }
        },
        {
            "jar": "dbfs:/FileStore/jars/custom-library-1.0.jar"
        }
    ]
}

# Method 4: requirements.txt for clusters
# Upload requirements.txt to DBFS and reference in cluster config
"""
# requirements.txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
mlflow>=2.8.0
great-expectations>=0.18.0
"""
```

### Example 6: Cluster Policies

```json
// Cluster policy to enforce standards and control costs
{
  "cluster_type": {
    "type": "fixed",
    "value": "all-purpose"
  },
  "spark_version": {
    "type": "allowlist",
    "values": [
      "13.3.x-scala2.12",
      "14.0.x-scala2.12"
    ]
  },
  "node_type_id": {
    "type": "allowlist",
    "values": [
      "Standard_DS3_v2",
      "Standard_DS4_v2",
      "Standard_DS5_v2"
    ]
  },
  "num_workers": {
    "type": "range",
    "minValue": 1,
    "maxValue": 10
  },
  "autotermination_minutes": {
    "type": "fixed",
    "value": 30
  },
  "spark_conf.spark.databricks.cluster.profile": {
    "type": "forbidden"
  }
}
```

### Example 7: Cluster Events and Logging

```python
# Monitor cluster events
def get_cluster_events(cluster_id, limit=100):
    """Retrieve cluster events for troubleshooting"""
    from databricks.sdk import WorkspaceClient
    
    w = WorkspaceClient()
    events = w.clusters.events(
        cluster_id=cluster_id,
        limit=limit,
        order="DESC"
    )
    
    for event in events.events:
        print(f"Time: {event.timestamp}")
        print(f"Type: {event.type}")
        print(f"Details: {event.details}")
        print("-" * 50)
    
    return events

# Get cluster logs
def analyze_cluster_logs():
    """Analyze cluster logs for errors"""
    
    # Driver logs
    driver_logs = dbutils.fs.ls("dbfs:/cluster-logs/")
    
    # Look for error patterns
    log_path = "dbfs:/cluster-logs/latest/driver/log4j-active.log"
    
    try:
        log_content = dbutils.fs.head(log_path, maxBytes=10000)
        
        # Parse for errors
        errors = [line for line in log_content.split('\n') if 'ERROR' in line]
        
        print(f"Found {len(errors)} error lines")
        for error in errors[:10]:  # Show first 10 errors
            print(error)
            
    except Exception as e:
        print(f"Could not read logs: {str(e)}")
```

### Example 8: Resource Optimization

```python
# Optimize cluster resource utilization

def check_cluster_utilization():
    """Check current cluster resource utilization"""
    
    # Get current executors
    from pyspark import SparkContext
    sc = SparkContext.getOrCreate()
    
    # Executor information
    executors = sc._jsc.sc().getExecutorMemoryStatus()
    print(f"Number of executors: {len(executors)}")
    
    # Check parallelism
    default_parallelism = sc.defaultParallelism
    print(f"Default parallelism: {default_parallelism}")
    
    # Get configuration
    total_cores = int(spark.conf.get("spark.executor.cores", "4"))
    executor_memory = spark.conf.get("spark.executor.memory", "4g")
    
    print(f"Executor cores: {total_cores}")
    print(f"Executor memory: {executor_memory}")
    
    # Calculate recommended partition count
    num_executors = len(executors) - 1  # Exclude driver
    recommended_partitions = num_executors * total_cores * 2
    
    print(f"Recommended partitions: {recommended_partitions}")
    
    return {
        "num_executors": num_executors,
        "total_cores": total_cores,
        "executor_memory": executor_memory,
        "recommended_partitions": recommended_partitions
    }

# Usage
utilization = check_cluster_utilization()

# Adjust partitions based on cluster size
spark.conf.set("spark.sql.shuffle.partitions", utilization["recommended_partitions"])
```

## Best Practices

### 1. Cluster Sizing
```python
# Guidelines for cluster sizing

def recommend_cluster_size(data_size_gb, workload_type):
    """Recommend cluster configuration based on workload"""
    
    if workload_type == "etl":
        # ETL workloads: more workers, memory-optimized
        workers = max(2, data_size_gb // 50)
        node_type = "Standard_DS4_v2"
        
    elif workload_type == "streaming":
        # Streaming: steady workers, balanced compute
        workers = 4
        node_type = "Standard_DS3_v2"
        
    elif workload_type == "ml":
        # ML: fewer workers, GPU-enabled
        workers = 2
        node_type = "Standard_NC6s_v3"
        
    elif workload_type == "analytics":
        # Interactive analytics: autoscaling
        workers = {"min": 2, "max": 8}
        node_type = "Standard_DS3_v2"
    
    return {
        "workers": workers,
        "node_type": node_type,
        "autotermination_minutes": 30
    }

# Example usage
etl_config = recommend_cluster_size(500, "etl")
print(f"Recommended ETL config: {etl_config}")
```

### 2. Cost Optimization
- Use autoscaling for variable workloads
- Set autotermination for idle clusters
- Use job clusters for production workloads
- Leverage spot instances where appropriate
- Use cluster pools to reduce startup time

### 3. Performance Optimization
- Choose appropriate node types
- Configure Spark settings for workload
- Use Photon runtime when available
- Enable adaptive query execution
- Optimize shuffle partitions

### 4. Monitoring and Maintenance
- Monitor cluster metrics regularly
- Review Spark UI for bottlenecks
- Check cluster events for issues
- Analyze logs for errors
- Track costs and usage

## Summary

Key points about Databricks compute:

1. **Cluster Types**: All-purpose for interactive work, job clusters for production
2. **Autoscaling**: Dynamically adjust resources based on workload
3. **Pools**: Reduce startup time with idle instances
4. **Runtime**: Choose appropriate runtime for workload (Standard, ML, Genomics)
5. **Configuration**: Optimize Spark settings for performance and cost
6. **Monitoring**: Track metrics, events, and logs for optimization

## Next Steps
- Learn about Delta Lake storage
- Explore Streaming workloads
- Study Performance Optimization techniques
