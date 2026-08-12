
#!/usr/bin/env python3

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os
import time

# Set environment (for safety) and allow overrides via environment variables
os.environ.setdefault('SPARK_HOME', '/home/locha/spark-4.1.2-bin-hadoop3')
os.environ.setdefault('HADOOP_HOME', '/home/locha/hadoop-3.5.0')
os.environ.setdefault('JAVA_HOME', '/usr/lib/jvm/java-17-openjdk-amd64')

# Allow selecting the Spark master using the SPARK_MASTER env var (e.g. 'yarn' or 'local[*]')
spark_master = os.environ.get('SPARK_MASTER', 'local[*]')

# If running inside WSL/remote container, bind Spark UI to an accessible IP by default
os.environ.setdefault('SPARK_LOCAL_IP', os.environ.get('SPARK_LOCAL_IP', '0.0.0.0'))

# Ensure Hadoop config is visible to Spark
if 'HADOOP_HOME' in os.environ and os.path.isdir(os.path.join(os.environ['HADOOP_HOME'], 'etc', 'hadoop')):
    os.environ.setdefault('HADOOP_CONF_DIR', os.path.join(os.environ['HADOOP_HOME'], 'etc', 'hadoop'))

# Create Spark session (use parentheses to avoid line-continuation issues)
spark = (
    SparkSession.builder
    .appName("TelecomHDFSStreaming")
    .master(spark_master)
    .config("spark.sql.streaming.schemaInference", "true")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.driver.memory", "2g")
    .config("spark.executor.memory", "2g")
    .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

print(f"✅ Spark {spark.version} ready!")
print(f"📊 Spark UI: http://localhost:4040")

# Path to HDFS telecom data
hdfs_path = "hdfs://localhost:9000/telecom/"
print(f"📡 Streaming from: {hdfs_path}")

try:
    # Check if HDFS has data
    hdfs_files = spark.sparkContext._jvm.org.apache.hadoop.fs.FileSystem.get(
        spark.sparkContext._jsc.hadoopConfiguration()
    ).listStatus(
        spark.sparkContext._jvm.org.apache.hadoop.fs.Path(hdfs_path)
    )

    file_count = len(hdfs_files)
    print(f"📁 Found {file_count} files in HDFS /telecom")

    if file_count == 0:
        print("⚠️ No files found! Please upload data to HDFS.")
        print("   hdfs dfs -put /home/hadoop-projects/CleanedTables/*.csv /telecom/")
        spark.stop()
        exit(0)

except Exception as e:
    print(f"⚠️ Could not access HDFS: {e}")
    print("   Make sure Hadoop services are running:")
    print("   cd /home/locha/hadoop-3.5.0/sbin && ./start-dfs.sh")

# Read streaming data from HDFS
stream_df = (
    spark.readStream
    .option("header", "false")
    .option("maxFilesPerTrigger", 1)
    .option("recursiveFileLookup", "true")
    .csv(hdfs_path)
)

print("✅ Streaming DataFrame created!")

# Add processing metadata
processed_stream = (
    stream_df
    .withColumn("processing_time", current_timestamp())
    .withColumn("source_file", input_file_name())
    # monotonically_increasing_id is not supported in streaming DataFrames; use processing_time as batch marker
    .withColumn("batch_time", current_timestamp())
)

# Query 1: Show live data stream
query1 = (
    processed_stream.writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", "false")
    .option("numRows", 10)
    .trigger(processingTime="5 seconds")
    .start()
)

print("✅ Query 1 started: Console Output")

# Query 2: Save to HDFS Parquet for analysis
output_hdfs = "hdfs://localhost:9000/telecom_streaming_analytics/"
query2 = (
    processed_stream.writeStream
    .outputMode("append")
    .format("parquet")
    .option("path", output_hdfs)
    .option("checkpointLocation", "/tmp/checkpoints")
    .trigger(processingTime="10 seconds")
    .start()
)

print(f"✅ Query 2 started: Saving to {output_hdfs}")

print("""
===========================================
    🚀 STREAMING ACTIVE
===========================================
Monitoring: http://localhost:4040
HDFS Data: http://localhost:9870/explorer.html#/telecom

Press Ctrl+C to stop streaming...
===========================================
""")

# Keep streaming running
try:
    spark.streams.awaitAnyTermination()
except KeyboardInterrupt:
    print("\\n⏹️ Stopping streaming...")
    spark.streams.stop()
    print("✅ Streaming stopped")
finally:
    spark.stop()
