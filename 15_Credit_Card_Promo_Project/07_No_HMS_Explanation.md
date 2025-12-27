# Working Without Hive Metastore (The "Data Swamp" Scenario)

You asked: *"Is it possible to use Hive query but not use HMS when writing data?"*

**Yes.** This is exactly how "Data Swamps" are created. Developers use the power of Spark SQL (which looks like Hive) to process data, but they skip the governance step of registering it in the Metastore.

## How it works (The "No-HMS" Pattern)

In this mode, **Files are King**. The "Table" concept is temporary and exists only while the code is running.

### 1. Writing Data (Bypassing HMS)
Instead of `saveAsTable`, developers write directly to a path.

```python
# Writing directly to a folder. 
# HMS knows NOTHING about this. No table name, no schema stored centrally.
df.write.parquet("/data/lake/project_x/output")
```

### 2. Querying Data (Using SQL without HMS)
You can still write SQL, but you have to "bring your own schema" or let Spark infer it from the files every single time.

**Method A: Temporary Views (The "Session" Table)**
You create a view that acts like a table, but it dies when the script ends.
```python
df = spark.read.parquet("/data/lake/project_x/output")
df.createOrReplaceTempView("my_temp_table")

# Looks like Hive, but it's NOT Hive. It's just Spark SQL in memory.
spark.sql("SELECT * FROM my_temp_table WHERE amount > 100").show()
```

**Method B: Direct File Querying**
You can write SQL directly against the path.
```sql
SELECT * FROM parquet.`/data/lake/project_x/output`
```

## The Consequence: Why this is hard to manage
If you have 1000s of these "file dumps":
1.  **No Catalog**: You cannot run `SHOW TABLES` to see what exists. You have to browse the file system (`ls -R`).
2.  **Schema Drift**: If Job A changes the output schema (adds a column), Job B (which reads the file) might crash because it expected the old schema. HMS protects against this; file systems do not.
3.  **Lost Logic**: To understand what is in `/data/lake/project_x/output`, you have to find the code that wrote it.

## Summary Table

| Feature | With Hive Metastore (HMS) | Without HMS (File-Based) |
| :--- | :--- | :--- |
| **Write Command** | `df.write.saveAsTable("mytable")` | `df.write.parquet("/path")` |
| **Read Command** | `spark.table("mytable")` | `spark.read.parquet("/path")` |
| **SQL Access** | `SELECT * FROM mytable` | `SELECT * FROM parquet.'/path'` |
| **Persistence** | Table definition lasts forever | "Table" view dies with the script |
| **Schema Storage** | Stored in Database (HMS) | Stored in File Headers |
| **Discoverability** | Easy (`SHOW TABLES`) | Hard (File System Search) |
