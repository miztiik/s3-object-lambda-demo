# -*- coding: utf-8 -*-

import requests
import json
import logging
import os
import time
import random
import boto3


class GlobalArgs:
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def set_logging(lv=GlobalArgs.LOG_LEVEL):
    """ Helper to enable logging """
    logging.basicConfig(level=lv)
    logger = logging.getLogger()
    logger.setLevel(lv)
    return logger


LOG = set_logging()
client = boto3.client('s3')


def process_msgs(msg_batch):
    try:
        m_process_stat = {}
        err = f'{{"missing_store_id":{True}}}'
        for m in msg_batch:
            # As SNS send messages to as string, we have to monkey it into a dict
            LOG.info(f'{{"msg":{json.loads(m.get("body")).get("Message")}}}')
        m_process_stat = {
            "s_msgs": len(msg_batch),
        }
        LOG.debug(f'{{"m_process_stat":"{json.dumps(m_process_stat)}"}}')
    except Exception as e:
        LOG.exception(f"ERROR:{str(e)}")
        raise e
    else:
        return m_process_stat


def lambda_handler(event, context):
    resp = {"status": False}
    LOG.info(boto3.__version__)
    LOG.info(json.dumps(event))

    object_get_context = event["getObjectContext"]
    request_route = object_get_context["outputRoute"]
    request_token = object_get_context["outputToken"]
    s3_url = object_get_context["inputS3Url"]

    # Get object from S3
    response = requests.get(s3_url)
    original_object = json.loads(response.content.decode("utf-8"))
    LOG.info(json.dumps(original_object))

    # Transform object
    # transformed_object = original_object.upper()
    original_object.pop("discount", None)
    original_object.pop("price", None)
    transformed_object = json.dumps(original_object)


    # Write object back to S3 Object Lambda
    _r = client.write_get_object_response(
        Body=transformed_object,
        RequestRoute=request_route,
        RequestToken=request_token
    )
    LOG.info(f'{{"resp":{json.dumps(_r)}}}')

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": resp
        })
    }
