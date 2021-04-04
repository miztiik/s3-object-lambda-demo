#!/bin/bash
set -ex

AWS_PROFILE="elf"
AWS_REGION="us-east-2"
DELETE_THIS_LOG_GROUP="polyglot_svc_fn"


LOG_GROUPS=$(
aws logs describe-log-groups --output table --profile $AWS_PROFILE --region $AWS_REGION |
        awk '{print $6}' |
        grep -v ^$ |
        grep -v DescribeLogGroups |
        grep $DELETE_THIS_LOG_GROUP
)

for name in ${LOG_GROUPS}; do
    printf "Delete group ${name}... "
    aws logs delete-log-group --log-group-name ${name} && echo OK || echo Fail
done

aws logs create-log-group --log-group-name /aws/lambda/${DELETE_THIS_LOG_GROUP} --profile $AWS_PROFILE --region $AWS_REGION && echo OK || echo Fail