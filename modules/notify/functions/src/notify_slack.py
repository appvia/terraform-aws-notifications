# -*- coding: utf-8 -*-
"""
    Notify Slack
    ------------

    Receives event payloads that are parsed and sent to Slack

"""

import json
import os
import urllib.parse
import urllib.request
from typing import Any, Dict
from urllib.error import HTTPError

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
powertools_namespace = os.environ["POWERTOOLS_SERVICE_NAME"]
metrics = Metrics(namespace=powertools_namespace)
from aws_lambda_powertools.metrics import MetricUnit

from msg_parser import decrypt_url, parse_sns
from msg_render_slack import SlackRender
from render import Render


def send_slack_notification(payload: Dict[str, Any]) -> str:
    """
    Send notification payload to Slack

    :params payload: formatted Slack message payload
    :returns: { code: integer, info: string}
    """

    slack_url = os.environ["SLACK_WEBHOOK_URL"]
    if not slack_url.startswith("http"):
        slack_url = decrypt_url(slack_url)

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)

    logger.debug(
        "Slack endpoint payload",
        endpoint_url=slack_url,
        payload=payload,
    )

    try:
        result = urllib.request.urlopen(req, data)
        logger.debug(
            "Successfully posted to slack with response", code=result.getcode()
        )
        return json.dumps({"code": result.getcode(), "info": result.info().as_string()})

    except HTTPError as e:
        logger.error(
            "Failed to post to slack",
            code=e.code,
            reason=e.reason,
            endpoint_url=slack_url,
            payload=payload,
        )
        return json.dumps({"code": e.getcode(), "info": e.info().as_string()})


# note - this lambda is invoked as event from SNS - no sensible correlation id to assume
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: LambdaContext) -> str:
    """
    Lambda function to parse notification events and forward to Slack

    :param event: lambda expected event object
    :param context: lambda expected context object
    :returns: none
    """
    metrics.add_metric(name="Invocations", unit=MetricUnit.Count, value=1)

    logger.debug("The event", event=event)

    renderer: Render = SlackRender()

    # Slack will return HTTP(200) on success
    parse_sns_status: bool = parse_sns(
        snsRecords=event["Records"],
        vendor_send_to_function=send_slack_notification,
        renderer=renderer,
        rendererSuccessCode=200,
    )
    if not parse_sns_status:
        logger.error(
            "Failed to process event",
            event=event,
            context=context,
        )
        raise Exception("Failed to process all SNS records")

    return {}
