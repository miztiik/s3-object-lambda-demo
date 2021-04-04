#!/usr/bin/env python3

import boto3

BKT_TO_BE_DELETED = "store-events-bkt-stack-databucketd8691f4e-1gn3rpcx8b638"

s3 = boto3.resource("s3")
bucket = s3.Bucket(BKT_TO_BE_DELETED)
bucket.object_versions.all().delete()
bucket.delete()
