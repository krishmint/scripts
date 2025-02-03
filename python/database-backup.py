import boto3
import time
import datetime

# Configuration
RDS_INSTANCE_ID = "your-rds-instance-id"
SNAPSHOT_ID = f"{RDS_INSTANCE_ID}-backup-{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}"
              # The f"..." syntax is a formatted string, It allows us to embed variables directly inside the string. 
              # strftime() converts the date-time object into a formatted string.
S3_BUCKET = "your-s3-bucket-name"
EXPORT_TASK_ID = f"{SNAPSHOT_ID}-export"
IAM_ROLE_ARN = "arn:aws:iam::123456789012:role/MyRDSExportRole"
S3_EXPORT_PATH = f"s3://{S3_BUCKET}/rds-exports/{SNAPSHOT_ID}/"

# Initialize AWS clients
rds_client = boto3.client("rds")

def create_rds_snapshot():
    """Create an RDS snapshot."""
    print(f"Creating snapshot: {SNAPSHOT_ID}")
    rds_client.create_db_snapshot(
        DBInstanceIdentifier=RDS_INSTANCE_ID,
        DBSnapshotIdentifier=SNAPSHOT_ID
    )

    # Wait for snapshot to be available
    while True:
        snapshot = rds_client.describe_db_snapshots(DBSnapshotIdentifier=SNAPSHOT_ID)["DBSnapshots"][0]
        status = snapshot["Status"]
        print(f"Snapshot Status: {status}")
        if status == "available":
            print("Snapshot created successfully.")
            return SNAPSHOT_ID
        time.sleep(60)  # Check status every 60 seconds

def export_snapshot_to_s3(snapshot_id):
    """Export the RDS snapshot to S3 in Parquet format."""
    print(f"Starting export task: {EXPORT_TASK_ID}")
    rds_client.start_export_task(
        ExportTaskIdentifier=EXPORT_TASK_ID,
        SourceArn=f"arn:aws:rds:region:account-id:snapshot:{snapshot_id}",
        S3BucketName=S3_BUCKET,
        IamRoleArn=IAM_ROLE_ARN,
        KmsKeyId="your-kms-key-id",  # Replace with your KMS Key ID or remove for SSE-S3
        S3Prefix=f"rds-exports/{snapshot_id}/",
        ExportOnly=["postgresql"]  # Specify databases/tables (optional)
    )

    # Monitor export task
    while True:
        task_status = rds_client.describe_export_tasks(ExportTaskIdentifier=EXPORT_TASK_ID)["ExportTasks"][0]["Status"]
        print(f"Export Task Status: {task_status}")
        if task_status == "complete":
            print(f"Export completed successfully! Data available at {S3_EXPORT_PATH}")
            break
        elif task_status == "failed":
            print("Export task failed.")
            break
        time.sleep(120)  # Check status every 2 minutes

def main():
    snapshot_id = create_rds_snapshot()
    export_snapshot_to_s3(snapshot_id)

if __name__ == "__main__":
    main()
