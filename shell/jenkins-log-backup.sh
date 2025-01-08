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
# 2nd "for-loop" inside 1st "for-loop" for all builds number of jobs

