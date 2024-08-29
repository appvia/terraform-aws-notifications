# -*- coding: utf-8 -*-
"""
    Notify Teams
    ------------

    Receives event payloads that are parsed and sent to Teams

"""

import json
import logging
import os
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from enum import Enum
from typing import Any, Dict, Optional, Union, cast
from urllib.error import HTTPError

LOG_EVENTS = os.environ['LOG_EVENTS']   # Log only if "True"

import msg_parser as parser
import msg_render_teams as render

def send_teams_notification(payload: Dict[str, Any]) -> str:
    """
    Send notification payload to teams

    :params payload: formatted teams message payload
    :returns: response details from sending notification
    """
    teams_url = os.environ["TEAMS_WEBHOOK_URL"]
    if not teams_url.startswith("http"):
        teams_url = parser.decrypt_url(teams_url)
    
    if LOG_EVENTS == "True":
      logging.info(f"Event logging enabled (teams payload) to {teams_url}: `{payload}`")

    req = Request(teams_url, json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        response = urlopen(req)
        response.read()
        logging.info("Message posted")
        return json.dumps({"code": response.getcode(), "info": response.info().as_string()})
    except HTTPError as e:
        logging.error("Request failed: %d %s", e.code, e.reason)
        return json.dumps({"code": e.getcode(), "info": e.info().as_string()})
    except URLError as e:
        logging.error("Server connection failed: %s", e.reason)
        return json.dumps({"code": 500, "info": "Unexpected error"})

def lambda_handler(event: Dict[str, Any], context: Dict[str, Any]) -> str:
    """
    Lambda function to parse notification events and forward to teams

    :param event: lambda expected event object
    :param context: lambda expected context object
    :returns: none
    """

    if LOG_EVENTS == "True":
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
          subject=subject,
        )
        payload = render.render_payload(
          parsedMessage=parserResults.parsedMsg,
          originalMessage=message,
          subject=subject,
        )
        response = send_teams_notification(payload=payload)

    if json.loads(response)["code"] != 202:
        response_info = json.loads(response)["info"]
        logging.error(
            f"Error: received status `{response_info}` using event `{event}` and context `{context}`"
        )

    return response
