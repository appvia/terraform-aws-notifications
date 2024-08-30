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

from msg_parser import parse_sns, decrypt_url
from msg_render_slack import SlackRender
from render import Render

LOG_EVENTS = True if os.environ.get("LOG_EVENTS", "False") == "True" else False

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

  if LOG_EVENTS == True:
    logging.info(f"XTRA: Event logging enabled (slack payload): `{json.dumps(payload)}`")

  try:
    result = urllib.request.urlopen(req, data)
    logging.info(f"Message posted: code(${result.getcode()})")
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

  if LOG_EVENTS == True:
    logging.info(f"XTRA: Event logging enabled (Event): `{json.dumps(event)}`")

  renderer: Render = SlackRender(
    logExtra=LOG_EVENTS
  )

  # Slack will return HTTP(200) on success
  parse_sns_status: bool = parse_sns(
    snsRecords=event["Records"],
    vendor_send_to_function=send_slack_notification,
    renderer=renderer,
    rendererSuccessCode=200,
    logExtra=LOG_EVENTS
  )
  if not parse_sns_status:
    logging.error(
      f"Error: processing event `{event}` and context `{context}`"
    )
    raise Exception('Failed to process all SNS records')
  
  return {}