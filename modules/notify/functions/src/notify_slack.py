# -*- coding: utf-8 -*-
"""
    Notify Slack
    ------------

    Receives event payloads that are parsed and sent to Slack

"""

import json
import logging
import os
import urllib.parse
import urllib.request
from typing import Any, Dict
from urllib.error import HTTPError

import msg_parser as parser
import msg_render_slack as render

def send_slack_notification(payload: Dict[str, Any]) -> str:
    """
    Send notification payload to Slack

    :params payload: formatted Slack message payload
    :returns: response details from sending notification
    """

    slack_url = os.environ["SLACK_WEBHOOK_URL"]
    if not slack_url.startswith("http"):
        slack_url = parser.decrypt_url(slack_url)

    data = urllib.parse.urlencode({"payload": json.dumps(payload)}).encode("utf-8")
    req = urllib.request.Request(slack_url)

    if os.environ.get("LOG_EVENTS", "False") == "True":
        logging.info(f"Event logging enabled (slack payload): `{json.dumps(payload)}`")

    try:
        result = urllib.request.urlopen(req, data)
        return json.dumps({"code": result.getcode(), "info": result.info().as_string()})

    except HTTPError as e:
        logging.error(f"{e}: result")
        return json.dumps({"code": e.getcode(), "info": e.info().as_string()})


def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Lambda function to parse notification events and forward to Slack

    :param event: lambda expected event object
    :param context: lambda expected context object
    :returns: none
    """

    if os.environ.get("LOG_EVENTS", "False") == "True":
        logging.info(f"Event logging enabled (Event): `{json.dumps(event)}`")

    for record in event["Records"]:
        sns = record["Sns"]
        subject = sns["Subject"]
        message = sns["Message"]
        region = sns["TopicArn"].split(":")[3]
        messageAttributes = sns["MessageAttributes"]

        parserResults = parser.get_message_payload(
            message=message, 
            region=region,
            messageAttributes=messageAttributes,
            subject=subject
        )
        payload = render.render_payload(
            parsedMessage=parserResults.parsedMsg,
            originalMessage=message,
            subject=subject,
        )
        response = send_slack_notification(payload=payload)

    if json.loads(response)["code"] != 200:
        response_info = json.loads(response)["info"]
        logging.error(
            f"Error: received status `{response_info}` using event `{event}` and context `{context}`"
        )


#    return response
