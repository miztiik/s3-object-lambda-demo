#!/usr/bin/env python3

from stacks.back_end.serverless_s3_producer_stack.serverless_s3_producer_stack import ServerlessS3ProducerStack
from stacks.back_end.s3_object_lambda_stack.s3_object_lambda_stack import S3ObjectLambdaStack
from stacks.back_end.s3_stack.s3_stack import S3Stack
from stacks.back_end.s3_stack.s3_access_points_stack import S3AccessPointsStack
from aws_cdk import core as cdk


app = cdk.App()

# S3 Bucket to hold our store events
store_events_bkt_stack = S3Stack(
    app,
    # f"{app.node.try_get_context('project')}-store-events-bkt-stack",
    f"store-events-bkt-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: S3 Bucket to hold our store events"
)

# Produce store events using AWS Lambda and store them in S3
serverless_s3_producer_stack = ServerlessS3ProducerStack(
    app,
    f"store-events-producer-stack",
    stack_log_level="INFO",
    sales_event_bkt=store_events_bkt_stack.data_bkt,
    sales_lambda_ap_name="lambda-consumer",
    description="Miztiik Automation: Produce store events using AWS Lambda and store them in S3"
)

# Process S3 requests in flight using lambda
s3_obj_lambda_stack = S3ObjectLambdaStack(
    app,
    f"s3-object-lambda-stack",
    stack_log_level="INFO",
    sales_lambda_ap_name="lambda-consumer",
    description="Miztiik Automation: Process S3 requests in flight using lambda"
)

# Store events bucket access points
store_events_bkt_access_points_stack = S3AccessPointsStack(
    app,
    # f"{app.node.try_get_context('project')}-sales-events-bkt-stack",
    f"store-events-bkt-access-points-stack",
    stack_log_level="INFO",
    sales_lambda_ap_name="lambda-consumer",
    sales_lambda_consumer_role=serverless_s3_producer_stack.data_producer_fn_role,
    s3_object_lambda_fn_role=s3_obj_lambda_stack.s3_object_lambda_fn_role,
    sales_event_bkt=store_events_bkt_stack.data_bkt,
    description="Miztiik Automation: Create 'sales_event' & 'inventory_event` bucket access points"
)


# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)

app.synth()
