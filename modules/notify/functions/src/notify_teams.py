# -*- coding: utf-8 -*-
"""
    Notify Teams
    ------------

    Receives event payloads that are parsed and sent to Teams

"""

import json
import os
from enum import Enum
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from aws_lambda_powertools import Logger, Metrics
from aws_lambda_powertools.utilities.typing import LambdaContext

logger = Logger()
powertools_namespace = os.environ["POWERTOOLS_SERVICE_NAME"]
metrics = Metrics(namespace=powertools_namespace)
from aws_lambda_powertools.metrics import MetricUnit

from msg_parser import decrypt_url, parse_sns
from msg_render_teams import TeamsRender
from render import Render

LOG_EVENTS = True if os.environ.get("LOG_EVENTS", "False") == "True" else False


def send_teams_notification(payload: Dict[str, Any]) -> str:
    """
    Send notification payload to teams

    :params payload: formatted teams message payload
    :returns: { code: integer, info: string}
    """
    teams_url = os.environ["TEAMS_WEBHOOK_URL"]
    if not teams_url.startswith("http"):
        teams_url = decrypt_url(teams_url)

    logger.debug(
        "Teams endpoint payload",
        endpoint_url=teams_url,
        payload=payload,
    )

    req = Request(
        teams_url,
        json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        response = urlopen(req)
        response.read()
        logger.debug(
            "Successfully posted to slack with response", code=response.getcode()
        )
        return json.dumps(
            {"code": response.getcode(), "info": response.info().as_string()}
        )
    except HTTPError as e:
        logger.error(
            "Failed to post to teams",
            code=e.code,
            reason=e.reason,
            endpoint_url=teams_url,
            payload=payload,
        )
        return json.dumps({"code": e.getcode(), "info": e.info().as_string()})


# note - this lambda is invoked as event from SNS - no sensible correlation id to assume
@metrics.log_metrics(capture_cold_start_metric=True)
def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Lambda function to parse notification events and forward to teams

    :param event: lambda expected event object
    :param context: lambda expected context object
    :returns: none
    """
    metrics.add_metric(name="NotificationsInvocations", unit=MetricUnit.Count, value=1)

    logger.debug("The event", event=event)

    renderer: Render = TeamsRender()

    # Teams will return HTTP(202) on success - or will it?
    parse_sns_status: bool = parse_sns(
        event["Records"],
        send_teams_notification,
        renderer,
        202,
    )
    if not parse_sns_status:
        logger.error(
            "Failed to process event",
            event=event,
            context=context,
        )
        raise Exception("Failed to process all SNS records")

    return {}
