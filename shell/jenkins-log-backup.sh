#!/bin/basi
set -x
#################################################

# DESCRIPTION - shell script to backup jenkins build log file(basically build num folder) from folder path "/var/lib/jenkins/jobs/job-Project-name/builds/build-num/ " and the store it in S3 and 
# create a S3 lifecycle policy to change storage tier from standard to glacier archive after 15 days   

#################################################

JENKINS_LOGS="/var/lib/jenkin/jobs" ## folder where jenkins logs files are stored
S3_BUCKET="jenkins_logs" ## s3 bucket name
DATE=$(date +%d-%m-%Y)


## check if aws cli is installed by running command "aws" and checking its output
if ! command -v aws &> /dev/null;
then
        echo"aws cli not installed-- install aws cli then proceed"
        exit 1
fi

### we will need multiple "for-loop"
# 1st "for-loop" over all jobs (diff projects)
# 2nd "for-loop" inside 1st "for-loop" for all builds number of todays date 
# "if-condition" inside 2nd loop to check the buildnumber folder date  and upload only if it is of current date


for job_dir in "$JENKINS_JOBS"*/; do
   JOB_NAME=$(base "$job_dir")


      for build_dir in "$job_dir/builds/"*/; do
         BUILD_NUM=$(basename "$build_dir")
         LOG_FILE="$build_dir/log"

         # Check if log file exists and was created today
         if [ -f "$LOG_FILE" ] && [ "$(date -r "$LOG_FILE" +%Y-%m-%d)" == "$DATE" ]; then
         # [ -f "$LOG_FILE" ] = This checks if the file specified by the variable LOG_FILE exists and is a regular file.
         
             aws s3 cp "$LOG_FILE" "$S3_BUCKET/$JOB_NAME-$BUILD_NUM.log" --only-show-errors  # Upload log file to S3 with the build number as the filename

             if [ $? -eq 0 ]; then ## $? :This is a special variable in Bash that holds the exit status of the last executed command
                                   # -eq: This is a comparison operator in Bash that means "equal to.It's used to compare integers.
             echo "Uploaded: $JOB_NAME/$BUILD_NUM to $S3_BUCKET/$JOB_NAME-$BUILD_NUM.log"
             else
             echo "Failed to upload: $JOB_NAME/$BUILD_NUM"
             fi
         fi

