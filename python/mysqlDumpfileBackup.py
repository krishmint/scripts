import subprocess
import boto3
import datetime
import os

# AWS S3 configuration
S3_BUCKET_NAME = 'your-s3-bucket-name'
S3_REGION_NAME = 'your-s3-region'  # e.g., 'us-east-1'

# MySQL configuration
RDS_ENDPOINT = 'your-rds-endpoint'
USERNAME = 'your-username'
PASSWORD = 'your-password'

# Generate a timestamp for the dump file
timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
dump_filename = f"mysql_backup_{timestamp}.sql"

# Command to create a MySQL dump of all databases with DROP TABLE statements
dump_command = [
    'mysqldump',
    '-h', RDS_ENDPOINT,
    '-u', USERNAME,
    f'-p{PASSWORD}',
    '--add-drop-table',
    '--all-databases'
]

# Execute the dump command and write the output to a file
with open(dump_filename, 'w') as dump_file:
    subprocess.run(dump_command, stdout=dump_file)
# open(dump_filename, 'w'):This function opens a file for writing.
# subprocess.run() function is used to execute the specified command.
# stdout=dump_file argument ensures that the output of the mysqldump command is written directly to the file dump_filename.

# Upload the dump file to S3
s3_client = boto3.client('s3', region_name=S3_REGION_NAME)
s3_client.upload_file(dump_filename, S3_BUCKET_NAME, dump_filename)
# Filename: The path to the file to be uploaded.(1st dump filename)
# Bucket: The name of the S3 bucket where the file will be stored.
# Key: The name of the object in the S3 bucket. (2nd dump file)

# Remove the local dump file after upload
os.remove(dump_filename)
