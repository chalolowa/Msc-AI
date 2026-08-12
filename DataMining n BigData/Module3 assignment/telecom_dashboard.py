
#!/usr/bin/env python3
"""
Real-time visualization of telecom streaming data
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import subprocess
import tempfile
import os
from datetime import datetime
import time

def get_hdfs_data():
    """Get latest streaming data from HDFS"""
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()

        # Determine hdfs command location (allow override via HDFS_CMD env var)
        hdfs_cmd = os.environ.get('HDFS_CMD', '/home/locha/hadoop-3.5.0/bin/hdfs')
        # Get latest parquet files from HDFS
        cmd = f'{hdfs_cmd} dfs -ls hdfs://localhost:9000/telecom_streaming_analytics/ | grep "parquet" | tail -5 | awk "{{print $8}}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.stdout:
            files = result.stdout.strip().split('\n')
            data_frames = []
            for f in files:
                if f:
                    # Download file using explicit hdfs command
                    local_path = os.path.join(temp_dir, os.path.basename(f))
                    subprocess.run(f"{hdfs_cmd} dfs -get {f} {local_path}", shell=True, capture_output=True)
                    if os.path.exists(local_path):
                        df = pd.read_parquet(local_path)
                        data_frames.append(df)

            if data_frames:
                return pd.concat(data_frames, ignore_index=True)

    except Exception as e:
        print(f"⚠️ Error reading HDFS: {e}")

    return None

def create_dashboard():
    """Create real-time dashboard"""
    plt.style.use('seaborn-v0_8')

    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Telecom Real-Time Streaming Dashboard', fontsize=16)

    def update(frame):
        """Update dashboard with new data"""
        df = get_hdfs_data()

        if df is None or df.empty:
            for ax in axes.flatten():
                ax.clear()
                ax.text(0.5, 0.5, 'Waiting for data...', ha='center', va='center')
            return

        # Clear axes
        for ax in axes.flatten():
            ax.clear()

        # 1. Records over time
        if 'processing_time' in df.columns:
            df['processing_time'] = pd.to_datetime(df['processing_time'])
            time_counts = df.groupby(df['processing_time'].dt.floor('min')).size()
            axes[0,0].plot(time_counts.index, time_counts.values, 'b-')
            axes[0,0].set_title('Records per Minute')
            axes[0,0].set_xlabel('Time')
            axes[0,0].set_ylabel('Record Count')
            axes[0,0].tick_params(axis='x', rotation=45)

        # 2. Column distribution
        axes[0,1].bar(['Columns'], [len(df.columns)])
        axes[0,1].set_title('Number of Columns')
        axes[0,1].set_ylabel('Count')

        # 3. Sample data table
        sample = df.head(5)
        if not sample.empty:
            axes[1,0].axis('tight')
            axes[1,0].axis('off')
            axes[1,0].table(
                cellText=sample.values,
                colLabels=sample.columns,
                loc='center',
                cellLoc='center'
            )
            axes[1,0].set_title('Latest Records')

        # 4. Data statistics
        stats = {
            'Total Records': len(df),
            'Columns': len(df.columns),
            'Memory Usage': f"{df.memory_usage().sum() / 1024:.2f} KB",
            'Last Update': datetime.now().strftime('%H:%M:%S')
        }
        axes[1,1].axis('tight')
        axes[1,1].axis('off')
        axes[1,1].table(
            cellText=[[k, v] for k, v in stats.items()],
            colLabels=['Metric', 'Value'],
            loc='center'
        )
        axes[1,1].set_title('Streaming Statistics')

        plt.tight_layout()

    ani = FuncAnimation(fig, update, interval=5000)
    plt.show()

if __name__ == "__main__":
    print("🚀 Starting Telecom Streaming Dashboard...")
    print("   This will update every 5 seconds")
    create_dashboard()
